"""Static validation of every workflow file in this repository."""

import ast

import pytest
import yaml

from workflow_source import REPO_ROOT, SYNC_SCRIPT, SYNC_WORKFLOW, embedded_python, workflow_files

WORKFLOWS = workflow_files()


def test_workflow_files_exist():
    assert WORKFLOWS, "no workflow files found"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
class TestEachWorkflow:
    def test_is_valid_yaml_with_name_and_jobs(self, path):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(document, dict)
        assert document.get("name"), "a workflow needs a name"
        assert document.get("jobs"), "a workflow needs at least one job"

    def test_embedded_python_compiles(self, path):
        for source in embedded_python(path):
            ast.parse(source, filename=str(path))

    def test_every_job_declares_permissions_and_runner(self, path):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        for name, job in document["jobs"].items():
            assert "runs-on" in job, f"job {name} has no runs-on"
            assert "permissions" in job, f"job {name} has no explicit permissions"


def test_sync_workflow_embeds_no_script_and_runs_the_file():
    assert embedded_python(SYNC_WORKFLOW) == []
    document = yaml.safe_load(SYNC_WORKFLOW.read_text(encoding="utf-8"))
    steps = document["jobs"]["sync-metadata"]["steps"]
    assert steps[0]["with"]["repository"] == "TirSystem/github-action"
    assert steps[-1]["run"] == "python3 shared-scripts/tools/sync_github_metadata.py"


def test_sync_script_compiles_and_is_a_file_of_this_repository():
    source = SYNC_SCRIPT.read_text(encoding="utf-8")
    ast.parse(source, filename=str(SYNC_SCRIPT))
    assert "def main()" in source and 'if __name__ == "__main__":' in source


def test_each_workflow_name_has_one_source():
    names = [path.name for path in WORKFLOWS]
    assert len(names) == len(set(names)), "a workflow exists in several directories"


def test_no_workflow_copy_outside_the_workflow_directories():
    stray = [
        path.relative_to(REPO_ROOT)
        for pattern in ("*.yml", "*.yaml")
        for folder in (REPO_ROOT, REPO_ROOT / "src")
        if folder.is_dir()
        for path in folder.glob(pattern)
        if path.name == SYNC_WORKFLOW.name
    ]
    assert not stray, f"duplicate workflow copies: {stray}"
