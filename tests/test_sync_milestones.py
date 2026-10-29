"""Offline tests for tools/sync_milestones.py: a fake subprocess, tmp_path projects, no network."""

import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any  # the loaded script module and YAML trees have no fixed shape

import pytest
import yaml
from workflow_source import REPO_ROOT, load_script

SCRIPT = REPO_ROOT / "tools" / "sync_milestones.py"
WORKFLOW = REPO_ROOT / ".gitea" / "scoped_workflows" / "sync-milestones.yml"
REPO_TOKEN = "repo-token-value"
ISSUES_TOKEN = "issues-token-value"
SUBMODULE_SCRIPT = "framework/scripts/ci-publish-milestones.sh"


@pytest.fixture()
def sync(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Any:  # the loaded script module
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "output.txt"))
    monkeypatch.setenv("TOKEN_FOR_GITEA_REPO", REPO_TOKEN)
    monkeypatch.setenv("TOKEN_FOR_GITEA_ISSUES", ISSUES_TOKEN)
    monkeypatch.delenv("DRY_RUN", raising=False)
    return load_script(SCRIPT, "sync_milestones")


class FakeRuns:
    """Records subprocess.run calls as (command, environment) and answers them."""

    def __init__(self, returncodes: dict[str, int] | None = None, describe: str = "v0.17.0") -> None:
        self.calls: list[tuple[list[str], dict[str, str]]] = []
        self.returncodes = returncodes or {}
        self.describe = describe

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        self.calls.append((command, kwargs.get("env") or {}))
        code = next((value for key, value in self.returncodes.items() if key in command or key == command[0]), 0)
        output = self.describe + "\n" if "describe" in command else ""
        return subprocess.CompletedProcess(command, code, stdout=output)

    def commands(self) -> list[list[str]]:
        return [command for command, _ in self.calls]


def patch_run(monkeypatch: pytest.MonkeyPatch, sync: Any, fake: FakeRuns) -> FakeRuns:
    monkeypatch.setattr(sync.subprocess, "run", fake)
    return fake


def make_folder(name: str) -> None:
    Path(name).mkdir(parents=True)


def output_text() -> str:
    return Path("output.txt").read_text(encoding="utf-8")


def assert_no_token(fake: FakeRuns, captured: str) -> None:
    for command in fake.commands():
        assert REPO_TOKEN not in " ".join(command)
        assert ISSUES_TOKEN not in " ".join(command)
    assert REPO_TOKEN not in captured
    assert ISSUES_TOKEN not in captured


# check ---------------------------------------------------------------------


