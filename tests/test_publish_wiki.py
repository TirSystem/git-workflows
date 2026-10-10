"""Offline tests for tools/publish_wiki.py and its workflow."""

import base64
import importlib.util
import io
import json
import urllib.error
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".gitea" / "workflows" / "publish-wiki.yml"
_SPEC = importlib.util.spec_from_file_location(
    "publish_wiki", REPO_ROOT / "tools" / "publish_wiki.py"
)
assert _SPEC is not None and _SPEC.loader is not None
publish_wiki = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(publish_wiki)

API = "https://git.example.test/api/v1"
REPO_URL = f"{API}/repos/TirSystem/repo"
WIKI_URL = f"{REPO_URL}/wiki"


def b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


class TestParseGiteaToken:
    def test_accepts_bare_token(self):
        assert publish_wiki.parse_gitea_token(" abc ") == "abc"

    def test_accepts_json_object_and_string(self):
        assert publish_wiki.parse_gitea_token('{"GITEA_TOKEN": "abc"}') == "abc"
        assert publish_wiki.parse_gitea_token('"abc"') == "abc"

    @pytest.mark.parametrize("raw", [None, "", "  ", "{}", '{"GITEA_TOKEN": ""}', "[1]"])
    def test_rejects_missing_or_empty_token(self, raw):
        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.parse_gitea_token(raw)
        assert caught.value.category == "configuration"
        assert "TOKEN_FOR_GITEA" in str(caught.value) or "wiki token" in str(caught.value)


class TestReadPages:
    def test_reads_markdown_files_by_stem(self, tmp_path):
        (tmp_path / "Home.md").write_bytes(b"home")
        (tmp_path / "Notes.txt").write_bytes(b"ignored")
        assert publish_wiki.read_pages(tmp_path) == {"Home": b"home"}

    def test_rejects_missing_directory(self, tmp_path):
        with pytest.raises(publish_wiki.WorkflowError, match="missing"):
            publish_wiki.read_pages(tmp_path / "nope")

    def test_rejects_empty_directory_so_the_wiki_is_never_wiped(self, tmp_path):
        with pytest.raises(publish_wiki.WorkflowError, match="no Markdown pages"):
            publish_wiki.read_pages(tmp_path)


class FakeGitea:
    """Answers like the Gitea repository and wiki endpoints."""

    def __init__(self, wiki=None, has_wiki=True, wiki_initialised=True):
        self.wiki = dict(wiki or {})
        self.has_wiki = has_wiki
        self.wiki_initialised = wiki_initialised
        self.calls = []

    def __call__(self, url, method="GET", headers=None, body=None):
        self.calls.append((method, url, body))
        if url == REPO_URL:
            return {"has_wiki": self.has_wiki}
        if url.startswith(f"{WIKI_URL}/pages"):
            if not self.wiki_initialised:
                raise publish_wiki.WorkflowError("configuration", "404")
            return [{"title": title} for title in self.wiki]
        if method == "POST" and url == f"{WIKI_URL}/new":
            self.wiki[body["title"]] = body["content_base64"]
            return None
        title = url.rsplit("/", 1)[-1]
        if method == "GET":
            return {"title": title, "content_base64": self.wiki[title]}
        if method == "PATCH":
            self.wiki[title] = body["content_base64"]
            return None
        if method == "DELETE":
            del self.wiki[title]
            return None
        raise AssertionError(f"unexpected request {method} {url}")


@pytest.fixture()
def environment(monkeypatch, tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "Home.md").write_text("home v2", encoding="utf-8")
    (wiki_dir / "Credentials.md").write_text("credentials", encoding="utf-8")
    monkeypatch.setenv("WIKI_DIR", str(wiki_dir))
    monkeypatch.setenv("GITEA_API_URL", f"{API}/")
    monkeypatch.setenv("SOURCE_REPOSITORY", "TirSystem/repo")
    monkeypatch.setenv("WIKI_CREDENTIALS", "wiki-token")
    return wiki_dir


def run_main(monkeypatch, gitea):
    monkeypatch.setattr(publish_wiki, "request_json", gitea)
    return publish_wiki.main()


class TestMain:
    def test_creates_updates_and_deletes_to_match_the_source(
        self, monkeypatch, environment, capsys
    ):
        gitea = FakeGitea(
            wiki={"Home": b64("home v1"), "Credentials": b64("credentials"), "Old": b64("x")}
        )

        assert run_main(monkeypatch, gitea) == 0

        assert gitea.wiki == {"Home": b64("home v2"), "Credentials": b64("credentials")}
        methods = [(call[0], call[1].rsplit("/", 1)[-1]) for call in gitea.calls]
        assert ("PATCH", "Home") in methods
        assert ("DELETE", "Old") in methods
        assert ("PATCH", "Credentials") not in methods
        assert "0 created, 1 updated, 1 deleted" in capsys.readouterr().out

    def test_creates_every_page_when_the_wiki_was_never_written(
        self, monkeypatch, environment
    ):
        gitea = FakeGitea(wiki_initialised=False)

        assert run_main(monkeypatch, gitea) == 0

        assert set(gitea.wiki) == {"Home", "Credentials"}
        assert [call[0] for call in gitea.calls].count("POST") == 2

    def test_does_nothing_when_the_wiki_is_already_current(self, monkeypatch, environment):
        gitea = FakeGitea(wiki={"Home": b64("home v2"), "Credentials": b64("credentials")})

        assert run_main(monkeypatch, gitea) == 0

        assert all(call[0] == "GET" for call in gitea.calls)

    def test_sends_the_token_and_never_prints_it(self, monkeypatch, environment, capsys):
        seen = []

        class Recording(FakeGitea):
            def __call__(self, url, method="GET", headers=None, body=None):
                seen.append(headers["Authorization"])
                return super().__call__(url, method, headers, body)

        assert run_main(monkeypatch, Recording()) == 0

        assert set(seen) == {"token wiki-token"}
        output = capsys.readouterr()
        assert "wiki-token" not in output.out + output.err

    def test_fails_when_the_wiki_is_not_enabled(self, monkeypatch, environment):
        gitea = FakeGitea(has_wiki=False)

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            run_main(monkeypatch, gitea)

        assert caught.value.category == "configuration"
        assert all(call[0] == "GET" for call in gitea.calls)

    def test_fails_before_any_request_when_the_secret_is_missing(
        self, monkeypatch, environment
    ):
        monkeypatch.setenv("WIKI_CREDENTIALS", "")
        gitea = FakeGitea()

        with pytest.raises(publish_wiki.WorkflowError, match="No token for the wiki"):
            run_main(monkeypatch, gitea)

        assert gitea.calls == []

    def test_fails_before_any_request_when_the_source_is_empty(
        self, monkeypatch, environment
    ):
        for path in environment.glob("*.md"):
            path.unlink()
        gitea = FakeGitea(wiki={"Home": b64("keep me")})

        with pytest.raises(publish_wiki.WorkflowError, match="no Markdown pages"):
            run_main(monkeypatch, gitea)

        assert gitea.calls == []
        assert gitea.wiki == {"Home": b64("keep me")}


