"""Offline tests for tools/lint-action-scripts.sh (MIL-012 task 6).

The script runs shellcheck and shfmt on a folder; the tests give it a clean
script, a script with a shellcheck problem and a badly formatted one, so a
seeded error is shown to fail the run.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from workflow_source import REPO_ROOT

SCRIPT = REPO_ROOT / "tools" / "lint-action-scripts.sh"
WORKFLOW = REPO_ROOT / ".gitea" / "workflows" / "validate-workflows.yml"
BASH = shutil.which("bash")
# the tools are in the virtual environment of the interpreter that runs the tests
SEARCH_PATH = os.pathsep.join([str(Path(sys.executable).parent), os.environ.get("PATH", "")])
SHELLCHECK = shutil.which("shellcheck", path=SEARCH_PATH)
SHFMT = shutil.which("shfmt", path=SEARCH_PATH)
HAVE_TOOLS = BASH and SHELLCHECK and SHFMT

CLEAN = '#!/usr/bin/env bash\nmain() {\n  echo "$1"\n}\n\nmain "$@"\n'
SHELLCHECK_PROBLEM = '#!/usr/bin/env bash\nmain() {\n  echo $1\n}\n\nmain "$@"\n'
BADLY_FORMATTED = '#!/usr/bin/env bash\nmain() {\n        echo "$1"\n}\n\nmain "$@"\n'


def lint(folder: Path) -> subprocess.CompletedProcess:
    # shfmt reads .editorconfig from the folder upwards; a temporary folder is
    # outside this repository, so it gets a copy of the repository's file
    if folder != REPO_ROOT / "actions":
        shutil.copy(REPO_ROOT / ".editorconfig", folder / ".editorconfig")
    env = {**os.environ, "SHELLCHECK": str(SHELLCHECK), "SHFMT": str(SHFMT)}
    return subprocess.run(
        [BASH, str(SCRIPT), str(folder)],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO_ROOT,
        env=env,
    )


@pytest.mark.skipif(not HAVE_TOOLS, reason="bash, shellcheck and shfmt are needed")
class TestLint:
    def test_a_clean_script_passes(self, tmp_path):
        (tmp_path / "ok.sh").write_bytes(CLEAN.encode())  # LF on every platform
        result = lint(tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "clean" in result.stdout

    def test_a_shellcheck_problem_fails(self, tmp_path):
        (tmp_path / "bad.sh").write_bytes(SHELLCHECK_PROBLEM.encode())  # LF on every platform
        result = lint(tmp_path)
        assert result.returncode == 1
        assert "::error::[lint] shellcheck" in result.stdout

    def test_a_badly_formatted_script_fails(self, tmp_path):
        (tmp_path / "ugly.sh").write_bytes(BADLY_FORMATTED.encode())  # LF on every platform
        result = lint(tmp_path)
        assert result.returncode == 1
        assert "::error::[lint] shfmt" in result.stdout

    def test_no_scripts_is_not_a_failure(self, tmp_path):
        result = lint(tmp_path)
        assert result.returncode == 0
        assert "nothing was checked" in result.stdout

    def test_the_scripts_of_the_actions_are_clean(self):
        result = lint(REPO_ROOT / "actions")
        assert result.returncode == 0, result.stdout + result.stderr


class TestWorkflow:
    def test_validate_workflows_runs_the_lint_with_pinned_tools(self):
        document = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        commands = [step.get("run", "") for step in document["jobs"]["validate"]["steps"]]
        assert any("tools/lint-action-scripts.sh" in command for command in commands)
        requirements = (REPO_ROOT / "tests" / "requirements.txt").read_text(encoding="utf-8")
        assert "shellcheck-py==" in requirements
        assert "shfmt-py==" in requirements