def test_check_is_green_without_the_folder_and_needs_no_secrets(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("TOKEN_FOR_GITEA_REPO")
    monkeypatch.delenv("TOKEN_FOR_GITEA_ISSUES")
    fake = patch_run(monkeypatch, sync, FakeRuns())
    sync.check()
    assert "No docs/milestones folder in this repository; nothing to publish." in capsys.readouterr().out
    assert output_text() == "found=false\n"
    assert fake.calls == []


def test_check_finds_the_folder_and_accepts_both_secrets(sync: Any) -> None:
    make_folder("docs/milestones")
    sync.check()
    assert output_text() == "found=true\n"


def test_check_without_a_github_output_file_still_works(sync: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_OUTPUT")
    sync.check()


@pytest.mark.parametrize("name", ["TOKEN_FOR_GITEA_REPO", "TOKEN_FOR_GITEA_ISSUES"])
@pytest.mark.parametrize("empty", [True, False])
def test_check_fails_naming_the_missing_secret(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], name: str, empty: bool
) -> None:
    make_folder("docs/milestones")
    if empty:
        monkeypatch.setenv(name, "")
    else:
        monkeypatch.delenv(name)
    with pytest.raises(SystemExit) as raised:
        sync.check()
    assert raised.value.code == 1
    out = capsys.readouterr().out
    assert f"::error::[configuration] {name} is missing or empty." in out
    assert REPO_TOKEN not in out
    assert ISSUES_TOKEN not in out


# framework -----------------------------------------------------------------


def test_framework_uses_the_project_submodule_when_it_has_the_script(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    Path(SUBMODULE_SCRIPT).parent.mkdir(parents=True)
    Path(SUBMODULE_SCRIPT).write_text("", encoding="utf-8")
    fake = patch_run(monkeypatch, sync, FakeRuns(describe="v0.17.0-3-gabc"))
    sync.framework()
    assert fake.commands() == [
        ["git", "submodule", "update", "--init", "--recursive", "--depth=1"],
        ["git", "-C", "framework", "describe", "--tags", "--always"],
    ]
    out = capsys.readouterr().out
    assert "Framework source: project submodule at v0.17.0-3-gabc" in out
    assert_no_token(fake, out)
    environment = fake.calls[0][1]
    assert environment["GIT_CONFIG_COUNT"] == "2"
    assert environment["GIT_CONFIG_KEY_0"] == "url.https://git.tirsystem.com/.insteadOf"
    assert environment["GIT_CONFIG_VALUE_0"] == "ssh://git@git.tirsystem.com:10022/"
    assert environment["GIT_CONFIG_KEY_1"] == "http.extraheader"
    assert environment["GIT_CONFIG_VALUE_1"] == f"Authorization: token {REPO_TOKEN}"


def test_framework_clones_the_pinned_release_without_a_submodule(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake = patch_run(monkeypatch, sync, FakeRuns())
    sync.framework()
    assert sync.FRAMEWORK_TAG == "v0.18.0"
    assert fake.commands() == [
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            "v0.18.0",
            "https://git.tirsystem.com/TirSystem/sqa-qc-framework.git",
            "framework",
        ]
    ]
    out = capsys.readouterr().out
    assert "Framework source: release v0.18.0" in out
    assert_no_token(fake, out)
    assert fake.calls[0][1]["GIT_CONFIG_VALUE_1"] == f"Authorization: token {REPO_TOKEN}"


def test_framework_fails_without_the_repository_token(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("TOKEN_FOR_GITEA_REPO")
    fake = patch_run(monkeypatch, sync, FakeRuns())
    with pytest.raises(SystemExit):
        sync.framework()
    assert "::error::[configuration] TOKEN_FOR_GITEA_REPO is missing or empty." in capsys.readouterr().out
    assert fake.calls == []


@pytest.mark.parametrize("with_submodule", [True, False])
def test_framework_fails_as_tool_when_git_fails(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], with_submodule: bool
) -> None:
    if with_submodule:
        Path(SUBMODULE_SCRIPT).parent.mkdir(parents=True)
        Path(SUBMODULE_SCRIPT).write_text("", encoding="utf-8")
    fake = patch_run(monkeypatch, sync, FakeRuns({"git": 128}))
    with pytest.raises(SystemExit) as raised:
        sync.framework()
    assert raised.value.code == 1
    out = capsys.readouterr().out
    assert "::error::[tool]" in out
    assert "exit code 128" in out
    assert_no_token(fake, out)


def test_framework_fails_as_tool_when_describe_fails(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    Path(SUBMODULE_SCRIPT).parent.mkdir(parents=True)
    Path(SUBMODULE_SCRIPT).write_text("", encoding="utf-8")
    patch_run(monkeypatch, sync, FakeRuns({"describe": 1}))
    with pytest.raises(SystemExit):
        sync.framework()
    assert "::error::[tool] git describe in framework failed" in capsys.readouterr().out


def test_framework_fails_as_tool_when_git_cannot_start(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def missing(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("git")

    monkeypatch.setattr(sync.subprocess, "run", missing)
    with pytest.raises(SystemExit):
        sync.framework()
    assert "::error::[tool] git cannot be started" in capsys.readouterr().out


def test_describe_fails_as_tool_when_git_cannot_start(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def missing(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("git")

    monkeypatch.setattr(sync.subprocess, "run", missing)
    with pytest.raises(SystemExit):
        sync.describe_framework({})
    assert "::error::[tool] git cannot be started" in capsys.readouterr().out


# publish -------------------------------------------------------------------


@pytest.mark.parametrize(("dry_run", "expected"), [("true", "true"), ("false", "false"), ("", "")])
def test_publish_passes_dry_run_through(
    sync: Any, monkeypatch: pytest.MonkeyPatch, dry_run: str, expected: str
) -> None:
    monkeypatch.setenv("DRY_RUN", dry_run)
    fake = patch_run(monkeypatch, sync, FakeRuns())
    sync.publish()
    assert [environment["DRY_RUN"] for _, environment in fake.calls] == [expected, expected]
    assert all(environment["TOKEN_FOR_GITEA_ISSUES"] == ISSUES_TOKEN for _, environment in fake.calls)


def test_publish_runs_ensure_tools_then_publish_and_never_closes_or_deletes(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake = patch_run(monkeypatch, sync, FakeRuns())
    sync.publish()
    assert fake.commands() == [
        ["bash", SUBMODULE_SCRIPT, "ensure-tools"],
        ["bash", SUBMODULE_SCRIPT, "publish"],
    ]
    joined = " ".join(" ".join(command) for command in fake.commands())
    for option in ("delete", "close", "--prune", "--force"):
        assert option not in joined
    assert_no_token(fake, capsys.readouterr().out)


def test_publish_leaves_the_accepted_only_rule_to_the_script() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "--apply" not in text
    assert "sync-project" not in text


def test_publish_fails_without_the_issues_token(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("TOKEN_FOR_GITEA_ISSUES")
    fake = patch_run(monkeypatch, sync, FakeRuns())
    with pytest.raises(SystemExit):
        sync.publish()
    assert "::error::[configuration] TOKEN_FOR_GITEA_ISSUES is missing or empty." in capsys.readouterr().out
    assert fake.calls == []


@pytest.mark.parametrize("step", ["ensure-tools", "publish"])
def test_publish_fails_as_tool_when_a_step_fails(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], step: str
) -> None:
    fake = patch_run(monkeypatch, sync, FakeRuns({step: 3}))
    with pytest.raises(SystemExit) as raised:
        sync.publish()
    assert raised.value.code == 1
    out = capsys.readouterr().out
    assert f"::error::[tool] {SUBMODULE_SCRIPT} {step} failed with exit code 3." in out
    assert len(fake.calls) == (1 if step == "ensure-tools" else 2)


def test_publish_fails_as_tool_when_bash_cannot_start(
    sync: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def missing(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("bash")

    monkeypatch.setattr(sync.subprocess, "run", missing)
    with pytest.raises(SystemExit):
        sync.publish()
    assert "::error::[tool] bash cannot be started" in capsys.readouterr().out


# main ----------------------------------------------------------------------


@pytest.mark.parametrize("command", ["check", "framework", "publish"])
def test_main_dispatches_to_the_command(sync: Any, monkeypatch: pytest.MonkeyPatch, command: str) -> None:
    called: list[str] = []
    for name in ("check", "framework", "publish"):
        monkeypatch.setattr(sync, name, lambda name=name: called.append(name))
    sync.main(["sync_milestones.py", command])
    assert called == [command]


@pytest.mark.parametrize("argv", [["sync_milestones.py"], ["sync_milestones.py", "other"], ["sync_milestones.py", "check", "x"]])
def test_main_fails_with_a_usage_error(sync: Any, capsys: pytest.CaptureFixture[str], argv: list[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        sync.main(argv)
    assert raised.value.code == 1
    assert "::error::[configuration] usage: sync_milestones.py check|framework|publish" in capsys.readouterr().out


def test_module_run_as_a_script_uses_main(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["sync_milestones.py"])
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    assert raised.value.code == 1
    assert "[configuration]" in capsys.readouterr().out


# The workflow file ---------------------------------------------------------


@pytest.fixture(scope="module")
def document() -> dict[Any, Any]:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def triggers_of(document: dict[Any, Any]) -> dict[str, Any]:
    return document.get("on", document.get(True))  # PyYAML reads the key "on" as True


def steps_of(document: dict[Any, Any]) -> list[dict[str, Any]]:
    return document["jobs"]["publish"]["steps"]


def test_workflow_has_the_documented_triggers(document: dict[Any, Any]) -> None:
    triggers = triggers_of(document)
    assert document["name"] == "Publish accepted milestones"
    assert set(triggers) == {"push", "workflow_dispatch"}
    assert triggers["push"]["branches"] == ["main"]
    assert triggers["push"]["paths"] == ["docs/milestones/**", "docs/sqa/reviews/**"]
    dry_run = triggers["workflow_dispatch"]["inputs"]["dry_run"]
    assert dry_run["type"] == "boolean"
    assert dry_run["default"] is True


def test_workflow_has_one_job_with_read_permission_and_a_queueing_group(document: dict[Any, Any]) -> None:
    assert list(document["jobs"]) == ["publish"]
    job = document["jobs"]["publish"]
    assert job["name"] == "publish"
    assert job["permissions"] == {"contents": "read"}
    assert job["runs-on"] == "ubuntu-latest"
    assert job["timeout-minutes"] == 15
    assert document["concurrency"] == {"group": "publish-accepted-milestones", "cancel-in-progress": False}


def test_workflow_fetches_the_shared_script_at_the_major_tag(document: dict[Any, Any]) -> None:
    steps = steps_of(document)
    assert steps[0]["with"] == {"token": "${{ secrets.TOKEN_FOR_GITEA_REPO }}"}
    fetch = [step["with"] for step in steps if step.get("with", {}).get("repository")]
    assert fetch == [{"repository": "TirSystem/git-workflows", "ref": "v2", "path": "shared-scripts"}]


def test_workflow_checks_the_folder_before_it_uses_the_secrets(document: dict[Any, Any]) -> None:
    steps = steps_of(document)
    check = next(step for step in steps if step.get("id") == "source")
    assert check["run"] == "python3 shared-scripts/tools/sync_milestones.py check"
    assert check["env"] == {
        "TOKEN_FOR_GITEA_REPO": "${{ secrets.TOKEN_FOR_GITEA_REPO }}",
        "TOKEN_FOR_GITEA_ISSUES": "${{ secrets.TOKEN_FOR_GITEA_ISSUES }}",
    }
    later = steps[steps.index(check) + 1 :]
    assert [step["run"] for step in later] == [
        "python3 shared-scripts/tools/sync_milestones.py framework",
        "python3 shared-scripts/tools/sync_milestones.py publish",
    ]
    assert {step["if"] for step in later} == {"steps.source.outputs.found == 'true'"}
    assert later[0]["env"] == {"TOKEN_FOR_GITEA_REPO": "${{ secrets.TOKEN_FOR_GITEA_REPO }}"}
    assert later[1]["env"] == {
        "TOKEN_FOR_GITEA_ISSUES": "${{ secrets.TOKEN_FOR_GITEA_ISSUES }}",
        "DRY_RUN": "${{ inputs.dry_run }}",
    }


def test_workflow_uses_no_default_token_and_secrets_only_in_env_or_checkout_token() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "github.token" not in text
    assert "GITHUB_TOKEN" not in text
    for line in text.splitlines():
        if "secrets." in line and not line.lstrip().startswith("#"):
            assert line.strip().startswith(("TOKEN_FOR_GITEA_", "token:"))


def test_workflow_has_no_findings_from_the_validate_tool() -> None:
    validate = load_script(REPO_ROOT / "tools" / "validate_repo.py", "validate_repo")
    text = WORKFLOW.read_text(encoding="utf-8")
    assert list(validate.check_workflow(".gitea/scoped_workflows/sync-milestones.yml", text, yaml)) == []


def test_the_old_copy_is_removed() -> None:
    assert not (REPO_ROOT / ".gitea" / "workflows" / "sync-milestones.yml").exists()
