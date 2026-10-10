"""Offline tests for the reusable quality-check workflow (ADR-0005).

The shell steps of the workflow are run with stub tools in a throwaway git
repository, so no network and no real linter is needed.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from workflow_source import REPO_ROOT

WORKFLOW = REPO_ROOT / ".gitea" / "workflows" / "quality-checks.yml"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="bash is needed to run the workflow steps")


@pytest.fixture(scope="module")
def document() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def step_script(document: dict, name: str) -> str:
    steps = document["jobs"]["quality-checks"]["steps"]
    return next(step["run"] for step in steps if step.get("name") == name)


class TestDefinition:
    def test_is_a_reusable_workflow_with_the_contract_inputs(self, document):
        inputs = document[True]["workflow_call"]["inputs"]  # PyYAML reads `on` as True
        assert set(inputs) == {
            "languages",
            "working-directory",
            "ruff-version",
            "mypy-version",
            "shellcheck-py-version",
            "shfmt-py-version",
        }
        assert inputs["languages"]["default"] == "python,shell"
        assert inputs["working-directory"]["default"] == "."

    def test_tool_versions_are_pinned_to_the_adr(self, document):
        inputs = document[True]["workflow_call"]["inputs"]
        assert inputs["ruff-version"]["default"] == "0.6.9"
        assert inputs["mypy-version"]["default"] == "1.11.2"
        assert inputs["shellcheck-py-version"]["default"] == "0.10.0.1"
        assert inputs["shfmt-py-version"]["default"] == "3.11.0.2"

    def test_has_least_privilege_and_needs_no_secret(self, document):
        job = document["jobs"]["quality-checks"]
        assert job["permissions"] == {"contents": "read"}
        assert "secrets" not in WORKFLOW.read_text(encoding="utf-8").replace("needs no secret", "")

    def test_inputs_reach_the_scripts_only_through_the_environment(self, document):
        for step in document["jobs"]["quality-checks"]["steps"]:
            assert "${{" not in step.get("run", ""), f"{step.get('name')} interpolates an expression"

    @pytest.mark.parametrize(
        "name", ["Validate the inputs", "Install the tools", "Run the checks"]
    )
    def test_every_script_parses(self, document, name):
        script = step_script(document, name)
        result = subprocess.run([BASH, "-n"], input=script, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr


STUB = """#!/usr/bin/env bash
name="$(basename "$0")"
[ "$name" = ruff ] && name="ruff $1"
echo "$name :: $*" >> "$STUB_LOG"
case ",${STUB_FAIL}," in
  *",$name,"*)
    echo "$2:1:1: stub finding from $name"
    exit 1
    ;;
