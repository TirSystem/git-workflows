"""Offline tests for tools/publish_wiki.py and the publish-wiki workflows."""

import base64
import io
import urllib.error

import pytest
import yaml

from workflow_source import REPO_ROOT, load_publish_module

SCOPED_WORKFLOW = REPO_ROOT / ".gitea" / "scoped_workflows" / "publish-wiki-pages.yml"

API = "https://git.example.test/api/v1"
REPO_URL = f"{API}/repos/TirSystem/repo"
WIKI_URL = f"{REPO_URL}/wiki"


@pytest.fixture()
def publish_wiki():
    return load_publish_module()


def b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


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
    def test_reads_markdown_files_by_stem_and_ignores_other_files(self, publish_wiki, tmp_path):
        (tmp_path / "Home.md").write_bytes(b"home")
        (tmp_path / "Home.da.md").write_bytes(b"hjem")
        (tmp_path / "Notes.txt").write_bytes(b"ignored")
        assert publish_wiki.read_pages(tmp_path) == {"Home": b"home", "Home.da": b"hjem"}

    def test_rejects_a_directory_without_pages_so_the_wiki_is_never_wiped(
        self, publish_wiki, tmp_path
    ):
        with pytest.raises(publish_wiki.WorkflowError, match="no Markdown pages"):
            publish_wiki.read_pages(tmp_path)


class TestPageTitle:
    @pytest.mark.parametrize(
        ("key", "title"), [("Home", "Home"), ("Home-da", "Home da"), ("Getting-Started-ms", "Getting Started ms")]
    )
    def test_a_hyphen_is_sent_as_a_space(self, publish_wiki, key, title):
        # Gitea keeps a hyphen in a title literal (Home-da.-.md, address Home%2Dda).
        assert publish_wiki.page_title(key) == title


class TestPageKey:
    @pytest.mark.parametrize(
        ("name", "key"),
        [("Home", "Home"), ("Home da", "Home-da"), ("Home-da", "Home-da"), ("Home.da", "Home.da"),
         ("AI Prompt Template ms", "AI-Prompt-Template-ms"), ("_Sidebar", "_Sidebar")],
    )
    def test_a_space_and_a_hyphen_are_the_same_page(self, publish_wiki, name, key):
        assert publish_wiki.page_key(name) == key

    def test_file_names_with_spaces_and_hyphens_are_keyed_the_same(self, publish_wiki, tmp_path):
        (tmp_path / "Home da.md").write_bytes(b"hjem")
        (tmp_path / "_Sidebar.md").write_bytes(b"menu")
        assert publish_wiki.read_pages(tmp_path) == {"Home-da": b"hjem", "_Sidebar": b"menu"}

    def test_two_files_for_one_page_are_refused(self, publish_wiki, tmp_path):
        (tmp_path / "Home da.md").write_bytes(b"one")
        (tmp_path / "Home-da.md").write_bytes(b"two")
        with pytest.raises(publish_wiki.WorkflowError, match="name the wiki page Home-da"):
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
            return [{"title": key.replace("-", " "), "sub_url": key} for key in self.wiki]
        if method == "POST" and url == f"{WIKI_URL}/new":
            self.wiki[body["title"].replace(" ", "-")] = body["content_base64"]
            return None
        title = url.rsplit("/", 1)[-1]
        if method == "GET":
            return {"title": title, "content_base64": self.wiki[title]}
        if method == "PATCH":
            assert " " in body["title"] or "-" not in body["title"], body["title"]
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
    monkeypatch.setenv("WIKI_PRUNE", "true")
    monkeypatch.setenv("WIKI_DIR", str(wiki_dir))
    monkeypatch.setenv("GITEA_API_URL", f"{API}/")
    monkeypatch.setenv("SOURCE_REPOSITORY", "TirSystem/repo")
    monkeypatch.setenv("WIKI_CREDENTIALS", "wiki-token")
    return wiki_dir


def run_main(publish_wiki, gitea):
    publish_wiki.request_json = gitea
    return publish_wiki.main()


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
        self, publish_wiki, environment, capsys, monkeypatch
    ):
        monkeypatch.setenv("WIKI_PRUNE", "false")
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


