"""Offline tests for tools/release.py and .gitea/workflows/release.yml."""

import pytest
import yaml

from workflow_source import REPO_ROOT, load_script

release = load_script(REPO_ROOT / "tools" / "release.py", "release")
WORKFLOW = REPO_ROOT / ".gitea" / "workflows" / "release.yml"

SHA = "a" * 40
CONTEXT = "Validate workflows / validate (push)"

CHANGELOG = """# Changelog

## [Unreleased]

### Added

- Something later.

## [1.1.0] - 2026-11-01

### Added

- A workflow.

## [1.0.0] - 2026-10-20

### Added

- First release.
"""


class FakeGitea:
    """Answers the calls of the release script and records the writes."""

    def __init__(self, tip=SHA, status="success", tags=(), context=CONTEXT):
        self.tip = tip
        self.status = status
        self.tags = list(tags)
        self.context = context
        self.writes = []

    def __call__(self, url, method="GET", headers=None, body=None):
        path = url.split("?")[0]
        if method != "GET":
            self.writes.append((method, path.rsplit("/repos/o/r", 1)[-1], body))
            return None
        if path.endswith("/branches/main"):
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
    gitea = FakeGitea(tags=[])
    assert run(gitea) == 0
    assert [(m, p) for m, p, _ in gitea.writes] == [("POST", "/releases"), ("POST", "/tags")]


def test_failed_validation_run_creates_no_tag(env):
    gitea = FakeGitea(status="failure")
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert error.value.category == "validation"
    assert gitea.writes == []


def test_missing_validation_run_creates_no_tag(env):
    gitea = FakeGitea(status=None)
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
    assert "No validation run" in str(error.value)
    assert gitea.writes == []


def test_commit_that_is_not_the_tip_is_refused(env):
    gitea = FakeGitea(tip="b" * 40)
    with pytest.raises(release.WorkflowError) as error:
        run(gitea)
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
    assert "Dry run" in capsys.readouterr().out


@pytest.mark.parametrize("version", ["v1.0.0", "1.0", "1.0.0-rc1", ""])
def test_malformed_version_is_a_configuration_error(env, version):
    env.setenv("RELEASE_VERSION", version)
    with pytest.raises(release.WorkflowError) as error:
        run(FakeGitea())
    assert error.value.category == "configuration"


def test_missing_token_is_a_configuration_error(env):
    env.setenv("RELEASE_CREDENTIALS", "  ")
    with pytest.raises(release.WorkflowError) as error:
        run(FakeGitea())
    assert error.value.category == "configuration"


def test_workflow_runs_the_file_and_defaults_to_a_dry_run():
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    triggers = data.get("on", data.get(True))
    inputs = triggers["workflow_dispatch"]["inputs"]
    assert inputs["dry_run"]["default"] == "true"
    job = data["jobs"]["release"]
    assert job["permissions"] == {"contents": "write"}
    runs = [step.get("run", "") for step in job["steps"]]
    assert "python3 tools/release.py" in runs
