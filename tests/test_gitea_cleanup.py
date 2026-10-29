"""Offline tests for tools/gitea_cleanup.py: a fake API, no network and no deletion."""

import io
import json
import urllib.error

import pytest

from workflow_source import REPO_ROOT, load_script

BASE = "https://git.example.test/api/v1/repos/TirSystem/repo"


@pytest.fixture()
def cleanup():
    return load_script(REPO_ROOT / "tools" / "gitea_cleanup.py", "gitea_cleanup")


@pytest.fixture()
def env_file(tmp_path):
    path = tmp_path / ".env"
    path.write_text('TOKEN_FOR_GITEA_WIKI="wiki-secret"\nTOKEN_FOR_GITEA_REPO=repo-secret\n', encoding="utf-8")
    return str(path)


class FakeApi:
    """Records every call and answers the two list requests."""

    def __init__(self, pages=(), releases=()):
        self.calls = []
        # Gitea shows the title of Home-da as "Home da"; the page name is the sub_url.
        self.pages = [{"title": title.replace("-", " "), "sub_url": title} for title in pages]
        self.releases = [{"tag_name": tag, "id": index} for index, tag in enumerate(releases, start=1)]

    def __call__(self, method, url, token):
        self.calls.append((method, url, token))
        if method == "GET" and "/wiki/pages" in url:
            return self.pages
        if method == "GET" and "/releases" in url:
            return self.releases
        return None

    def deletes(self):
        return [url for method, url, _ in self.calls if method == "DELETE"]


def run(cleanup, env_file, *extra):
    return cleanup.main(["--api", "https://git.example.test/api/v1", "--repo", "repo", "--env-file", env_file, *extra])


class TestReadToken:
    def test_returns_the_value_without_quotes(self, cleanup, env_file):
        assert cleanup.read_token(env_file, "TOKEN_FOR_GITEA_WIKI") == "wiki-secret"
        assert cleanup.read_token(env_file, "TOKEN_FOR_GITEA_REPO") == "repo-secret"

    def test_a_missing_name_exits_without_printing_the_file(self, cleanup, env_file):
        with pytest.raises(SystemExit) as caught:
            cleanup.read_token(env_file, "TOKEN_FOR_GITEA_NOPE")
        assert "TOKEN_FOR_GITEA_NOPE is missing" in str(caught.value)
        assert "secret" not in str(caught.value)


class TestCall:
    def test_returns_the_decoded_json(self, cleanup, monkeypatch):
        seen = {}

        def urlopen(request):
            seen["method"] = request.get_method()
            seen["auth"] = request.get_header("Authorization")
            return io.BytesIO(json.dumps([{"a": 1}]).encode())

        monkeypatch.setattr(cleanup.urllib.request, "urlopen", urlopen)
        assert cleanup.call("GET", BASE, "tok") == [{"a": 1}]
        assert seen == {"method": "GET", "auth": "token tok"}

    def test_an_empty_body_returns_none(self, cleanup, monkeypatch):
        monkeypatch.setattr(cleanup.urllib.request, "urlopen", lambda request: io.BytesIO(b""))
        assert cleanup.call("DELETE", BASE, "tok") is None

    def test_an_http_error_exits_and_names_the_status_not_the_token(self, cleanup, monkeypatch):
        def urlopen(request):
            raise urllib.error.HTTPError(BASE, 403, "Forbidden", {}, io.BytesIO(b""))

        monkeypatch.setattr(cleanup.urllib.request, "urlopen", urlopen)
        with pytest.raises(SystemExit) as caught:
            cleanup.call("GET", BASE, "tok-secret")
        assert "HTTP 403" in str(caught.value)
        assert "tok-secret" not in str(caught.value)


class TestSelection:
    def test_only_pages_whose_renamed_page_exists_are_listed(self, cleanup):
        titles = ["Home", "Home.da", "Home-da", "Upgrading.ms", "Orphan.da", "Orphan", "_Sidebar", "Upgrading-ms"]
        assert cleanup.renamed_wiki_pages(titles) == ["Home.da", "Upgrading.ms"]

    def test_the_newest_and_the_kept_tags_stay(self, cleanup):
        releases = [{"tag_name": tag} for tag in ("v3", "v2", "v1", "v0")]
        assert [r["tag_name"] for r in cleanup.old_releases(releases, 2, {"v0"})] == ["v1"]

    def test_keeping_nothing_deletes_every_release(self, cleanup):
        releases = [{"tag_name": "v1"}, {"tag_name": "v0"}]
        assert len(cleanup.old_releases(releases, 0, set())) == 2


class TestMain:
    def test_a_dry_run_lists_and_deletes_nothing(self, cleanup, env_file, monkeypatch, capsys):
        api = FakeApi(pages=["Home", "Home.da", "Home-da"], releases=["v2", "v1"])
        monkeypatch.setattr(cleanup, "call", api)
        assert run(cleanup, env_file, "--wiki-renamed", "--releases") == 0
        out = capsys.readouterr().out
        assert "DRY RUN" in out and "Home.da" in out and "v1" in out
        assert api.deletes() == []
        assert "secret" not in out

    def test_apply_deletes_the_renamed_pages_with_the_wiki_token(self, cleanup, env_file, monkeypatch):
        api = FakeApi(pages=["Home", "Home.da", "Home-da"])
        monkeypatch.setattr(cleanup, "call", api)
        assert run(cleanup, env_file, "--wiki-renamed", "--apply") == 0
        assert api.deletes() == [f"{BASE}/wiki/page/Home.da"]
        assert {token for method, _, token in api.calls if method == "DELETE"} == {"wiki-secret"}

    def test_apply_deletes_old_release_pages_and_never_a_tag(self, cleanup, env_file, monkeypatch):
        api = FakeApi(releases=["v2", "v1", "v0"])
        monkeypatch.setattr(cleanup, "call", api)
        assert run(cleanup, env_file, "--releases", "--keep-latest", "1", "--keep", "v0", "--apply") == 0
        assert api.deletes() == [f"{BASE}/releases/2"]
        assert not any("/tags/" in url for url in api.deletes())

    def test_a_branch_is_deleted_only_with_apply(self, cleanup, env_file, monkeypatch):
        commands = []
        monkeypatch.setattr(cleanup.subprocess, "run", lambda cmd, check: commands.append(cmd))
        run(cleanup, env_file, "--branch", "old", "--clone", "/clone")
        assert commands == []
        run(cleanup, env_file, "--branch", "old", "--clone", "/clone", "--apply")
        assert commands == [["git", "-C", "/clone", "branch", "-D", "old"]]

    def test_nothing_chosen_is_a_usage_error(self, cleanup, env_file):
        with pytest.raises(SystemExit) as caught:
            run(cleanup, env_file)
        assert caught.value.code == 2

    def test_a_branch_without_a_clone_is_a_usage_error(self, cleanup, env_file):
        with pytest.raises(SystemExit) as caught:
            run(cleanup, env_file, "--branch", "old")
        assert caught.value.code == 2
