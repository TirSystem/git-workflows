"""Offline tests for tools/english_comments_report.py and .gitea/workflows/english-comments.yml.

The Gitea API is a fake that records the writes, so no host is contacted.
"""

import io
import json
import urllib.error

import pytest
import yaml

from workflow_source import REPO_ROOT, load_script

report = load_script(REPO_ROOT / "tools" / "english_comments_report.py", "english_comments_report")
WORKFLOW = REPO_ROOT / ".gitea" / "workflows" / "english-comments.yml"
TOKEN = "t" * 40
FINDING = {
    "path": "src/a.py",
    "line": 4,
    "end_line": 4,
    "language": "da",
    "probability": 0.93,
    "text": "Denne funktion beregner totalen",
}


class FakeGitea:
    """Lists the comments of one pull request and records the writes."""

    def __init__(self, comments=()):
        self.comments = list(comments)
        self.writes = []

    def __call__(self, url, method="GET", headers=None, body=None):
        assert headers["Authorization"] == f"token {TOKEN}"
        if method == "GET":
            return self.comments
        self.writes.append((method, url.split("/repos/o/r")[-1], body["body"]))
        return {"id": 99}


@pytest.fixture
def env(tmp_path, monkeypatch):
    findings = tmp_path / "findings.json"
    findings.write_text(json.dumps([FINDING]), encoding="utf-8")
    values = {
        "GITEA_API_URL": "https://git.example/api/v1/",
        "SOURCE_REPOSITORY": "o/r",
        "PR_NUMBER": "7",
        "PR_AUTHOR": "anna",
        "REPORT_TOKEN": TOKEN,
        "FINDINGS_FILE": str(findings),
        "RUN_URL": "https://git.example/o/r/actions/runs/5",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    return findings


def write_findings(path, findings):
    path.write_text(json.dumps(findings), encoding="utf-8")


def test_a_finding_writes_one_comment_that_mentions_the_author(env):
    gitea = FakeGitea()
    assert report.main(request=gitea) == 0
    [(method, path, body)] = gitea.writes
    assert (method, path) == ("POST", "/issues/7/comments")
    assert report.MARKER in body and body.startswith(report.MARKER)
    assert "@anna" in body and "`src/a.py`" in body and "| 4 |" in body
    assert "Denne funktion beregner totalen" in body
    assert "[The run](https://git.example/o/r/actions/runs/5)" in body


def test_a_second_run_updates_the_comment_instead_of_adding_one(env):
    old = {"id": 11, "body": f"{report.MARKER}\nsomething older"}
    gitea = FakeGitea([{"id": 3, "body": "hello"}, old])
    assert report.main(request=gitea) == 0
    [(method, path, _)] = gitea.writes
    assert (method, path) == ("PATCH", "/issues/comments/11")


def test_an_unchanged_comment_is_not_written_again(env):
    body = report.failing_body("anna", [FINDING], "https://git.example/o/r/actions/runs/5")
    gitea = FakeGitea([{"id": 11, "body": body}])
    assert report.main(request=gitea) == 0
    assert gitea.writes == []


def test_a_passing_run_marks_the_comment_resolved_without_a_mention(env):
    write_findings(env, [])
    gitea = FakeGitea([{"id": 11, "body": f"{report.MARKER}\n@anna failing"}])
    assert report.main(request=gitea) == 0
    [(method, path, body)] = gitea.writes
    assert (method, path) == ("PATCH", "/issues/comments/11")
    assert "passes" in body and "@anna" not in body


def test_a_passing_run_with_no_earlier_comment_writes_nothing(env):
    write_findings(env, [])
    gitea = FakeGitea()
    assert report.main(request=gitea) == 0
    assert gitea.writes == []


def test_comments_of_other_authors_are_not_touched(env):
    gitea = FakeGitea([{"id": 3, "body": "no marker here"}])
    report.main(request=gitea)
    assert [w[0] for w in gitea.writes] == ["POST"]


def test_all_pages_of_comments_are_searched(env):
    page = [{"id": n, "body": "x"} for n in range(report.PAGE_SIZE)]
    calls = []

    def paged(url, method="GET", headers=None, body=None):
        if method != "GET":
            calls.append((method, url))
            return None
        number = int(url.rsplit("page=", 1)[1])
        return page if number == 1 else [{"id": 900, "body": report.MARKER}]

    assert report.main(request=paged) == 0
    assert calls == [("PATCH", "https://git.example/api/v1/repos/o/r/issues/comments/900")]


def test_no_token_writes_nothing_and_does_not_fail(env, monkeypatch):
    monkeypatch.setenv("REPORT_TOKEN", "")
    gitea = FakeGitea()
    assert report.main(request=gitea) == 0
    assert gitea.writes == []


def test_a_missing_findings_file_means_the_check_did_not_run(env, monkeypatch):
    monkeypatch.setenv("FINDINGS_FILE", str(env.parent / "absent.json"))
    assert report.main(request=FakeGitea()) == 0


def test_an_unreadable_findings_file_is_a_configuration_error(env, capsys):
    env.write_text("not json", encoding="utf-8")
    assert report.main(request=FakeGitea()) == 1


@pytest.mark.parametrize("name", ["GITEA_API_URL", "PR_NUMBER", "PR_AUTHOR"])
def test_a_missing_setting_is_a_configuration_error(env, monkeypatch, name):
    monkeypatch.delenv(name)
    assert report.main(request=FakeGitea()) == 1


def test_text_in_a_comment_cannot_mention_someone_or_break_the_table():
    body = report.failing_body("anna", [{**FINDING, "text": "ping @bob `x` | y\nz"}])
    assert "@bob" not in body.replace("@​bob", "")
    assert "\\|" in body and "\n| " in body and "`x`" not in body


def test_long_lists_are_cut(env):
    many = [{**FINDING, "line": n} for n in range(report.MAX_ROWS + 5)]
    body = report.failing_body("anna", many)
    assert "...and 5 more" in body
    assert body.count("`src/a.py`") == report.MAX_ROWS


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_request_json_sends_the_body_and_reads_the_answer(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["method"] = request.get_method()
        seen["data"] = request.data
        return FakeResponse(b'{"id": 5}')

    monkeypatch.setattr(report.urllib.request, "urlopen", fake_urlopen)
    assert report.request_json("https://h/x", "POST", {"A": "b"}, {"body": "t"}) == {"id": 5}
    assert seen == {"method": "POST", "data": b'{"body": "t"}'}


def test_request_json_returns_none_for_an_empty_answer(monkeypatch):
    monkeypatch.setattr(report.urllib.request, "urlopen", lambda request, timeout: FakeResponse(b""))
    assert report.request_json("https://h/x") is None


@pytest.mark.parametrize(
    ("code", "category"), [(401, "credentials"), (403, "permissions"), (500, "api")]
)
def test_http_errors_have_a_category(monkeypatch, code, category):
    def fail(request, timeout):
        raise urllib.error.HTTPError(request.full_url, code, "reason", {}, None)

    monkeypatch.setattr(report.urllib.request, "urlopen", fail)
    with pytest.raises(report.ReportError, match=rf"\[{category}\]"):
        report.request_json("https://h/x?token=secret")


def test_an_unreachable_host_is_an_api_error(monkeypatch):
    def fail(request, timeout):
        raise urllib.error.URLError("down")

    monkeypatch.setattr(report.urllib.request, "urlopen", fail)
    with pytest.raises(report.ReportError, match=r"\[api\]"):
        report.request_json("https://h/x")


def test_an_api_error_is_printed_without_the_token_and_fails_the_step(env, monkeypatch, capsys):
    monkeypatch.undo()  # restore print
    for key, value in {
        "GITEA_API_URL": "https://git.example/api/v1",
        "SOURCE_REPOSITORY": "o/r",
        "PR_NUMBER": "7",
        "PR_AUTHOR": "anna",
        "REPORT_TOKEN": TOKEN,
        "FINDINGS_FILE": str(env),
    }.items():
        monkeypatch.setenv(key, value)

    def refuse(url, method="GET", headers=None, body=None):
        raise report.ReportError("permissions", "the token may not comment")

    assert report.main(request=refuse) == 1
    out = capsys.readouterr().out
    assert "::error::[permissions]" in out and TOKEN not in out


@pytest.fixture(scope="module")
def document():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


class TestWorkflow:

    def test_is_a_reusable_workflow_with_the_contract_inputs(self, document):
        call = document[True]["workflow_call"]  # PyYAML reads `on` as True
        assert set(call["inputs"]) == {
            "scope", "exclude", "allowed-words-file", "threshold", "min-words",
            "langid-version", "numpy-version", "tools-ref",
        }
        assert call["inputs"]["threshold"]["default"] == "0.6"
        assert call["inputs"]["min-words"]["default"] == "3"
        assert call["inputs"]["scope"]["default"] == "changed"
        assert call["secrets"]["REPORT_TOKEN"]["required"] is False

    def test_permissions_are_explicit_and_small(self, document):
        permissions = document["jobs"]["english-comments"]["permissions"]
        assert permissions == {"contents": "read", "issues": "write", "pull-requests": "write"}

    def test_checks_out_the_full_history_for_the_merge_base(self, document):
        first = document["jobs"]["english-comments"]["steps"][0]
        assert first["with"]["fetch-depth"] == 0

    def test_the_check_does_not_end_the_job_before_the_author_is_told(self, document):
        steps = {s.get("name"): s for s in document["jobs"]["english-comments"]["steps"]}
        assert steps["Check the comments"]["continue-on-error"] is True
        tell = steps["Tell the author"]
        assert tell["continue-on-error"] is True and "always()" in tell["if"]
        assert "steps.check.outcome == 'failure'" in steps["Fail the run when a comment is not in English"]["if"]

    def test_the_author_step_asks_for_the_pull_request_not_for_the_event_name(self, document):
        # in a called workflow gitea.event_name is workflow_call (seen on the instance, MIL-013 task 8)
        tell = next(s for s in document["jobs"]["english-comments"]["steps"] if s.get("name") == "Tell the author")
        assert "event_name" not in tell["if"]
        assert "gitea.event.pull_request.number != ''" in tell["if"]

    def test_inputs_reach_the_scripts_as_environment_variables_only(self, document):
        for step in document["jobs"]["english-comments"]["steps"]:
            assert "inputs." not in step.get("run", "")
            assert "secrets." not in step.get("run", "")

    def test_the_token_falls_back_to_the_token_of_the_run(self, document):
        tell = next(s for s in document["jobs"]["english-comments"]["steps"] if s.get("name") == "Tell the author")
        assert "secrets.REPORT_TOKEN || gitea.token" in tell["env"]["REPORT_TOKEN"]

    def test_uses_gitea_contexts_only(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        assert "gitea.event.pull_request.user.login" in text
        assert "github." not in text.replace("TirSystem/github-action", "")