esac
exit 0
"""


@pytest.fixture()
def bin_dir(tmp_path) -> Path:
    directory = tmp_path / "bin"
    directory.mkdir()
    for tool in ("ruff", "mypy", "shellcheck", "shfmt"):
        path = directory / tool
        path.write_text(STUB, encoding="utf-8", newline="\n")
        path.chmod(0o755)
    return directory


@pytest.fixture()
def repo(tmp_path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root


def add_files(root: Path, *relative: str) -> None:
    for name in relative:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n", encoding="utf-8", newline="\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)


def run_step(document, name, repo, bin_dir, tmp_path, **env):
    script = step_script(document, name)
    log = tmp_path / "tools.log"
    environment = dict(os.environ)
    environment.update(
        {
            "LANGUAGES": "python,shell",
            "WORKING_DIRECTORY": ".",
            "QC_VENV": (tmp_path / "venv").as_posix(),
            "QC_BIN": bin_dir.as_posix(),
            "STUB_LOG": log.as_posix(),
            "STUB_FAIL": "",
        }
    )
    environment.update(env)
    result = subprocess.run(
        [BASH, "-c", script], cwd=repo, env=environment, text=True, capture_output=True
    )
    calls = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    return result, calls


class TestValidateInputs:
    @pytest.mark.parametrize("languages", ["python", "shell", "python,shell", "python, shell"])
    def test_accepts_the_supported_languages(self, document, repo, bin_dir, tmp_path, languages):
        result, _ = run_step(document, "Validate the inputs", repo, bin_dir, tmp_path, LANGUAGES=languages)
        assert result.returncode == 0, result.stdout + result.stderr

    @pytest.mark.parametrize("languages", ["go", "python,ruby", ""])
    def test_rejects_an_unknown_or_empty_language(self, document, repo, bin_dir, tmp_path, languages):
        result, _ = run_step(document, "Validate the inputs", repo, bin_dir, tmp_path, LANGUAGES=languages)
        assert result.returncode == 1
        assert "[configuration]" in result.stdout

    @pytest.mark.parametrize("directory", ["/etc", "..", "../other", "a/../..", ""])
    def test_rejects_a_directory_outside_the_repository(
        self, document, repo, bin_dir, tmp_path, directory
    ):
        result, _ = run_step(
            document, "Validate the inputs", repo, bin_dir, tmp_path, WORKING_DIRECTORY=directory
        )
        assert result.returncode == 1
        assert "working-directory" in result.stdout


class TestRunChecks:
    def test_runs_every_python_and_shell_tool_on_the_tracked_files(
        self, document, repo, bin_dir, tmp_path
    ):
        add_files(repo, "app.py", "pkg/util.py", "run.sh", "README.md")
        result, calls = run_step(document, "Run the checks", repo, bin_dir, tmp_path)

        assert result.returncode == 0, result.stdout + result.stderr
        assert [c.split(" :: ")[0] for c in calls] == [
            "ruff check", "ruff format", "mypy", "shellcheck", "shfmt",
        ]
        assert "app.py pkg/util.py" in calls[0]
        assert "--strict" in calls[2]
        assert "run.sh" in calls[3]
        assert "All selected checks passed." in result.stdout

    def test_a_failing_tool_fails_the_job_and_the_others_still_run(
        self, document, repo, bin_dir, tmp_path
    ):
        add_files(repo, "app.py", "run.sh")
        result, calls = run_step(
            document, "Run the checks", repo, bin_dir, tmp_path, STUB_FAIL="ruff check,shellcheck"
        )

        assert result.returncode == 1
        assert len(calls) == 5, "every tool runs even after a failure"
        assert "::group::ruff check" in result.stdout
        assert "app.py:1:1: stub finding from ruff check" in result.stdout
        assert "FAIL ruff check" in result.stdout and "FAIL shellcheck" in result.stdout
        assert "PASS mypy --strict" in result.stdout
        assert "Quality checks failed: ruff check shellcheck" in result.stdout

    def test_a_language_without_files_is_skipped_and_passes(
        self, document, repo, bin_dir, tmp_path
    ):
        add_files(repo, "README.md")
        result, calls = run_step(document, "Run the checks", repo, bin_dir, tmp_path)

        assert result.returncode == 0
        assert calls == []
        assert "No python files" in result.stdout and "No shell files" in result.stdout

    def test_only_the_selected_languages_are_checked(self, document, repo, bin_dir, tmp_path):
        add_files(repo, "app.py", "run.sh")
        _, calls = run_step(document, "Run the checks", repo, bin_dir, tmp_path, LANGUAGES="shell")
        assert [c.split(" :: ")[0] for c in calls] == ["shellcheck", "shfmt"]

    def test_only_files_under_the_working_directory_are_checked(
        self, document, repo, bin_dir, tmp_path
    ):
        add_files(repo, "top.py", "service/api.py", "service/deploy.sh")
        _, calls = run_step(
            document, "Run the checks", repo, bin_dir, tmp_path, WORKING_DIRECTORY="service"
        )
        text = "\n".join(calls)
        assert "api.py" in text and "deploy.sh" in text
        assert "top.py" not in text

    def test_untracked_files_are_not_checked(self, document, repo, bin_dir, tmp_path):
        add_files(repo, "tracked.py")
        (repo / "untracked.py").write_text("x\n", encoding="utf-8")
        _, calls = run_step(document, "Run the checks", repo, bin_dir, tmp_path, LANGUAGES="python")
        assert "untracked.py" not in "\n".join(calls)

    def test_a_missing_working_directory_is_a_configuration_error(
        self, document, repo, bin_dir, tmp_path
    ):
        add_files(repo, "app.py")
        result, calls = run_step(
            document, "Run the checks", repo, bin_dir, tmp_path, WORKING_DIRECTORY="nope"
        )
        assert result.returncode == 1
        assert "[configuration]" in result.stdout
        assert calls == []

    def test_no_file_is_changed(self, document, repo, bin_dir, tmp_path):
        add_files(repo, "app.py", "run.sh")
        def snapshot():
            return {p.name: p.read_bytes() for p in repo.iterdir() if p.is_file()}

        before = snapshot()
        run_step(document, "Run the checks", repo, bin_dir, tmp_path, STUB_FAIL="ruff check")
        after = snapshot()
        assert before == after