class TestPageIdentity:
    """A wiki that already has pages named with spaces, as Gitea stores them."""

    def test_a_file_named_with_a_space_updates_the_existing_page(
        self, publish_wiki, environment, monkeypatch
    ):
        (environment / "Home.md").unlink()
        (environment / "Credentials.md").unlink()
        monkeypatch.setenv("WIKI_PRUNE", "false")
        (environment / "Home da.md").write_text("hjem v2", encoding="utf-8")
        gitea = FakeGitea(publish_wiki, wiki={"Home-da": b64("hjem v1")})

        assert run_main(publish_wiki, gitea) == 0

        assert gitea.wiki == {"Home-da": b64("hjem v2")}
        assert [call[0] for call in gitea.calls].count("POST") == 0
        assert ("PATCH", f"{WIKI_URL}/page/Home-da") in [(c[0], c[1]) for c in gitea.calls]

    def test_identical_pages_with_spaces_are_a_no_op(self, publish_wiki, environment):
        (environment / "Home.md").unlink()
        (environment / "Credentials.md").unlink()
        (environment / "Home da.md").write_text("hjem", encoding="utf-8")
        (environment / "_Sidebar.md").write_text("menu", encoding="utf-8")
        gitea = FakeGitea(
            publish_wiki, wiki={"Home-da": b64("hjem"), "_Sidebar": b64("menu")}
        )

        assert run_main(publish_wiki, gitea) == 0

        assert gitea.writes == []

    def test_prune_does_not_delete_a_page_that_is_in_the_folder_under_another_spelling(
        self, publish_wiki, environment
    ):
        (environment / "Home.md").unlink()
        (environment / "Credentials.md").unlink()
        (environment / "Install ms.md").write_text("pasang", encoding="utf-8")
        gitea = FakeGitea(
            publish_wiki, wiki={"Install-ms": b64("pasang"), "Old-page": b64("x")}
        )

        assert run_main(publish_wiki, gitea) == 0

        assert gitea.wiki == {"Install-ms": b64("pasang")}

    def test_the_address_wins_over_the_title_and_is_decoded(self, publish_wiki):
        def listing(url, headers=None, **kwargs):
            return [
                {"title": "Whatever", "sub_url": "Real-Address"},
                {"title": "Only title"},
                {"title": "Encoded", "sub_url": "Caf%C3%A9"},
            ]

        keys = publish_wiki.list_wiki_titles(WIKI_URL, {}, listing)

        assert keys == {"Real-Address", "Only-title", "Café"}


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


class TestExplicitPrune:
    """The scoped workflow sets WIKI_PRUNE: the docs/wiki folder is the opt-in."""

    @pytest.fixture()
    def explicit(self, environment, monkeypatch):
        monkeypatch.setenv("WIKI_PRUNE", "false")
        return environment

    @pytest.mark.parametrize(
        ("text", "expected"), [("true", True), (" TRUE\n", True), ("false", False)]
    )
    def test_reads_true_and_false(self, publish_wiki, text, expected):
        assert publish_wiki.parse_prune_setting(text) is expected

    @pytest.mark.parametrize("text", ["", "yes", "prune", None])
    def test_rejects_anything_else(self, publish_wiki, text):
        with pytest.raises(publish_wiki.WorkflowError) as caught:
            publish_wiki.parse_prune_setting(text)
        assert caught.value.category == "configuration"

    def test_publishes_without_a_marker_and_keeps_other_pages(
        self, publish_wiki, explicit, capsys
    ):
        gitea = FakeGitea(publish_wiki, wiki={"Old": b64("hand written")})

        assert run_main(publish_wiki, gitea) == 0

        assert set(gitea.wiki) == {"Old", "Home", "Credentials"}
        assert "set the prune input to true" in capsys.readouterr().out

    def test_prune_true_deletes_pages_outside_the_folder(
        self, publish_wiki, explicit, monkeypatch
    ):
        monkeypatch.setenv("WIKI_PRUNE", "true")
        gitea = FakeGitea(publish_wiki, wiki={"Old": b64("stale")})

        assert run_main(publish_wiki, gitea) == 0

        assert set(gitea.wiki) == {"Home", "Credentials"}

    def test_a_missing_folder_is_a_configuration_error_before_any_request(
        self, publish_wiki, explicit, monkeypatch, tmp_path
    ):
        monkeypatch.setenv("WIKI_DIR", str(tmp_path / "docs" / "wiki"))
        gitea = FakeGitea(publish_wiki)

        with pytest.raises(publish_wiki.WorkflowError, match="WIKI_DIR") as caught:
            run_main(publish_wiki, gitea)

        assert caught.value.category == "configuration"
        assert gitea.calls == []

    def test_an_empty_folder_never_deletes_pages_even_with_prune(
        self, publish_wiki, explicit, monkeypatch
    ):
        monkeypatch.setenv("WIKI_PRUNE", "true")
        for page in explicit.glob("*.md"):
            page.unlink()
        gitea = FakeGitea(publish_wiki, wiki={"Home": b64("home")})

        with pytest.raises(publish_wiki.WorkflowError) as caught:
            run_main(publish_wiki, gitea)

        assert caught.value.category == "configuration"
        assert gitea.writes == []

    def test_a_missing_secret_fails_before_any_request(
        self, publish_wiki, explicit, monkeypatch
    ):
        monkeypatch.setenv("WIKI_CREDENTIALS", "")
        gitea = FakeGitea(publish_wiki)

        with pytest.raises(publish_wiki.WorkflowError, match="TOKEN_FOR_GITEA_WIKI"):
            run_main(publish_wiki, gitea)

        assert gitea.calls == []


