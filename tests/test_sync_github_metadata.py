"""Offline tests for the Python embedded in sync-github-metadata.yml."""

import io
import json
import urllib.error

import pytest

from workflow_source import load_sync_module


@pytest.fixture()
def sync():
    return load_sync_module()


class TestGithubToken:
    def test_returns_stripped_token_from_json_object(self, sync):
        raw = json.dumps({"GITHUB_PAT": "  ghp_abc  "})
        assert sync["parse_github_token"](raw) == "ghp_abc"

    @pytest.mark.parametrize("raw", [None, "", "   "])
    def test_rejects_missing_or_empty_value(self, sync, raw):
        with pytest.raises(RuntimeError, match="missing or empty"):
            sync["parse_github_token"](raw)

    def test_rejects_invalid_json(self, sync):
        with pytest.raises(RuntimeError, match="valid JSON"):
            sync["parse_github_token"]("ghp_plain_token")

    def test_rejects_json_that_is_not_an_object(self, sync):
        with pytest.raises(RuntimeError, match="JSON object"):
            sync["parse_github_token"]('["x"]')

    @pytest.mark.parametrize("value", [{}, {"GITHUB_PAT": ""}, {"GITHUB_PAT": 5}])
    def test_rejects_missing_or_invalid_pat(self, sync, value):
        with pytest.raises(RuntimeError, match="GITHUB_PAT"):
            sync["parse_github_token"](json.dumps(value))


class TestGiteaToken:
    def test_accepts_bare_token(self, sync):
        assert sync["parse_gitea_token"]("abc123") == "abc123"

    def test_accepts_json_object(self, sync):
        assert sync["parse_gitea_token"]('{"GITEA_TOKEN": " t "}') == "t"

    def test_accepts_json_string(self, sync):
        assert sync["parse_gitea_token"]('"quoted"') == "quoted"

    @pytest.mark.parametrize("raw", [None, "", "  "])
    def test_rejects_missing_or_empty_value(self, sync, raw):
        with pytest.raises(RuntimeError, match="missing or empty"):
            sync["parse_gitea_token"](raw)

    @pytest.mark.parametrize("raw", ["{}", '{"GITEA_TOKEN": ""}', "12", "[]"])
    def test_rejects_value_without_token(self, sync, raw):
        with pytest.raises(RuntimeError, match="GITEA_TOKEN"):
            sync["parse_gitea_token"](raw)


class TestSplitRepository:
    def test_splits_owner_and_repo(self, sync):
        assert sync["split_repository"]("TirSystem/github-action") == (
            "TirSystem",
            "github-action",
        )

    @pytest.mark.parametrize("value", [None, "", "owner", "/repo", "owner/"])
    def test_rejects_incomplete_names(self, sync, value):
        with pytest.raises(RuntimeError, match="source repository"):
            sync["split_repository"](value)


class TestFindGithubTargets:
    @pytest.mark.parametrize(
        "address",
        [
            "git@github.com:Org/repo.git",
            "https://github.com/Org/repo.git",
            "https://user:token@github.com/Org/repo",
            "ssh://git@github.com/Org/repo.git",
        ],
    )
    def test_extracts_owner_and_repo(self, sync, address):
        mirrors = [{"remote_address": address}]
        assert sync["find_github_targets"](mirrors) == ("Org", "repo")

    def test_ignores_non_github_mirrors(self, sync):
        mirrors = [
            {"remote_address": "https://gitlab.com/Org/other.git"},
            {"remote_address": "https://github.com/Org/repo.git"},
        ]
        assert sync["find_github_targets"](mirrors) == ("Org", "repo")

    @pytest.mark.parametrize(
        "mirrors",
        [
            [],
            [{"remote_address": "https://gitlab.com/Org/other.git"}],
        ],
    )
    def test_fails_when_no_github_mirror_exists(self, sync, mirrors):
        with pytest.raises(RuntimeError, match="found 0"):
            sync["find_github_targets"](mirrors)

    def test_fails_when_several_github_mirrors_exist(self, sync):
        mirrors = [
            {"remote_address": "https://github.com/Org/one.git"},
            {"remote_address": "https://github.com/Org/two.git"},
        ]
        with pytest.raises(RuntimeError, match="found 2"):
            sync["find_github_targets"](mirrors)

    def test_fails_when_path_has_wrong_shape(self, sync):
        mirrors = [{"remote_address": "https://github.com/only-owner"}]
        with pytest.raises(RuntimeError, match="owner and repository"):
            sync["find_github_targets"](mirrors)


