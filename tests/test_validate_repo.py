"""Offline tests for tools/validate_repo.py: tmp_path repositories, fake shell tools, no network."""

import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any  # YAML nodes, the loaded script module and subprocess results have no fixed shape

import pytest
import yaml
from workflow_source import REPO_ROOT, load_script

SCRIPT = REPO_ROOT / "tools" / "validate_repo.py"
OWN_WORKFLOW = REPO_ROOT / ".gitea" / "scoped_workflows" / "validate.yml"
REAL_RUN = subprocess.run

GOOD = """name: Good
on: push
permissions:
  contents: read
jobs:
  build:
    name: build
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: One
        run: echo hi
"""


@pytest.fixture()
def validate(monkeypatch: pytest.MonkeyPatch) -> Any:  # the loaded script module
    monkeypatch.delenv("VALIDATE_VENV", raising=False)
    monkeypatch.setenv("SHELLCHECK", "fake-shellcheck")
    monkeypatch.setenv("SHFMT", "fake-shfmt")
    return load_script(SCRIPT, "validate_repo")


def check(validate: Any, text: str, path: str = ".gitea/workflows/x.yml") -> list[Any]:
    return list(validate.check_workflow(path, text, yaml))


def criteria(findings: list[Any]) -> list[str]:
    return [finding.criterion for finding in findings]


def workflow(jobs: str, header: str = "name: W\non: push\npermissions:\n  contents: read\n") -> str:
    return header + "jobs:\n" + jobs


def step_job(step_lines: str) -> str:
    return (
        "  build:\n    name: build\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n"
        "    steps:\n" + step_lines
    )


def make_repo(root: Path, files: dict[str, str], init_git: bool = True) -> Path:
    for name, content in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    if init_git:
        REAL_RUN(["git", "init", "-q", str(root)], check=True)
        REAL_RUN(["git", "-C", str(root), "add", "-A"], check=True)
    return root


def patch_shell(
    monkeypatch: pytest.MonkeyPatch,
    validate: Any,
    shellcheck: int = 0,
    shfmt: int = 0,
    raises: OSError | None = None,
) -> list[list[str]]:
    """Replace subprocess.run for the fake shell tools; git still runs for real."""
    calls: list[list[str]] = []
    codes = {"fake-shellcheck": shellcheck, "fake-shfmt": shfmt}

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        if command[0] == "git":
            return REAL_RUN(command, **kwargs)
        calls.append(command)
        if raises is not None:
            raise raises
        return subprocess.CompletedProcess(command, codes[command[0]])

    monkeypatch.setattr(validate.subprocess, "run", run)
    return calls


def run_in(
    monkeypatch: pytest.MonkeyPatch, validate: Any, root: Path
) -> None:
    monkeypatch.chdir(root)
    validate.run()


# WF-1, WF-3 ---------------------------------------------------------------


def test_check_workflow_reports_wf1_for_invalid_yaml(validate: Any) -> None:
    found = check(validate, "a: [\n")
    assert criteria(found) == ["WF-1"]
    assert found[0].line >= 1


def test_check_workflow_reports_wf1_on_line_one_without_a_mark(validate: Any) -> None:
    def compose(text: str) -> None:
        raise yaml.YAMLError("boom")

    fake = SimpleNamespace(compose=compose, YAMLError=yaml.YAMLError)
    found = validate.check_workflow("x.yml", "", fake)
    assert [(item.line, item.criterion) for item in found] == [(1, "WF-1")]


@pytest.mark.parametrize("text", ["", "just text\n"])
def test_check_workflow_reports_wf3_for_empty_or_scalar_file(validate: Any, text: str) -> None:
    assert criteria(check(validate, text)) == ["WF-3"]


def test_check_workflow_reports_wf3_per_missing_key(validate: Any) -> None:
    found = check(validate, "other: 1\n")
    assert [item.message for item in found] == [
        "The file declares no 'name'.",
        "The file declares no 'on'.",
        "The file declares no 'jobs'.",
    ]