class TestScopedWorkflow:
    @pytest.fixture()
    def document(self):
        return yaml.safe_load(SCOPED_WORKFLOW.read_text(encoding="utf-8"))

    @pytest.fixture()
    def steps(self, document):
        return {step.get("id", step["name"]): step for step in document["jobs"]["publish-wiki"]["steps"]}

    def test_runs_on_a_push_to_main_and_by_hand_without_inputs(self, document):
        triggers = document[True]
        assert list(triggers) == ["push", "workflow_dispatch"]
        assert triggers["push"]["branches"] == ["main"]
        assert not triggers["workflow_dispatch"]

    def test_a_push_runs_only_when_docs_wiki_changes(self, document):
        assert document[True]["push"]["paths"] == ["docs/wiki/**"]

    def test_the_token_is_read_from_the_secret_without_a_fallback(self, document):
        text = SCOPED_WORKFLOW.read_text(encoding="utf-8")
        step = document["jobs"]["publish-wiki"]["steps"][-1]
        assert step["env"]["WIKI_CREDENTIALS"] == "${{ secrets.TOKEN_FOR_GITEA_WIKI }}"
        assert "secrets.TOKEN_FOR_GITEA }}" not in text
        assert "github.token" not in text

    def test_job_has_read_only_permissions(self, document):
        assert document["jobs"]["publish-wiki"]["permissions"] == {"contents": "read"}

    def test_the_settings_reach_the_script_through_the_environment(self, document):
        step = document["jobs"]["publish-wiki"]["steps"][-1]
        assert step["env"]["WIKI_DIR"] == "docs/wiki"
        assert step["env"]["WIKI_PRUNE"] == "false"
        assert step["run"] == "python3 shared-scripts/tools/publish_wiki.py"
        assert "inputs." not in step["run"]

    def test_the_script_is_fetched_at_v2(self, steps):
        fetch = steps["Fetch the shared script"]["with"]
        assert fetch["repository"] == "TirSystem/git-workflows"
        assert fetch["ref"] == "v2"

    def test_the_folder_check_decides_whether_the_fetch_and_publish_steps_run(self, steps):
        assert steps["source"]["name"] == "Look for the wiki folder"
        assert "-d docs/wiki" in steps["source"]["run"]
        condition = "steps.source.outputs.found == 'true'"
        assert steps["Fetch the shared script"]["if"] == condition
        assert steps["Publish the pages to the wiki"]["if"] == condition


def test_this_repository_publishes_docs_wiki_through_the_scoped_workflow():
    """The wiki of this repository equals docs/wiki/ (ADR-0009): the folder is the opt-in."""
    assert SCOPED_WORKFLOW.is_file()
    assert not (REPO_ROOT / ".gitea" / "workflows" / "publish-own-wiki.yml").exists()
    assert not (REPO_ROOT / ".gitea" / "workflows" / "publish-wiki-pages.yml").exists()
    assert not (REPO_ROOT / "wiki").exists()
    assert (REPO_ROOT / "docs" / "wiki" / "Home.md").is_file()


def test_the_script_has_no_marker_path():
    """ADR-0009: the marker file is removed."""
    source = (REPO_ROOT / "tools" / "publish_wiki.py").read_text(encoding="utf-8")
    assert "MARKER_NAME" not in source
    assert "parse_marker" not in source
