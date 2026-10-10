"""Offline tests for the scoped publish-wiki workflow and its embedded script."""

import base64
import io
import urllib.error

import pytest
import yaml

from workflow_source import PUBLISH_WORKFLOW, REPO_ROOT, load_publish_module

API = "https://git.example.test/api/v1"
REPO_URL = f"{API}/repos/TirSystem/repo"
WIKI_URL = f"{REPO_URL}/wiki"


@pytest.fixture()
def publish_wiki():
    return load_publish_module()


def b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


class TestParseMarker:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [("", False), ("  \n", False), (None, False), ("prune", True), (" prune\n", True)],
    )
    def test_reads_the_empty_marker_and_the_prune_word(self, publish_wiki, text, expected):
        assert publish_wiki.parse_marker(text) is expected

    @pytest.mark.parametrize("text", ["Prune", "prune: true", "delete", "prune\nmore"])
    def test_rejects_anything_else(self, publish_wiki, text):
        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.parse_marker(text)
        assert caught.value.category == "configuration"
        assert "prune" in str(caught.value)


class TestParseGiteaToken:
    def test_returns_the_stripped_token(self, publish_wiki):
        assert publish_wiki.parse_gitea_token(" abc \n") == "abc"

    @pytest.mark.parametrize("raw", [None, "", "  "])
    def test_rejects_missing_or_empty_token(self, publish_wiki, raw):
        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.parse_gitea_token(raw)
        assert caught.value.category == "configuration"
        assert "TOKEN_FOR_GITEA_WIKI is missing or empty" in str(caught.value)


class TestReadPages:
    def test_reads_markdown_files_by_stem_and_ignores_the_marker(self, publish_wiki, tmp_path):
        (tmp_path / "Home.md").write_bytes(b"home")
        (tmp_path / "Home.da.md").write_bytes(b"hjem")
        (tmp_path / ".publish").write_bytes(b"prune")
        (tmp_path / "Notes.txt").write_bytes(b"ignored")
        assert publish_wiki.read_pages(tmp_path) == {"Home": b"home", "Home.da": b"hjem"}

    def test_rejects_a_directory_without_pages_so_the_wiki_is_never_wiped(
        self, publish_wiki, tmp_path
    ):
        (tmp_path / ".publish").write_text("prune", encoding="utf-8")
        with pytest.raises(publish_wiki.WorkflowError, match="no Markdown pages"):
            publish_wiki.read_pages(tmp_path)


class FakeGitea:
    """Answers like the Gitea repository and wiki endpoints."""

    def __init__(self, publish_wiki, wiki=None, has_wiki=True, wiki_initialised=True):
        self.error = publish_wiki.WorkflowError
        self.wiki = dict(wiki or {})
        self.has_wiki = has_wiki
        self.wiki_initialised = wiki_initialised
        self.calls = []

    def __call__(self, url, method="GET", headers=None, body=None):
        self.calls.append((method, url, body, headers))
        if url == REPO_URL:
            return {"has_wiki": self.has_wiki}
        if url.startswith(f"{WIKI_URL}/pages"):
            if not self.wiki_initialised:
                raise self.error("configuration", "404")
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

    @property
    def writes(self):
        return [call for call in self.calls if call[0] != "GET"]


@pytest.fixture()
def environment(monkeypatch, tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "Home.md").write_text("home v2", encoding="utf-8")
    (wiki_dir / "Credentials.md").write_text("credentials", encoding="utf-8")
    (wiki_dir / ".publish").write_text("prune\n", encoding="utf-8")
    monkeypatch.setenv("WIKI_DIR", str(wiki_dir))
    monkeypatch.setenv("GITEA_API_URL", f"{API}/")
    monkeypatch.setenv("SOURCE_REPOSITORY", "TirSystem/repo")
    monkeypatch.setenv("WIKI_CREDENTIALS", "wiki-token")
    return wiki_dir


def run_main(publish_wiki, gitea):
    publish_wiki.request_json = gitea
    return publish_wiki.main()


