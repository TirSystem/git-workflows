"""Offline tests for tools/release.py and .gitea/scoped_workflows/release.yml (ADR-0017)."""

import pytest
import yaml

from workflow_source import REPO_ROOT, load_script

release = load_script(REPO_ROOT / "tools" / "release.py", "release")
WORKFLOW = REPO_ROOT / ".gitea" / "scoped_workflows" / "release.yml"
FRAMEWORK_CHANGELOG = REPO_ROOT / "tests" / "fixtures" / "framework-changelog.md"

SHA = "a" * 40
CONTEXT = "Validate / validate (push)"

CHANGELOG = """# Changelog

## [Unreleased]

### Added

- Something later.

## [1.1.0] - 2026-11-01

### Added

- A workflow.

## [1.0.0] - 2026-10-20

### Breaking

- The first stable interface.

### Added

- First release.

## [0.9.0] - 2026-10-01

### Added

- A preview.
"""


class FakeGitea:
    """Answers the calls of the release script and records every call."""

    def __init__(self, tip=SHA, status="success", tags=(), context=CONTEXT, default_branch="main"):
        self.tip = tip
        self.status = status
        self.tags = list(tags)
        self.context = context
        self.default_branch = default_branch
        self.calls = []
        self.writes = []

    def __call__(self, url, method="GET", headers=None, body=None):
        path = url.split("?")[0]
        relative = path.rsplit("/repos/o/r", 1)[-1]
        self.calls.append((method, relative))
        if method != "GET":
            self.writes.append((method, relative, body))
            return None
        if relative == "":
            return {"default_branch": self.default_branch}
        if path.endswith(f"/branches/{self.default_branch}"):
            return {"commit": {"id": self.tip}}
        if path.endswith(f"/commits/{SHA}/status"):
            if self.status is None:
                return {"statuses": []}
            return {"statuses": [{"context": self.context, "status": self.status}]}
        if path.endswith("/tags"):
            return [{"name": name} for name in self.tags] if "page=1" in url else []
        raise AssertionError(f"unexpected request {method} {url}")