def test_check_workflow_accepts_a_good_workflow(validate: Any) -> None:
    assert check(validate, GOOD) == []


def test_check_workflow_ignores_jobs_that_are_not_a_mapping(validate: Any) -> None:
    assert check(validate, "name: W\non: push\njobs: text\n") == []


# WF-2 ---------------------------------------------------------------------


def test_check_duplicates_reports_same_name_in_gitea_and_github(validate: Any) -> None:
    files = [".gitea/workflows/ci.yml", ".github/workflows/ci.yml", ".github/workflows/other.yml"]
    found = validate.check_duplicates(files)
    assert [(item.path, item.criterion) for item in found] == [(".github/workflows/ci.yml", "WF-2")]


def test_check_duplicates_ignores_scoped_workflows(validate: Any) -> None:
    files = [".gitea/scoped_workflows/ci.yml", ".github/workflows/ci.yml"]
    assert validate.check_duplicates(files) == []


# WF-5 ---------------------------------------------------------------------


def test_check_workflow_reports_wf5_for_job_and_step_without_name(validate: Any) -> None:
    jobs = "  build:\n    runs-on: x\n    timeout-minutes: 1\n    steps:\n      - run: echo\n"
    found = check(validate, workflow(jobs))
    assert criteria(found) == ["WF-5", "WF-5"]
    assert "Job 'build' has no name" in found[0].message
    assert "step of job 'build' has no name" in found[1].message


def test_check_workflow_reports_wf5_for_duplicate_step_name(validate: Any) -> None:
    steps = "      - name: Same\n        run: a\n      - name: Same\n        run: b\n"
    found = check(validate, workflow(step_job(steps)))
    assert criteria(found) == ["WF-5"]
    assert "'Same' is used twice" in found[0].message


def test_check_workflow_survives_steps_that_are_not_a_list(validate: Any) -> None:
    jobs = "  build:\n    name: b\n    runs-on: x\n    timeout-minutes: 1\n    steps: text\n"
    assert check(validate, workflow(jobs)) == []