class TestOptIn:
    def test_a_repository_without_the_marker_is_never_written_to(
        self, publish_wiki, environment, capsys
    ):
        (environment / ".publish").unlink()
        gitea = FakeGitea(publish_wiki, wiki={"Old": b64("hand written")})

        assert run_main(publish_wiki, gitea) == 0

        assert gitea.calls == []
        assert "wiki publishing is not enabled" in capsys.readouterr().out
        assert gitea.wiki == {"Old": b64("hand written")}

    def test_a_repository_without_the_marker_does_not_need_the_secret(
        self, publish_wiki, environment, monkeypatch
    ):
        (environment / ".publish").unlink()
        monkeypatch.setenv("WIKI_CREDENTIALS", "")
        assert run_main(publish_wiki, FakeGitea(publish_wiki)) == 0

    def test_a_repository_without_a_wiki_directory_is_skipped(
        self, publish_wiki, monkeypatch, tmp_path
    ):
        monkeypatch.setenv("WIKI_DIR", str(tmp_path / "missing"))
        monkeypatch.setenv("SOURCE_REPOSITORY", "TirSystem/repo")
        gitea = FakeGitea(publish_wiki)
        assert run_main(publish_wiki, gitea) == 0
        assert gitea.calls == []

    def test_an_opted_in_repository_without_the_secret_fails_before_any_request(
        self, publish_wiki, environment, monkeypatch
    ):
        monkeypatch.setenv("WIKI_CREDENTIALS", "")
        gitea = FakeGitea(publish_wiki)

        with pytest.raises(publish_wiki.WorkflowError, match="TOKEN_FOR_GITEA_WIKI"):
            run_main(publish_wiki, gitea)

        assert gitea.calls == []

    def test_an_unknown_marker_content_is_refused_before_any_request(
        self, publish_wiki, environment
    ):
        (environment / ".publish").write_text("mirror everything", encoding="utf-8")
        gitea = FakeGitea(publish_wiki)

        with pytest.raises(publish_wiki.WorkflowError, match="prune"):
            run_main(publish_wiki, gitea)

        assert gitea.calls == []


class TestPublish:
    def test_prune_creates_updates_and_deletes_to_match_the_source(
        self, publish_wiki, environment, capsys
    ):
        gitea = FakeGitea(
            publish_wiki,
            wiki={"Home": b64("home v1"), "Credentials": b64("credentials"), "Old": b64("x")},
        )

        assert run_main(publish_wiki, gitea) == 0

        assert gitea.wiki == {"Home": b64("home v2"), "Credentials": b64("credentials")}
        methods = [(call[0], call[1].rsplit("/", 1)[-1]) for call in gitea.calls]
        assert ("PATCH", "Home") in methods
        assert ("DELETE", "Old") in methods
        assert ("PATCH", "Credentials") not in methods
        assert "0 created, 1 updated, 1 deleted" in capsys.readouterr().out

    def test_without_prune_pages_outside_the_source_are_kept(
        self, publish_wiki, environment, capsys
    ):
        (environment / ".publish").write_text("", encoding="utf-8")
        gitea = FakeGitea(
            publish_wiki, wiki={"Home": b64("home v1"), "Old": b64("hand written")}
        )

        assert run_main(publish_wiki, gitea) == 0

        assert gitea.wiki["Old"] == b64("hand written")
        assert gitea.wiki["Home"] == b64("home v2")
        assert "Credentials" in gitea.wiki
        assert not [call for call in gitea.calls if call[0] == "DELETE"]
        out = capsys.readouterr().out
        assert "1 created, 1 updated, 0 deleted" in out
        assert "1 page(s) are in the wiki but not in" in out
        assert "prune" in out

    def test_creates_every_page_when_the_wiki_was_never_written(
        self, publish_wiki, environment
    ):
        gitea = FakeGitea(publish_wiki, wiki_initialised=False)

        assert run_main(publish_wiki, gitea) == 0

        assert set(gitea.wiki) == {"Home", "Credentials"}
        assert [call[0] for call in gitea.calls].count("POST") == 2

    def test_does_nothing_when_the_wiki_is_already_current(self, publish_wiki, environment):
        gitea = FakeGitea(
            publish_wiki, wiki={"Home": b64("home v2"), "Credentials": b64("credentials")}
        )

        assert run_main(publish_wiki, gitea) == 0

        assert gitea.writes == []

    def test_sends_the_token_and_never_prints_it(self, publish_wiki, environment, capsys):
        gitea = FakeGitea(publish_wiki)

        assert run_main(publish_wiki, gitea) == 0

        assert {call[3]["Authorization"] for call in gitea.calls} == {"token wiki-token"}
        output = capsys.readouterr()
        assert "wiki-token" not in output.out + output.err

    def test_fails_when_the_wiki_is_not_enabled_and_writes_nothing(
        self, publish_wiki, environment
    ):
        gitea = FakeGitea(publish_wiki, has_wiki=False)

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            run_main(publish_wiki, gitea)

        assert caught.value.category == "configuration"
        assert gitea.writes == []

    def test_an_empty_source_never_deletes_pages_even_with_prune(
        self, publish_wiki, environment
    ):
        for path in environment.glob("*.md"):
            path.unlink()
        gitea = FakeGitea(publish_wiki, wiki={"Home": b64("keep me")})

        with pytest.raises(publish_wiki.WorkflowError, match="no Markdown pages"):
            run_main(publish_wiki, gitea)

        assert gitea.calls == []
        assert gitea.wiki == {"Home": b64("keep me")}


