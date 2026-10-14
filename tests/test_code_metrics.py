"""Offline tests for the reusable code-metrics workflow and tools/code-metrics.sh (ADR-0010).

The script steps run in a throwaway git repository whose `origin` is a bare
repository on disk, so no network and no instance is needed.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from workflow_source import REPO_ROOT

WORKFLOW = REPO_ROOT / ".gitea" / "workflows" / "code-metrics.yml"
SCRIPT = REPO_ROOT / "tools" / "code-metrics.sh"
BASH = shutil.which("bash")
GIT = shutil.which("git")

pytestmark = pytest.mark.skipif(
    BASH is None or GIT is None, reason="bash and git are needed to run the workflow steps"
)

COVERAGE = '<?xml version="1.0" ?>\n<coverage lines-covered="87" lines-valid="100"><packages/></coverage>\n'


@pytest.fixture(scope="module")
def document() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


class TestDefinition:
    def test_is_a_reusable_workflow_with_the_contract_inputs(self, document):
        inputs = document[True]["workflow_call"]["inputs"]  # PyYAML reads `on` as True
        assert {name: item["default"] for name, item in inputs.items()} == {
            "working-directory": ".",
            "exclude": "",
            "coverage-report": "",
            "coverage-artifact": "",
            "coverage-warn": "60",
            "coverage-good": "80",
            "badges-branch": "badges",
            "tools-ref": "v1",
        }

    def test_asks_for_contents_write_and_nothing_else_and_needs_no_secret(self, document):
        job = document["jobs"]["code-metrics"]
        assert job["permissions"] == {"contents": "write"}
        assert "secrets" not in WORKFLOW.read_text(encoding="utf-8").replace("needs no secret", "")

    def test_inputs_reach_the_scripts_only_through_the_environment(self, document):
        job = document["jobs"]["code-metrics"]
        for step in job["steps"]:
            assert "${{" not in step.get("run", ""), f"{step.get('name')} interpolates an expression"
        assert set(job["env"]) == {
            "WORKING_DIRECTORY",
            "EXCLUDE",
            "COVERAGE_REPORT",
            "COVERAGE_ARTIFACT",
            "COVERAGE_WARN",
            "COVERAGE_GOOD",
            "BADGES_BRANCH",
        }

    def test_the_workflow_embeds_no_script_and_runs_the_file(self, document):
        steps = document["jobs"]["code-metrics"]["steps"]
        assert [step["run"] for step in steps if "run" in step] == [
            "bash shared-scripts/tools/code-metrics.sh validate",
            "bash shared-scripts/tools/code-metrics.sh measure",
            "bash shared-scripts/tools/code-metrics.sh publish",
        ]

    def test_the_scripts_are_fetched_at_the_tools_ref_input(self, document):
        steps = document["jobs"]["code-metrics"]["steps"]
        fetch = next(step for step in steps if step.get("name") == "Fetch the shared scripts")
        assert fetch["with"] == {
            "repository": "TirSystem/github-action",
            "ref": "${{ inputs.tools-ref }}",
            "path": "shared-scripts",
        }

    def test_the_script_parses(self):
        result = subprocess.run([BASH, "-n", str(SCRIPT)], text=True, capture_output=True)
        assert result.returncode == 0, result.stderr

    def test_an_unknown_command_is_refused(self):
        result = subprocess.run([BASH, str(SCRIPT), "bogus"], text=True, capture_output=True)
        assert result.returncode == 2


def git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        [GIT, "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


@pytest.fixture()
def python3_bin(tmp_path) -> Path:
    """A directory with a `python3` that runs the interpreter of the tests."""
    directory = tmp_path / "pybin"
    directory.mkdir()
    shim = directory / "python3"
    shim.write_text(f'#!/bin/sh\nexec "{Path(sys.executable).as_posix()}" "$@"\n', newline="\n")
    shim.chmod(0o755)
    return directory


@pytest.fixture()
def remote(tmp_path) -> Path:
    path = tmp_path / "remote.git"
    subprocess.run([GIT, "init", "-q", "--bare", str(path)], check=True)
    return path


@pytest.fixture()
def repo(tmp_path, remote) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git("init", "-q", "-b", "main", cwd=root)
    git("remote", "add", "origin", str(remote), cwd=root)
    (root / "a.py").write_text("x = 1\n# c\n\n", newline="\n")
    (root / "run.sh").write_text("echo hi\n", newline="\n")
    git("add", "-A", cwd=root)
    git("commit", "-q", "-m", "init", cwd=root)
    return root


def run(command: str, repo: Path, tmp_path: Path, python3_bin: Path, **env: str):
    environment = dict(os.environ)
    environment.update(
        {
            "WORKING_DIRECTORY": ".",
            "EXCLUDE": "",
            "COVERAGE_REPORT": "",
            "COVERAGE_ARTIFACT": "",
            "COVERAGE_WARN": "60",
            "COVERAGE_GOOD": "80",
            "BADGES_BRANCH": "badges",
            "BADGES_OUT": str(tmp_path / "out"),
            "PATH": f"{python3_bin.as_posix()}{os.pathsep}{environment['PATH']}",
        }
    )
    environment.update(env)
    return subprocess.run(
        [BASH, str(SCRIPT), command], cwd=repo, env=environment, text=True, capture_output=True
    )


def branch_files(remote: Path, branch: str = "badges") -> list[str]:
    out = subprocess.run(
        [GIT, "--git-dir", str(remote), "ls-tree", "-r", "--name-only", branch],
        text=True,
        capture_output=True,
    )
    return out.stdout.split()


def commit_count(remote: Path, branch: str = "badges") -> int:
    out = subprocess.run(
        [GIT, "--git-dir", str(remote), "rev-list", "--count", branch], text=True, capture_output=True
    )
    return int(out.stdout.strip() or 0)


def measure_and_publish(repo, tmp_path, python3_bin, **env):
    measured = run("measure", repo, tmp_path, python3_bin, **env)
    assert measured.returncode == 0, measured.stdout + measured.stderr
    return run("publish", repo, tmp_path, python3_bin, **env)


class TestValidate:
    def test_accepts_the_defaults(self, repo, tmp_path, python3_bin):
        result = run("validate", repo, tmp_path, python3_bin)
        assert result.returncode == 0, result.stdout
        assert "badges go to the branch badges" in result.stdout

    @pytest.mark.parametrize(
        ("name", "value", "message"),
        [
            ("WORKING_DIRECTORY", "/etc", "working-directory must be a relative path"),
            ("WORKING_DIRECTORY", "../x", "working-directory must be a relative path"),
            ("WORKING_DIRECTORY", "nope", "working-directory 'nope' does not exist"),
            ("COVERAGE_REPORT", "/tmp/c.xml", "coverage-report must be a relative path"),
            ("COVERAGE_ARTIFACT", "cov", "coverage-artifact 'cov' needs coverage-report"),
            ("BADGES_BRANCH", "main", "must not be a default branch"),
            ("BADGES_BRANCH", "master", "must not be a default branch"),
            ("BADGES_BRANCH", "", "must not be a default branch"),
            ("BADGES_BRANCH", "a b", "is not a valid branch name"),
            ("BADGES_BRANCH", "x..y", "is not a valid branch name"),
        ],
    )
    def test_refuses_an_invalid_input_and_names_it(
        self, repo, tmp_path, python3_bin, name, value, message
    ):
        result = run("validate", repo, tmp_path, python3_bin, **{name: value})
        assert result.returncode == 1
        assert f"::error::[configuration] " in result.stdout
        assert message in result.stdout


class TestPublish:
    def test_creates_the_branch_with_the_badges_and_the_numbers(self, repo, remote, tmp_path, python3_bin):
        result = measure_and_publish(repo, tmp_path, python3_bin)
        assert result.returncode == 0, result.stdout + result.stderr
        assert sorted(branch_files(remote)) == ["code-files.svg", "code-lines.svg", "code-metrics.json"]
        shown = subprocess.run(
            [GIT, "--git-dir", str(remote), "show", "badges:code-lines.svg"], text=True, capture_output=True
        ).stdout
        assert 'aria-label="lines of code: 2"' in shown  # a.py has one code line, run.sh one
        message = subprocess.run(
            [GIT, "--git-dir", str(remote), "log", "-1", "--format=%s", "badges"],
            text=True,
            capture_output=True,
        ).stdout.strip()
        assert message == "Update code metrics badges [skip ci]"

    def test_the_branch_of_the_caller_is_not_changed(self, repo, remote, tmp_path, python3_bin):
        before = git("status", "--porcelain", cwd=repo)
        measure_and_publish(repo, tmp_path, python3_bin)
        assert git("status", "--porcelain", cwd=repo) == before
        assert git("branch", "--show-current", cwd=repo) == "main"

    def test_an_unchanged_run_commits_nothing(self, repo, remote, tmp_path, python3_bin):
        measure_and_publish(repo, tmp_path, python3_bin)
        second = measure_and_publish(repo, tmp_path, python3_bin)
        assert second.returncode == 0
        assert "Badges are current; nothing to commit." in second.stdout
        assert commit_count(remote) == 1

    def test_a_changed_number_is_one_commit_that_changes_only_badge_files(
        self, repo, remote, tmp_path, python3_bin
    ):
        measure_and_publish(repo, tmp_path, python3_bin)
        (repo / "b.py").write_text("y = 2\nz = 3\n", newline="\n")
        git("add", "-A", cwd=repo)
        git("commit", "-q", "-m", "more", cwd=repo)
        result = measure_and_publish(repo, tmp_path, python3_bin)
        assert result.returncode == 0, result.stdout
        assert commit_count(remote) == 2
        changed = subprocess.run(
            [GIT, "--git-dir", str(remote), "show", "--name-only", "--format=", "badges"],
            text=True,
            capture_output=True,
        ).stdout.split()
        assert sorted(changed) == ["code-files.svg", "code-lines.svg", "code-metrics.json"]

    def test_a_coverage_report_adds_the_coverage_badge(self, repo, remote, tmp_path, python3_bin):
        (repo / "cov.xml").write_text(COVERAGE, newline="\n")
        result = measure_and_publish(repo, tmp_path, python3_bin, COVERAGE_REPORT="cov.xml")
        assert result.returncode == 0, result.stdout
        assert "coverage.svg" in branch_files(remote)

    def test_a_report_from_an_artifact_is_read_below_the_artifact_directory(
        self, repo, remote, tmp_path, python3_bin
    ):
        artifact = repo / "coverage-artifact"
        artifact.mkdir()
        (artifact / "cov.xml").write_text(COVERAGE, newline="\n")
        result = measure_and_publish(
            repo, tmp_path, python3_bin, COVERAGE_ARTIFACT="coverage", COVERAGE_REPORT="cov.xml"
        )
        assert result.returncode == 0, result.stdout
        assert "coverage.svg" in branch_files(remote)

    def test_a_report_missing_from_the_artifact_names_the_path(self, repo, tmp_path, python3_bin):
        result = run(
            "measure",
            repo,
            tmp_path,
            python3_bin,
            COVERAGE_ARTIFACT="coverage",
            COVERAGE_REPORT="cov.xml",
        )
        assert result.returncode == 1
        assert "coverage-report 'coverage-artifact/cov.xml' does not exist" in result.stdout

    def test_a_missing_report_fails_names_the_file_and_changes_nothing(
        self, repo, remote, tmp_path, python3_bin
    ):
        result = run("measure", repo, tmp_path, python3_bin, COVERAGE_REPORT="nope.xml")
        assert result.returncode == 1
        assert "::error::[configuration] coverage-report 'nope.xml' does not exist." in result.stdout
        assert branch_files(remote) == []

    def test_the_shared_scripts_directory_is_not_counted(self, repo, remote, tmp_path, python3_bin):
        shared = repo / "shared-scripts" / "tools"
        shared.mkdir(parents=True)
        (shared / "big.py").write_text("a = 1\n" * 50, newline="\n")
        measure_and_publish(repo, tmp_path, python3_bin)
        shown = subprocess.run(
            [GIT, "--git-dir", str(remote), "show", "badges:code-files.svg"], text=True, capture_output=True
        ).stdout
        assert 'aria-label="code files: 2"' in shown

    def test_a_branch_that_holds_other_files_is_refused(self, repo, remote, tmp_path, python3_bin):
        git("push", "-q", "origin", "main:docs", cwd=repo)
        result = measure_and_publish(repo, tmp_path, python3_bin, BADGES_BRANCH="docs")
        assert result.returncode == 1
        assert "it is not a badges branch" in result.stdout

    def test_publish_without_measure_is_refused(self, repo, tmp_path, python3_bin):
        result = run("publish", repo, tmp_path, python3_bin)
        assert result.returncode == 1
        assert "run measure first" in result.stdout

    def test_a_rejected_push_is_retried_once_after_a_fetch(self, repo, remote, tmp_path, python3_bin):
        marker = tmp_path / "rejected-once"
        hook = remote / "hooks" / "pre-receive"
        hook.write_text(
            f'#!/bin/sh\nif [ ! -e "{marker.as_posix()}" ]; then touch "{marker.as_posix()}"; '
            "echo rejected once >&2; exit 1; fi\nexit 0\n",
            newline="\n",
        )
        hook.chmod(0o755)
        result = measure_and_publish(repo, tmp_path, python3_bin)
        assert result.returncode == 0, result.stdout + result.stderr
        assert marker.exists()

    def test_two_rejected_pushes_fail(self, repo, remote, tmp_path, python3_bin):
        hook = remote / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\necho rejected >&2\nexit 1\n", newline="\n")
        hook.chmod(0o755)
        result = measure_and_publish(repo, tmp_path, python3_bin)
        assert result.returncode == 1
        assert re.search(r"push to 'badges' failed twice", result.stdout)