@pytest.fixture
def env(tmp_path, monkeypatch):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(CHANGELOG, encoding="utf-8")
    values = {
        "GITEA_API_URL": "https://git.example/api/v1",
        "SOURCE_REPOSITORY": "o/r",
        "RELEASE_CREDENTIALS": "t" * 40,
        "RELEASE_VERSION": "1.1.0",
        "RELEASE_SHA": SHA,
        "RELEASE_DRY_RUN": "false",
        "CHANGELOG_FILE": str(changelog),
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("RELEASE_BRANCH", raising=False)
    monkeypatch.delenv("VALIDATION_CONTEXT", raising=False)
    return monkeypatch


def run(gitea):
    return release.main(request=gitea)


def test_green_commit_with_entry_creates_release_and_major_tag(env):
    gitea = FakeGitea(tags=["v1.0.0", "v1"])
    assert run(gitea) == 0
    methods = [(m, p) for m, p, _ in gitea.writes]
    assert methods == [("POST", "/releases"), ("DELETE", "/tags/v1"), ("POST", "/tags")]
    release_body = gitea.writes[0][2]
    assert release_body["tag_name"] == "v1.1.0"
    assert release_body["target_commitish"] == SHA
    assert "### Added" in release_body["body"] and "A workflow." in release_body["body"]
    assert gitea.writes[2][2]["tag_name"] == "v1" and gitea.writes[2][2]["target"] == SHA


def test_first_release_creates_the_major_tag_without_deleting(env):
    env.setenv("RELEASE_VERSION", "1.0.0")
    gitea = FakeGitea(tags=["v0.9.0"])
    assert run(gitea) == 0
    assert [(m, p) for m, p, _ in gitea.writes] == [("POST", "/releases"), ("POST", "/tags")]
    assert gitea.writes[1][2]["tag_name"] == "v1"


def test_failed_validation_run_creates_no_tag(env):
    gitea = FakeGitea(status="failure")
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert error.value.category == "validation"
    assert "failure, not success" in str(error.value)
    assert gitea.writes == []


def test_missing_validation_run_creates_no_tag(env):
    gitea = FakeGitea(status=None)
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert error.value.category == "validation"
    assert "No validation run" in str(error.value)
    assert gitea.writes == []


def test_commit_that_is_not_the_tip_is_refused(env):
    gitea = FakeGitea(tip="b" * 40)
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert error.value.category == "validation"
    assert "not the tip" in str(error.value)
    assert gitea.writes == []


def test_version_without_changelog_entry_is_refused(env):
    env.setenv("RELEASE_VERSION", "1.2.0")
    gitea = FakeGitea()
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert error.value.category == "validation"
    assert gitea.writes == []


def test_existing_tag_is_never_moved(env):
    gitea = FakeGitea(tags=["v1.1.0", "v1.0.0", "v1"])
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert error.value.category == "validation"
    assert "already exists" in str(error.value)
    assert gitea.writes == []


def test_older_patch_does_not_move_the_major_tag(env):
    env.setenv("RELEASE_VERSION", "1.0.0")
    gitea = FakeGitea(tags=["v1.1.0", "v1"])
    assert run(gitea) == 0
    assert [(m, p) for m, p, _ in gitea.writes] == [("POST", "/releases")]


def test_dry_run_is_the_default_and_writes_nothing(env, capsys):
    env.delenv("RELEASE_DRY_RUN")
    gitea = FakeGitea(tags=["v1.0.0", "v1"])
    assert run(gitea) == 0
    assert gitea.writes == []
    assert {method for method, _ in gitea.calls} == {"GET"}
    assert "Dry run" in capsys.readouterr().out


def test_dry_run_of_a_zero_version_says_there_is_no_major_tag(env, capsys):
    env.setenv("RELEASE_VERSION", "0.9.0")
    env.setenv("RELEASE_DRY_RUN", "true")
    gitea = FakeGitea()
    assert run(gitea) == 0
    assert gitea.writes == []
    assert "no major tag for a 0.x release" in capsys.readouterr().out


@pytest.mark.parametrize("version", ["v1.0.0", "1.0", "1.0.0-rc1", ""])
def test_malformed_version_is_a_configuration_error(env, version):
    env.setenv("RELEASE_VERSION", version)
    with pytest.raises(release.WorkflowError) as error:
        run(FakeGitea())
    assert error.value.category == "configuration"


@pytest.mark.parametrize("token", ["  ", None])
def test_missing_token_names_the_secret_and_has_no_fallback(env, token):
    if token is None:
        env.delenv("RELEASE_CREDENTIALS")
    else:
        env.setenv("RELEASE_CREDENTIALS", token)
    env.setenv("GITHUB_TOKEN", "x" * 40)
    env.setenv("GITEA_TOKEN", "x" * 40)
    gitea = FakeGitea()
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert error.value.category == "configuration"
    assert error.value.detail == "TOKEN_FOR_GITEA_RELEASE is missing or empty."
    assert gitea.calls == []


def test_default_branch_comes_from_the_api(env):
    gitea = FakeGitea(default_branch="trunk", tags=["v1.0.0", "v1"])
    assert run(gitea) == 0
    assert ("GET", "/branches/trunk") in gitea.calls
    assert gitea.writes[0][:2] == ("POST", "/releases")


def test_release_branch_overrides_the_default_branch(env):
    env.setenv("RELEASE_BRANCH", "other")
    gitea = FakeGitea(default_branch="other")
    assert run(gitea) == 0
    assert ("GET", "") not in gitea.calls


def test_repository_without_a_default_branch_is_an_api_error(env):
    gitea = FakeGitea(default_branch="")
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert error.value.category == "api"


def test_default_context_is_the_scoped_validation_status(env):
    assert release.DEFAULT_CONTEXT == "Validate / validate (push)"
    gitea = FakeGitea(context="Validate workflows / validate (push)")
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert "No validation run" in str(error.value)


def test_validation_context_can_be_overridden(env):
    env.setenv("VALIDATION_CONTEXT", "Other / check (push)")
    gitea = FakeGitea(context="Other / check (push)")
    assert run(gitea) == 0


def test_both_changelog_formats_give_the_notes_through_the_script(env):
    gitea = FakeGitea()
    assert run(gitea) == 0
    assert "A workflow." in gitea.writes[0][2]["body"]

    env.setenv("RELEASE_VERSION", "0.18.0")
    env.setenv("CHANGELOG_FILE", str(FRAMEWORK_CHANGELOG))
    gitea = FakeGitea()
    assert run(gitea) == 0
    page = gitea.writes[0][2]
    assert page["tag_name"] == "v0.18.0"
    assert page["body"].startswith("## 0.18.0 (2026-10-28)")
    assert "Wiki page `Artifacts`" in page["body"] and "broken link" not in page["body"]


def test_framework_changelog_without_an_entry_is_refused(env):
    env.setenv("RELEASE_VERSION", "0.19.0")
    env.setenv("CHANGELOG_FILE", str(FRAMEWORK_CHANGELOG))
    gitea = FakeGitea()
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert error.value.category == "validation"
    assert gitea.writes == []


def test_zero_version_makes_no_major_tag(env, capsys):
    env.setenv("RELEASE_VERSION", "0.9.0")
    gitea = FakeGitea(tags=["v0.8.0", "v0"])
    assert run(gitea) == 0
    assert [(m, p) for m, p, _ in gitea.writes] == [("POST", "/releases")]
    assert "no major tag for a 0.x release" in capsys.readouterr().out


def test_plan_tags_major_rule():
    assert release.plan_tags([], (0, 9, 0)) == ("v0.9.0", None, False)
    assert release.plan_tags([], (1, 0, 0)) == ("v1.0.0", "v1", True)
    assert release.plan_tags(["v1.1.0", "v1"], (1, 0, 1)) == ("v1.0.1", "v1", False)
    assert release.plan_tags(["v1.1.0"], (2, 0, 0)) == ("v2.0.0", "v2", True)
    assert release.plan_tags(["v1.0.0", "v2.0.0"], (1, 0, 1)) == ("v1.0.1", "v1", True)
    assert release.plan_tags(["v1.1.0", "v2.0.0"], (1, 0, 1)) == ("v1.0.1", "v1", False)


def test_calls_made_are_listed_in_api_calls(env):
    gitea = FakeGitea(tags=["v1.0.0", "v1"])
    assert run(gitea) == 0
    shapes = {
        "": "",
        "/branches/main": "/branches/{branch}",
        f"/commits/{SHA}/status": "/commits/{sha}/status",
        "/tags/v1": "/tags/{tag}",
    }
    made = {(method, shapes.get(path, path)) for method, path in gitea.calls}
    assert made == set(release.API_CALLS)


def load_workflow():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_workflow_is_scoped_and_started_by_hand():
    data = load_workflow()
    assert data["name"] == "Release"
    triggers = data.get("on", data.get(True))
    assert list(triggers) == ["workflow_dispatch"]
    inputs = triggers["workflow_dispatch"]["inputs"]
    assert inputs["version"]["required"] is True
    assert inputs["dry_run"]["default"] == "true"
    assert data["concurrency"] == {"group": "release", "cancel-in-progress": False}


def test_old_per_repository_workflow_is_gone():
    assert not (REPO_ROOT / ".gitea" / "workflows" / "release.yml").exists()


def test_workflow_job_has_read_permission_and_a_fixed_name():
    job = load_workflow()["jobs"]["release"]
    assert job["name"] == "release"
    assert job["permissions"] == {"contents": "read"}
    assert job["runs-on"] == "ubuntu-latest"
    assert job["timeout-minutes"] == 15


def test_workflow_fetches_the_script_at_v2_and_runs_it():
    steps = load_workflow()["jobs"]["release"]["steps"]
    fetch = [step for step in steps if "with" in step]
    assert [(s["with"]["repository"], s["with"]["ref"], s["with"]["path"]) for s in fetch] == [
        ("TirSystem/git-workflows", "v2", "shared-scripts")
    ]
    assert steps[-1]["run"] == "python3 shared-scripts/tools/release.py"


def test_token_is_only_in_the_env_of_the_release_step_and_never_in_a_command():
    steps = load_workflow()["jobs"]["release"]["steps"]
    holders = [step for step in steps if "secrets." in str(step)]
    assert holders == [steps[-1]]
    assert holders[0]["env"]["RELEASE_CREDENTIALS"] == "${{ secrets.TOKEN_FOR_GITEA_RELEASE }}"
    assert all("secrets." not in step.get("run", "") for step in steps)
    assert all("RELEASE_CREDENTIALS" not in step.get("run", "") for step in steps)


def test_workflow_has_no_fallback_token():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "github.token" not in text and "gitea.token" not in text
    assert "||" not in text
    assert text.count("secrets.") == 1


def test_workflow_passes_the_settings_the_script_reads():
    env = load_workflow()["jobs"]["release"]["steps"][-1]["env"]
    assert env == {
        "GITEA_API_URL": "${{ gitea.api_url }}",
        "SOURCE_REPOSITORY": "${{ gitea.repository }}",
        "RELEASE_CREDENTIALS": "${{ secrets.TOKEN_FOR_GITEA_RELEASE }}",
        "RELEASE_VERSION": "${{ inputs.version }}",
        "RELEASE_DRY_RUN": "${{ inputs.dry_run }}",
        "RELEASE_SHA": "${{ gitea.sha }}",
    }