class TestDescribeToken:
    def test_recognises_a_gitea_token_shape(self):
        description = publish_wiki.describe_token("a1b2c3d4e5" * 4)
        assert "40 characters" in description
        assert "looks like a Gitea token" in description

    @pytest.mark.parametrize(
        ("token", "expected"),
        [
            ("*******", "only mask characters"),
            ("TOKEN_FOR_GITEA_WIKI=" + "a" * 40, "contains '='"),
            ('"' + "a" * 40 + '"', "quote character"),
            ("abc def", "whitespace"),
        ],
    )
    def test_names_the_likely_mistake_without_echoing_the_token(self, token, expected):
        description = publish_wiki.describe_token(token)
        assert expected in description
        assert token not in description


class TestRejectedToken:
    def test_rejection_adds_the_token_shape_but_not_the_token(self, monkeypatch, environment):
        monkeypatch.setenv("WIKI_CREDENTIALS", "*******")

        def reject(url, method="GET", headers=None, body=None):
            raise publish_wiki.WorkflowError("credentials", "Gitea rejected the token.")

        monkeypatch.setattr(publish_wiki, "request_json", reject)

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.main()

        message = str(caught.value)
        assert caught.value.category == "credentials"
        assert "Token shape: 7 characters" in message
        assert "only mask characters" in message
        assert "*******" not in message.split("Token shape:")[0]

    def test_other_categories_are_not_changed(self, monkeypatch, environment):
        def forbid(url, method="GET", headers=None, body=None):
            raise publish_wiki.WorkflowError("permissions", "Forbidden.")

        monkeypatch.setattr(publish_wiki, "request_json", forbid)

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.main()

        assert str(caught.value) == "[permissions] Forbidden."


class TestRequestJson:
    @staticmethod
    def raise_http_error(monkeypatch, code, reason):
        def fake_urlopen(request, timeout):
            raise urllib.error.HTTPError(
                request.full_url, code, reason, {}, io.BytesIO(b"secret detail")
            )

        monkeypatch.setattr(publish_wiki.urllib.request, "urlopen", fake_urlopen)

    @pytest.mark.parametrize(
        ("code", "reason", "category"),
        [
            (401, "Unauthorized", "credentials"),
            (403, "Forbidden", "permissions"),
            (404, "Not Found", "configuration"),
            (500, "Server Error", "api"),
        ],
    )
    def test_categorizes_http_errors(self, monkeypatch, code, reason, category):
        self.raise_http_error(monkeypatch, code, reason)

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.request_json(REPO_URL)

        assert caught.value.category == category
        assert f"HTTP {code}" in str(caught.value)
        assert "secret detail" not in str(caught.value)

    def test_reports_unreachable_service_as_api_failure(self, monkeypatch):
        def fake_urlopen(request, timeout):
            raise urllib.error.URLError("no route")

        monkeypatch.setattr(publish_wiki.urllib.request, "urlopen", fake_urlopen)

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.request_json(REPO_URL)

        assert caught.value.category == "api"


class TestWorkflow:
    @pytest.fixture()
    def document(self):
        return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))

    def test_runs_only_on_main_when_wiki_changes_or_by_hand(self, document):
        triggers = document[True]  # PyYAML reads the key `on` as True
        assert triggers["push"]["branches"] == ["main"]
        assert triggers["push"]["paths"] == ["wiki/**"]
        assert "workflow_dispatch" in triggers

    def test_job_has_read_only_permissions(self, document):
        job = document["jobs"]["publish-wiki"]
        assert job["permissions"] == {"contents": "read"}

    def test_checks_the_pages_before_publishing_them(self, document):
        runs = [step.get("run", "") for step in document["jobs"]["publish-wiki"]["steps"]]
        assert runs.index("python3 tools/build_wiki.py --check") < runs.index(
            "python3 tools/publish_wiki.py"
        )

    def test_secret_is_passed_only_through_the_environment(self, document):
        text = WORKFLOW.read_text(encoding="utf-8")
        assert text.count("secrets.TOKEN_FOR_GITEA_WIKI") == 1
        steps = document["jobs"]["publish-wiki"]["steps"]
        publish_step = steps[-1]
        assert publish_step["env"]["WIKI_CREDENTIALS"] == (
            "${{ secrets.TOKEN_FOR_GITEA_WIKI || secrets.TOKEN_FOR_GITEA }}"
        )
        assert "secrets" not in publish_step["run"]