class TestDescribeToken:
    def test_recognises_a_gitea_token_shape(self, publish_wiki):
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
    def test_names_the_likely_mistake_without_echoing_the_token(
        self, publish_wiki, token, expected
    ):
        description = publish_wiki.describe_token(token)
        assert expected in description
        assert token not in description


class TestRejectedToken:
    def test_rejection_adds_the_token_shape_but_not_the_token(
        self, publish_wiki, environment, monkeypatch
    ):
        monkeypatch.setenv("WIKI_CREDENTIALS", "*******")

        def reject(url, method="GET", headers=None, body=None):
            raise publish_wiki.WorkflowError("credentials", "Gitea rejected the token.")

        publish_wiki.request_json = reject

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.main()

        message = str(caught.value)
        assert caught.value.category == "credentials"
        assert "Token shape: 7 characters" in message
        assert "only mask characters" in message
        assert "*******" not in message.split("Token shape:")[0]

    def test_other_categories_are_not_changed(self, publish_wiki, environment):
        def forbid(url, method="GET", headers=None, body=None):
            raise publish_wiki.WorkflowError("permissions", "Forbidden.")

        publish_wiki.request_json = forbid

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.main()

        assert str(caught.value) == "[permissions] Forbidden."


class TestRequestJson:
    @staticmethod
    def raise_http_error(publish_wiki, monkeypatch, code, reason):
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
    def test_categorizes_http_errors(self, publish_wiki, monkeypatch, code, reason, category):
        self.raise_http_error(publish_wiki, monkeypatch, code, reason)

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.request_json(REPO_URL)

        assert caught.value.category == category
        assert f"HTTP {code}" in str(caught.value)
        assert "secret detail" not in str(caught.value)

    def test_reports_unreachable_service_as_api_failure(self, publish_wiki, monkeypatch):
        def fake_urlopen(request, timeout):
            raise urllib.error.URLError("no route")

        monkeypatch.setattr(publish_wiki.urllib.request, "urlopen", fake_urlopen)

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.request_json(REPO_URL)

        assert caught.value.category == "api"


class TestWorkflow:
    @pytest.fixture()
    def document(self):
        return yaml.safe_load(PUBLISH_WORKFLOW.read_text(encoding="utf-8"))

    def test_runs_only_on_main_when_wiki_changes_or_by_hand(self, document):
        triggers = document[True]  # PyYAML reads the key `on` as True
        assert triggers["push"]["branches"] == ["main"]
        assert triggers["push"]["paths"] == ["wiki/**"]
        assert "workflow_dispatch" in triggers

    def test_job_has_read_only_permissions(self, document):
        assert document["jobs"]["publish-wiki"]["permissions"] == {"contents": "read"}

    def test_secret_is_passed_only_through_the_environment_and_has_no_fallback(self, document):
        text = PUBLISH_WORKFLOW.read_text(encoding="utf-8")
        assert "secrets.TOKEN_FOR_GITEA }}" not in text
        publish_step = document["jobs"]["publish-wiki"]["steps"][-1]
        assert publish_step["env"]["WIKI_CREDENTIALS"] == "${{ secrets.TOKEN_FOR_GITEA_WIKI }}"
        assert "secrets" not in publish_step["run"]

    def test_the_workflow_has_one_source_and_needs_nothing_from_tools(self):
        assert not (REPO_ROOT / ".gitea" / "workflows" / "publish-wiki.yml").exists()
        assert not (REPO_ROOT / "tools" / "publish_wiki.py").exists()
        script = PUBLISH_WORKFLOW.read_text(encoding="utf-8").split("python3 - <<'PY'", 1)[1]
        assert "tools/" not in script


def test_this_repository_opts_in_and_prunes():
    """The wiki of this repository must equal wiki/ (ADR-0001, ADR-0004)."""
    marker = REPO_ROOT / "wiki" / ".publish"
    assert marker.read_text(encoding="utf-8").strip() == "prune"