def test_run_treats_wf5_as_a_warning_and_passes(
    validate: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    jobs = "  build:\n    runs-on: x\n    timeout-minutes: 1\n    steps:\n      - name: s\n        run: echo\n"
    root = make_repo(tmp_path, {".gitea/workflows/a.yml": workflow(jobs)})
    run_in(monkeypatch, validate, root)
    out = capsys.readouterr().out
    assert "::warning file=.gitea/workflows/a.yml,line=6::[WF-5] Job 'build' has no name." in out
    assert "1 finding(s), 0 error(s)." in out


# WF-7 ---------------------------------------------------------------------


def test_check_workflow_reports_wf7_when_no_permissions_anywhere(validate: Any) -> None:
    text = workflow(step_job("      - name: s\n        run: echo\n"), header="name: W\non: push\n")
    found = check(validate, text)
    assert criteria(found) == ["WF-7"]


def test_check_workflow_accepts_job_level_permissions(validate: Any) -> None:
    job = step_job("      - name: s\n        run: echo\n").replace(
        "    name: build\n", "    name: build\n    permissions:\n      contents: read\n"
    )
    assert check(validate, workflow(job, header="name: W\non: push\n")) == []


def test_check_workflow_reports_wf7_for_a_calling_job_without_permissions(validate: Any) -> None:
    jobs = "  call:\n    uses: TirSystem/git-workflows/.gitea/workflows/x.yml@v2\n"
    found = check(validate, workflow(jobs, header="name: W\non: push\n"))
    assert criteria(found) == ["WF-7"]


# WF-8 ---------------------------------------------------------------------

SHA = "a" * 40


@pytest.mark.parametrize(
    ("value", "flagged"),
    [
        ("actions/checkout", True),
        (f"actions/checkout@{SHA}", False),
        ("actions/checkout@v4.2.2", False),
        ("actions/checkout@4.2.2", False),
        ("actions/checkout@v4.2.2-rc.1", False),
        ("TirSystem/git-workflows/.gitea/workflows/x.yml@v2", False),
        ("actions/checkout@v4", True),
        ("actions/checkout@main", True),
        ("actions/checkout@v4.2", True),
        ("./local-action", False),
        ("docker://alpine:3", False),
    ],
)
def test_check_uses_decides_wf8(validate: Any, value: str, flagged: bool) -> None:
    found: list[Any] = []
    validate.check_uses("x.yml", value, 3, found)
    assert criteria(found) == (["WF-8"] if flagged else [])


def test_check_uses_messages_name_the_problem(validate: Any) -> None:
    found: list[Any] = []
    validate.check_uses("x.yml", "actions/checkout", 1, found)
    validate.check_uses("x.yml", "actions/checkout@v4", 2, found)
    validate.check_uses("x.yml", "actions/checkout@main", 3, found)
    assert "no version" in found[0].message
    assert "another organisation" in found[1].message
    assert "branch" in found[2].message


def test_check_workflow_checks_step_and_job_level_uses(validate: Any) -> None:
    step = "      - name: s\n        uses: actions/checkout@main\n"
    found = check(validate, workflow(step_job(step)))
    assert [(item.criterion, item.line) for item in found] == [("WF-8", 12)]
    jobs = "  call:\n    uses: other/repo/.gitea/workflows/x.yml@main\n"
    found = check(validate, workflow(jobs))
    assert [(item.criterion, item.line) for item in found] == [("WF-8", 7)]


# WF-9 ---------------------------------------------------------------------


@pytest.mark.parametrize("secret", ["GITEA_X", "GITHUB_X"])
def test_check_workflow_reports_wf9_for_reserved_secret_names(validate: Any, secret: str) -> None:
    step = f"      - name: s\n        env:\n          T: ${{{{ secrets.{secret} }}}}\n        run: echo\n"
    found = check(validate, workflow(step_job(step)))
    assert criteria(found) == ["WF-9"]
    assert secret in found[0].message


def test_check_workflow_accepts_github_token_and_other_secrets_in_env(validate: Any) -> None:
    step = (
        "      - name: s\n        env:\n          A: ${{ secrets.GITHUB_TOKEN }}\n"
        "          B: ${{ secrets.MY_TOKEN }}\n        run: echo\n"
    )
    assert check(validate, workflow(step_job(step))) == []


def test_check_workflow_reports_wf9_for_a_secret_in_a_run_command(validate: Any) -> None:
    step = "      - name: s\n        run: curl -H ${{ secrets.MY_TOKEN }} x\n"
    assert criteria(check(validate, workflow(step_job(step)))) == ["WF-9"]


# WF-10 --------------------------------------------------------------------


@pytest.mark.parametrize(
    "expression",
    ["inputs.name", "github.event.pull_request.title", "gitea.event.issue.title", "steps.a.outputs.value"],
)
def test_check_workflow_reports_wf10_for_untrusted_text_in_run(validate: Any, expression: str) -> None:
    step = f"      - name: s\n        run: echo ${{{{ {expression} }}}}\n"
    assert criteria(check(validate, workflow(step_job(step)))) == ["WF-10"]


def test_check_workflow_accepts_trusted_expressions_in_run(validate: Any) -> None:
    step = "      - name: s\n        run: echo ${{ github.sha }}\n"
    assert check(validate, workflow(step_job(step))) == []


# WF-14 --------------------------------------------------------------------


def test_check_workflow_reports_wf14_for_missing_runs_on_and_timeout(validate: Any) -> None:
    jobs = "  build:\n    name: b\n    steps:\n      - name: s\n        run: echo\n"
    found = check(validate, workflow(jobs))
    assert criteria(found) == ["WF-14", "WF-14"]
    assert "runs-on" in found[0].message
    assert "timeout-minutes" in found[1].message


def test_check_workflow_exempts_a_calling_job_from_wf14_and_wf5(validate: Any) -> None:
    jobs = "  call:\n    uses: TirSystem/git-workflows/.gitea/workflows/x.yml@v2\n"
    assert check(validate, workflow(jobs)) == []


# WF-20 --------------------------------------------------------------------


def run_block(lines: int) -> str:
    body = "".join(f"          echo {number}\n" for number in range(lines))
    return step_job("      - name: s\n        run: |\n" + body)


def test_check_workflow_accepts_a_run_block_of_five_lines(validate: Any) -> None:
    assert check(validate, workflow(run_block(5))) == []


def test_check_workflow_reports_wf20_for_a_run_block_of_six_lines(validate: Any) -> None:
    found = check(validate, workflow(run_block(6)))
    assert criteria(found) == ["WF-20"]
    assert "6 lines" in found[0].message


# Silencing ------------------------------------------------------------------


def test_ignored_matches_the_criterion_on_the_line(validate: Any) -> None:
    finding = validate.Finding("x.yml", 2, "WF-8", "m")
    lines = ["a", "uses: x  # validate-ignore: WF-7, WF-8", "b"]
    assert validate.ignored(finding, lines, set())
    assert not validate.ignored(validate.Finding("x.yml", 1, "WF-8", "m"), lines, set())
    assert not validate.ignored(validate.Finding("x.yml", 2, "WF-9", "m"), lines, set())


def test_ignored_matches_the_criterion_for_the_whole_file(validate: Any) -> None:
    finding = validate.Finding("x.yml", 99, "WF-5", "m")
    assert validate.ignored(finding, ["a"], {"WF-5"})
    assert not validate.ignored(finding, ["a"], set())


def test_run_silences_findings_on_the_line_and_for_the_file(
    validate: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    text = (
        "name: A\n"
        "on: push\n"
        "# validate-ignore-file: WF-5\n"
        "jobs:\n"
        "  build:  # validate-ignore: WF-7, WF-14\n"
        "    steps:\n"
        "      - run: echo hi\n"
    )
    root = make_repo(tmp_path, {".gitea/workflows/a.yml": text})
    run_in(monkeypatch, validate, root)
    assert "0 finding(s), 0 error(s)." in capsys.readouterr().out


def test_ignored_accepts_an_explanation_after_the_ids(validate: Any) -> None:
    lines = ["uses: x  # validate-ignore: WF-8 because the tag is ours"]
    assert validate.ignored(validate.Finding("x.yml", 1, "WF-8", "m"), lines, set())
    assert not validate.ignored(validate.Finding("x.yml", 1, "WF-7", "m"), lines, set())


def test_run_silences_findings_when_the_comments_carry_an_explanation(
    validate: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    text = (
        "name: A\n"
        "on: push\n"
        "# validate-ignore-file: WF-5, WF-7 because the names are generated\n"
        "jobs:\n"
        "  build:\n"
        "    runs-on: x\n"
        "    timeout-minutes: 1\n"
        "    steps:\n"
        "      - name: s\n"
        "        uses: actions/checkout@main  # validate-ignore: WF-8 because the tag is ours\n"
    )
    root = make_repo(tmp_path, {".gitea/workflows/a.yml": text})
    run_in(monkeypatch, validate, root)
    assert "0 finding(s), 0 error(s)." in capsys.readouterr().out


# Findings: order and format -----------------------------------------------


def test_run_prints_findings_sorted_as_annotations_and_fails(
    validate: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    text = "name: A\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo hi\n"
    root = make_repo(tmp_path, {".gitea/workflows/a.yml": text})
    monkeypatch.chdir(root)
    with pytest.raises(SystemExit) as raised:
        validate.run()
    assert raised.value.code == 1
    lines = capsys.readouterr().out.splitlines()
    path = ".gitea/workflows/a.yml"
    assert lines == [
        f"::error file={path},line=4::[WF-14] Job 'build' has no timeout-minutes.",
        f"::warning file={path},line=4::[WF-5] Job 'build' has no name.",
        f"::error file={path},line=4::[WF-7] Job 'build' declares no permissions.",
        f"::warning file={path},line=7::[WF-5] A step of job 'build' has no name.",
        "Checked 1 workflow file(s) and 0 shell script(s): 4 finding(s), 2 error(s).",
        "::error::[finding] The validation found errors; fix them or silence them with "
        "'# validate-ignore: <criterion>'.",
    ]


def test_run_reports_wf1_and_wf2_for_broken_and_duplicate_files(
    validate: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_repo(
        tmp_path,
        {
            ".gitea/workflows/ci.yml": GOOD,
            ".github/workflows/ci.yml": GOOD,
            ".github/workflows/broken.yml": "a: [\n",
        },
    )
    monkeypatch.chdir(root)
    with pytest.raises(SystemExit):
        validate.run()
    out = capsys.readouterr().out
    assert "::error file=.github/workflows/broken.yml,line=" in out
    assert "[WF-1] Not valid YAML" in out
    assert "::error file=.github/workflows/ci.yml,line=1::[WF-2]" in out


def test_run_passes_for_a_clean_repository(
    validate: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_repo(tmp_path, {".gitea/workflows/a.yml": GOOD})
    run_in(monkeypatch, validate, root)
    assert "1 workflow file(s) and 0 shell script(s): 0 finding(s), 0 error(s)." in capsys.readouterr().out


# Nothing to validate, shell scripts ---------------------------------------


def test_run_is_green_when_there_is_nothing_to_validate(
    validate: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_repo(tmp_path, {"README.md": "# x\n", "src/app.py": "x = 1\n"})
    calls = patch_shell(monkeypatch, validate)
    run_in(monkeypatch, validate, root)
    assert "nothing to validate" in capsys.readouterr().out
    assert calls == []


def test_run_checks_a_repository_with_only_shell_scripts(
    validate: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_repo(tmp_path, {"scripts/a.sh": "echo a\n", "b.sh": "echo b\n"})
    calls = patch_shell(monkeypatch, validate)
    run_in(monkeypatch, validate, root)
    assert calls == [
        ["fake-shellcheck", "b.sh", "scripts/a.sh"],
        ["fake-shfmt", "-d", "b.sh", "scripts/a.sh"],
    ]
    assert "0 workflow file(s) and 2 shell script(s): 0 finding(s), 0 error(s)." in capsys.readouterr().out


@pytest.mark.parametrize(("shellcheck", "shfmt", "tools"), [(1, 0, ["shellcheck"]), (0, 1, ["shfmt"]), (1, 1, ["shellcheck", "shfmt"])])
def test_run_fails_when_a_shell_tool_finds_problems(
    validate: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    shellcheck: int,
    shfmt: int,
    tools: list[str],
) -> None:
    root = make_repo(tmp_path, {"a.sh": "echo a\n"})
    patch_shell(monkeypatch, validate, shellcheck=shellcheck, shfmt=shfmt)
    monkeypatch.chdir(root)
    with pytest.raises(SystemExit) as raised:
        validate.run()
    assert raised.value.code == 1
    out = capsys.readouterr().out
    for tool in tools:
        assert f"::error::[shell] {tool} found problems" in out
    assert out.count("[shell]") == len(tools)


def test_check_shell_fails_as_tool_when_a_command_cannot_start(
    validate: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    patch_shell(monkeypatch, validate, raises=FileNotFoundError("missing"))
    with pytest.raises(SystemExit) as raised:
        validate.check_shell(["a.sh"])
    assert raised.value.code == 1
    assert "::error::[tool] shellcheck cannot be started" in capsys.readouterr().out


def test_check_shell_returns_true_when_both_tools_are_clean(validate: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    patch_shell(monkeypatch, validate)
    assert validate.check_shell(["a.sh"]) is True


# Tool commands, file listing ----------------------------------------------


def test_tool_command_prefers_the_environment(validate: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHFMT", "my-shfmt")
    assert validate.tool_command("shfmt") == "my-shfmt"


def test_tool_command_defaults_to_the_virtual_environment(validate: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SHELLCHECK")
    assert validate.tool_command("shellcheck") == str(Path(".validate-venv") / "bin" / "shellcheck")
    monkeypatch.setenv("VALIDATE_VENV", "venv2")
    assert validate.tool_command("shellcheck") == str(Path("venv2") / "bin" / "shellcheck")


def test_tracked_files_lists_only_git_tracked_files(validate: Any, tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"b.sh": "", "dir/a.yml": ""})
    (root / "untracked.sh").write_text("", encoding="utf-8")
    assert validate.tracked_files(root) == ["b.sh", "dir/a.yml"]


def test_tracked_files_falls_back_to_every_file_outside_git(validate: Any, tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"b.sh": "", "dir/a.yml": ""}, init_git=False)
    assert validate.tracked_files(root) == ["b.sh", "dir/a.yml"]


def test_tracked_files_falls_back_to_every_file_when_git_cannot_start(
    validate: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = make_repo(tmp_path, {"b.sh": "", "dir/a.yml": ""}, init_git=False)

    def missing_git(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        raise FileNotFoundError("git")

    monkeypatch.setattr(validate.subprocess, "run", missing_git)
    assert validate.tracked_files(root) == ["b.sh", "dir/a.yml"]


def test_run_skips_tracked_files_deleted_from_the_working_tree(
    validate: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_repo(
        tmp_path,
        {".gitea/workflows/a.yml": GOOD, ".gitea/workflows/gone.yml": GOOD, "gone.sh": "echo a\n"},
    )
    (root / ".gitea" / "workflows" / "gone.yml").unlink()
    (root / "gone.sh").unlink()
    calls = patch_shell(monkeypatch, validate)
    run_in(monkeypatch, validate, root)
    assert "1 workflow file(s) and 0 shell script(s): 0 finding(s), 0 error(s)." in capsys.readouterr().out
    assert calls == []


def test_check_workflow_accepts_a_job_without_steps(validate: Any) -> None:
    jobs = "  build:\n    name: b\n    runs-on: x\n    timeout-minutes: 1\n"
    assert check(validate, workflow(jobs)) == []


def test_workflow_files_keeps_yaml_files_directly_in_the_known_directories(validate: Any) -> None:
    files = [
        ".gitea/workflows/a.yml",
        ".gitea/workflows/b.yaml",
        ".gitea/workflows/sub/c.yml",
        ".gitea/scoped_workflows/d.yml",
        ".github/workflows/e.yml",
        ".github/workflows/readme.md",
        "other/f.yml",
    ]
    assert validate.workflow_files(files) == [
        ".gitea/workflows/a.yml",
        ".gitea/workflows/b.yaml",
        ".gitea/scoped_workflows/d.yml",
        ".github/workflows/e.yml",
    ]


def test_shell_scripts_keeps_sh_files(validate: Any) -> None:
    assert validate.shell_scripts(["a.sh", "b.py", "d/c.sh"]) == ["a.sh", "d/c.sh"]


# install ------------------------------------------------------------------


def fake_install(
    monkeypatch: pytest.MonkeyPatch, validate: Any, failing_call: int | None = None
) -> list[list[str]]:
    calls: list[list[str]] = []

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 1 if failing_call == len(calls) else 0)

    monkeypatch.setattr(validate.subprocess, "run", run)
    return calls


def test_install_creates_the_environment_and_installs_pinned_tools(
    validate: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("VALIDATE_VENV", "venv3")
    calls = fake_install(monkeypatch, validate)
    validate.install()
    assert calls[0] == [sys.executable, "-m", "venv", "venv3"]
    assert calls[1][0] == str(Path("venv3") / "bin" / "pip")
    assert calls[1][1:] == [
        "install",
        "--quiet",
        "PyYAML==6.0.3",
        "shellcheck-py==0.10.0.1",
        "shfmt-py==3.11.0.2",
    ]


@pytest.mark.parametrize("failing_call", [1, 2])
def test_install_fails_as_tool_when_a_command_fails(
    validate: Any,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    failing_call: int,
) -> None:
    calls = fake_install(monkeypatch, validate, failing_call=failing_call)
    with pytest.raises(SystemExit) as raised:
        validate.install()
    assert raised.value.code == 1
    assert len(calls) == failing_call
    assert "::error::[tool]" in capsys.readouterr().out


# main, __main__, PyYAML -----------------------------------------------------


@pytest.mark.parametrize("command", ["install", "run"])
def test_main_dispatches_to_the_command(validate: Any, monkeypatch: pytest.MonkeyPatch, command: str) -> None:
    called: list[str] = []
    monkeypatch.setattr(validate, "install", lambda: called.append("install"))
    monkeypatch.setattr(validate, "run", lambda: called.append("run"))
    validate.main(["validate_repo.py", command])
    assert called == [command]


@pytest.mark.parametrize("argv", [["validate_repo.py"], ["validate_repo.py", "other"], ["validate_repo.py", "run", "x"]])
def test_main_fails_with_a_usage_error(
    validate: Any, capsys: pytest.CaptureFixture[str], argv: list[str]
) -> None:
    with pytest.raises(SystemExit) as raised:
        validate.main(argv)
    assert raised.value.code == 1
    assert "::error::[configuration] usage: validate_repo.py install|run" in capsys.readouterr().out


def test_module_run_as_a_script_uses_main(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["validate_repo.py"])
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    assert raised.value.code == 1
    assert "[configuration]" in capsys.readouterr().out


def test_run_fails_as_tool_when_pyyaml_is_missing(
    validate: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(sys.modules, "yaml", None)  # makes "import yaml" raise ImportError
    with pytest.raises(SystemExit) as raised:
        validate.run()
    assert raised.value.code == 1
    assert "::error::[tool] PyYAML is not installed" in capsys.readouterr().out


# Integration: this repository's own validate workflow -----------------------


def test_own_validate_workflow_has_no_findings(validate: Any) -> None:
    text = OWN_WORKFLOW.read_text(encoding="utf-8")
    assert check(validate, text, ".gitea/scoped_workflows/validate.yml") == []


def test_own_validate_workflow_has_the_documented_shape() -> None:
    text = OWN_WORKFLOW.read_text(encoding="utf-8")
    document = yaml.safe_load(text)
    triggers = document.get("on", document.get(True))  # PyYAML reads the key "on" as True
    assert document["name"] == "Validate"
    assert set(triggers) == {"pull_request", "push", "workflow_dispatch"}
    assert triggers["push"]["branches"] == ["main"]
    assert list(document["jobs"]) == ["validate"]
    assert "secrets." not in text
    job = document["jobs"]["validate"]
    assert job["permissions"] == {"contents": "read"}
    steps = job["steps"]
    fetch = [step for step in steps if step.get("with", {}).get("repository")]
    assert [step["with"]["repository"] for step in fetch] == ["TirSystem/git-workflows"]
    assert fetch[0]["with"]["ref"] == "v3"
    commands = [step["run"] for step in steps if "run" in step]
    assert commands == [
        "python3 shared-scripts/tools/validate_repo.py install",
        ".validate-venv/bin/python shared-scripts/tools/validate_repo.py run",
    ]