class TestRequestJson:
    @staticmethod
    def raise_http_error(sync, monkeypatch, code, reason):
        def fake_urlopen(request, timeout):
            raise urllib.error.HTTPError(
                request.full_url, code, reason, {}, io.BytesIO(b"secret detail")
            )

        monkeypatch.setattr(sync["urllib"].request, "urlopen", fake_urlopen)

    @pytest.mark.parametrize(
        ("code", "reason", "category"),
        [
            (401, "Unauthorized", "credentials"),
            (403, "Forbidden", "permissions"),
            (404, "Not Found", "configuration"),
            (500, "Server Error", "api"),
        ],
    )
    def test_categorizes_http_errors(self, sync, monkeypatch, code, reason, category):
        self.raise_http_error(sync, monkeypatch, code, reason)
        with pytest.raises(sync["WorkflowError"]) as caught:
            sync["request_json"]("https://example.test/x")
        assert caught.value.category == category
        assert str(caught.value).startswith(f"[{category}] Gitea API request failed")
        assert f"HTTP {code} ({reason})" in str(caught.value)

    def test_does_not_leak_the_response_body(self, sync, monkeypatch):
        self.raise_http_error(sync, monkeypatch, 403, "Forbidden")
        with pytest.raises(RuntimeError) as caught:
            sync["request_json"]("https://example.test/x")
        assert "secret detail" not in str(caught.value)

    def test_names_github_for_github_urls(self, sync, monkeypatch):
        self.raise_http_error(sync, monkeypatch, 401, "Unauthorized")
        with pytest.raises(RuntimeError, match="GitHub API request failed"):
            sync["request_json"]("https://api.github.com/repos/Org/repo")

    def test_reports_unreachable_service_as_api_failure(self, sync, monkeypatch):
        def fake_urlopen(request, timeout):
            raise urllib.error.URLError("name resolution failed")

        monkeypatch.setattr(sync["urllib"].request, "urlopen", fake_urlopen)
        with pytest.raises(sync["WorkflowError"]) as caught:
            sync["request_json"]("https://example.test/x")
        assert caught.value.category == "api"
        assert "unreachable" in str(caught.value)


class TestWorkflowError:
    def test_configuration_errors_carry_their_category(self, sync):
        with pytest.raises(sync["WorkflowError"]) as caught:
            sync["parse_github_token"]("")
        assert caught.value.category == "configuration"
        assert str(caught.value).startswith("[configuration] ")


class FakeApi:
    """Records calls and answers like the Gitea and GitHub REST APIs."""

    def __init__(self, mirrors, source=None, github=None):
        self.mirrors = mirrors
        self.github = github if github is not None else {"permissions": {"admin": True}}
        self.source = source or {"description": "Desc", "topics": ["a", "b"]}
        self.calls = []

    def __call__(self, url, method="GET", headers=None, body=None):
        self.calls.append((method, url, headers, body))
        if url.endswith("/push_mirrors"):
            return self.mirrors
        if url.startswith("https://git.example.test"):
            return self.source
        if method == "GET" and url.startswith("https://api.github.com"):
            return self.github
        return None


@pytest.fixture()
def environment(monkeypatch):
    monkeypatch.setenv("GITEA_API_URL", "https://git.example.test/api/v1/")
    monkeypatch.setenv("GITEA_CREDENTIALS", "gitea-token")
    monkeypatch.setenv("SOURCE_REPOSITORY", "TirSystem/repo")
    monkeypatch.setenv("GITHUB_CREDENTIALS", json.dumps({"GITHUB_PAT": "gh-token"}))


class TestMain:
    def test_syncs_description_and_topics_to_the_single_github_mirror(
        self, sync, environment, capsys
    ):
        api = FakeApi([{"remote_address": "git@github.com:Org/repo.git"}])
        sync["request_json"] = api

        assert sync["main"]() == 0

        requests = [(call[0], call[1]) for call in api.calls]
        assert requests == [
            ("GET", "https://git.example.test/api/v1/repos/TirSystem/repo"),
            ("GET", "https://git.example.test/api/v1/repos/TirSystem/repo/push_mirrors"),
            ("GET", "https://api.github.com/repos/Org/repo"),
            ("PATCH", "https://api.github.com/repos/Org/repo"),
            ("PUT", "https://api.github.com/repos/Org/repo/topics"),
        ]
        assert api.calls[0][2]["Authorization"] == "token gitea-token"
        assert api.calls[2][2]["Authorization"] == "Bearer gh-token"
        assert api.calls[3][3] == {"description": "Desc"}
        assert api.calls[4][3] == {"names": ["a", "b"]}
        assert "Synced description and topics to Org/repo." in capsys.readouterr().out

    def test_sends_empty_values_when_gitea_has_none(self, sync, environment):
        api = FakeApi(
            [{"remote_address": "git@github.com:Org/repo.git"}],
            source={"description": None, "topics": None},
        )
        sync["request_json"] = api

        sync["main"]()

        assert api.calls[3][3] == {"description": ""}
        assert api.calls[4][3] == {"names": []}

    def test_skips_with_a_warning_when_mirror_list_is_invalid(
        self, sync, environment, capsys
    ):
        api = FakeApi({"message": "unexpected"})
        sync["request_json"] = api

        assert sync["main"]() == 0

        assert all(call[0] == "GET" for call in api.calls)
        assert "WARNING" in capsys.readouterr().out

    def test_fails_before_any_request_when_credentials_are_missing(
        self, sync, environment, monkeypatch
    ):
        monkeypatch.setenv("GITHUB_CREDENTIALS", "")
        api = FakeApi([])
        sync["request_json"] = api

        with pytest.raises(RuntimeError, match="CREDENTIALS_FOR_GITHUB"):
            sync["main"]()
        assert api.calls == []

    def test_stops_before_any_change_when_github_token_cannot_administer(
        self, sync, environment
    ):
        api = FakeApi(
            [{"remote_address": "git@github.com:Org/repo.git"}],
            github={"permissions": {"admin": False, "push": True}},
        )
        sync["request_json"] = api

        with pytest.raises(sync["WorkflowError"]) as caught:
            sync["main"]()

        assert caught.value.category == "permissions"
        assert all(call[0] == "GET" for call in api.calls)

    def test_does_not_print_any_secret(self, sync, environment, capsys):
        api = FakeApi([{"remote_address": "git@github.com:Org/repo.git"}])
        sync["request_json"] = api

        sync["main"]()

        output = capsys.readouterr()
        assert "gh-token" not in output.out + output.err
        assert "gitea-token" not in output.out + output.err
