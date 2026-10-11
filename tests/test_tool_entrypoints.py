"""Offline tests for the parts of tools/ that the flow tests do not reach.

The flow tests of each tool replace its HTTP function with a fake, so the real
`request_json` of the three API tools and the command-line entry point of each
tool are tested here: the reply that is parsed, the HTTP error that is named by
category, and the exit code and message of a run as a process.
"""

import io
import json
import subprocess
import sys
import urllib.error

import pytest

from workflow_source import REPO_ROOT, load_script

TOOLS = REPO_ROOT / "tools"

changelog = load_script(TOOLS / "changelog.py", "changelog_entry")
build_wiki = load_script(TOOLS / "build_wiki.py", "build_wiki_entry")
release = load_script(TOOLS / "release.py", "release_entry")
publish = load_script(TOOLS / "publish_wiki.py", "publish_wiki_entry")
sync = load_script(TOOLS / "sync_github_metadata.py", "sync_entry")

API_TOOLS = pytest.mark.parametrize(
    "tool", [release, publish, sync], ids=["release", "publish_wiki", "sync_github_metadata"]
)


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self) -> bytes:
        return self._body


def http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://git.example/api", code, "reason", {}, io.BytesIO(b""))


@pytest.fixture()
def urlopen(monkeypatch):
    """Replace urllib.request.urlopen; set `.reply` to a body or an exception."""

    class Opener:
        reply: object = b"{}"
        requests: list = []

        def __call__(self, request, timeout=None):
            self.requests.append(request)
            if isinstance(self.reply, BaseException):
                raise self.reply
            return FakeResponse(self.reply)

    opener = Opener()
    opener.requests = []
    monkeypatch.setattr("urllib.request.urlopen", opener)
    return opener


class TestRequestJson:
    @API_TOOLS
    def test_parses_a_json_reply(self, tool, urlopen):
        urlopen.reply = b'{"name": "x"}'
        assert tool["request_json"]("https://git.example/api", headers={"A": "b"}) == {"name": "x"}

    @API_TOOLS
    def test_an_empty_reply_is_none(self, tool, urlopen):
        urlopen.reply = b""
        assert tool["request_json"]("https://git.example/api", method="DELETE") is None

    @API_TOOLS
    def test_a_body_is_sent_as_json(self, tool, urlopen):
        urlopen.reply = b"{}"
        tool["request_json"]("https://git.example/api", method="POST", body={"k": 1})
        assert json.loads(urlopen.requests[0].data) == {"k": 1}
        assert urlopen.requests[0].get_method() == "POST"

    @API_TOOLS
    @pytest.mark.parametrize(
        "code, category",
        [(401, "credentials"), (403, "permissions"), (500, "api")],
    )
    def test_an_http_error_is_named_by_category(self, tool, urlopen, code, category):
        urlopen.reply = http_error(code)
        with pytest.raises(tool["WorkflowError"]) as error:
            tool["request_json"]("https://git.example/api")
        assert error.value.category == category
        assert str(code) in str(error.value)

    @pytest.mark.parametrize("tool", [publish, sync], ids=["publish_wiki", "sync_github_metadata"])
    def test_a_missing_repository_is_a_configuration_error(self, tool, urlopen):
        urlopen.reply = http_error(404)
        with pytest.raises(tool["WorkflowError"]) as error:
            tool["request_json"]("https://git.example/api")
        assert error.value.category == "configuration"

    @API_TOOLS
    def test_an_unreachable_host_is_an_api_error(self, tool, urlopen):
        urlopen.reply = urllib.error.URLError("no route")
        with pytest.raises(tool["WorkflowError"]) as error:
            tool["request_json"]("https://git.example/api")
        assert error.value.category == "api"
        assert "unreachable" in str(error.value)

    def test_the_sync_tool_names_the_service_in_its_message(self, urlopen):
        urlopen.reply = http_error(500)
        with pytest.raises(sync["WorkflowError"]) as github:
            sync["request_json"]("https://api.github.com/repos/o/r")
        assert "GitHub API" in str(github.value)
        with pytest.raises(sync["WorkflowError"]) as gitea:
            sync["request_json"]("https://git.example/api/v1/repos/o/r")
        assert "Gitea API" in str(gitea.value)


class TestPagination:
    def test_release_reads_every_page_of_tags(self):
        pages = {1: [{"name": f"v{n}"} for n in range(50)], 2: [{"name": "v50"}], 3: []}

        def request(url, headers=None):
            page = int(url.split("page=")[1])
            return pages[page]

        names = release["list_tag_names"]("https://git.example/api", {}, request)
        assert len(names) == 51 and names[-1] == "v50"

    def test_release_stops_on_an_empty_first_page(self):
        assert release["list_tag_names"]("https://git.example/api", {}, lambda *a, **k: []) == []

    def test_publish_reads_every_page_of_wiki_titles(self):
        full = [{"sub_url": f"Page-{n}"} for n in range(publish["PAGE_LIMIT"])]
        calls = []

        def send(url, headers=None):
            calls.append(url)
            return full if "page=1&" in url else [{"sub_url": "Last"}]

        titles = publish["list_wiki_titles"]("https://git.example/wiki", {}, send)
        assert len(calls) == 2
        assert "Last" in titles and "Page-0" in titles

    def test_publish_refuses_a_list_that_is_not_a_list(self):
        with pytest.raises(publish["WorkflowError"]) as error:
            publish["list_wiki_titles"](
                "https://git.example/wiki", {}, lambda *a, **k: {"message": "x"}
            )
        assert error.value.category == "api"


class TestReleaseInputs:
    @pytest.fixture()
    def env(self, tmp_path, monkeypatch):
        changelog_file = tmp_path / "CHANGELOG.md"
        changelog_file.write_text(
            "## [Unreleased]\n\n## [1.0.0] - 2026-10-10\n\n### Added\n\n- First.\n",
            encoding="utf-8",
        )
        for key, value in {
            "GITEA_API_URL": "https://git.example/api/v1",
            "SOURCE_REPOSITORY": "o/r",
            "RELEASE_CREDENTIALS": "t" * 40,
            "RELEASE_VERSION": "1.0.0",
            "RELEASE_SHA": "a" * 40,
            "RELEASE_DRY_RUN": "true",
            "CHANGELOG_FILE": str(changelog_file),
        }.items():
            monkeypatch.setenv(key, value)
        return monkeypatch

    @pytest.mark.parametrize("repository", ["", "owner", "/repo", "owner/"])
    def test_a_malformed_repository_is_refused(self, env, repository):
        env.setenv("SOURCE_REPOSITORY", repository)
        with pytest.raises(release["WorkflowError"]) as error:
            release["main"](request=lambda *a, **k: None)
        assert error.value.category == "configuration"

    @pytest.mark.parametrize("sha", ["", "abc", "g" * 40])
    def test_a_malformed_commit_is_refused(self, env, sha):
        env.setenv("RELEASE_SHA", sha)
        with pytest.raises(release["WorkflowError"]) as error:
            release["main"](request=lambda *a, **k: None)
        assert "RELEASE_SHA" in str(error.value)

    def test_an_unreadable_changelog_is_a_configuration_error(self, env, tmp_path):
        env.setenv("CHANGELOG_FILE", str(tmp_path / "missing.md"))
        with pytest.raises(release["WorkflowError"]) as error:
            release["main"](request=lambda *a, **k: None)
        assert error.value.category == "configuration"

    def test_a_changelog_that_breaks_its_convention_is_a_validation_error(self, env, tmp_path):
        bad = tmp_path / "bad.md"
        bad.write_text("## [1.0.0] - 2026-10-10\n\n### Added\n\n- X.\n", encoding="utf-8")
        env.setenv("CHANGELOG_FILE", str(bad))
        with pytest.raises(release["WorkflowError"]) as error:
            release["main"](request=lambda *a, **k: None)
        assert error.value.category == "validation"
        assert "Unreleased" in str(error.value)


class TestChangelogCommandLine:
    @pytest.fixture()
    def good(self, tmp_path):
        path = tmp_path / "CHANGELOG.md"
        path.write_text(
            "## [Unreleased]\n\n## [1.1.0] - 2026-10-11\n\n### Added\n\n- A.\n\n"
            "## [1.0.0] - 2026-10-10\n\n### Fixed\n\n- B.\n",
            encoding="utf-8",
        )
        return path

    def test_check_passes_a_good_file(self, good, capsys):
        assert changelog["main"](["check", "--file", str(good)]) == 0
        assert "follows the convention" in capsys.readouterr().out

    def test_check_names_a_missing_version(self, good, capsys):
        assert changelog["main"](["check", "--file", str(good), "--version", "2.0.0"]) == 1
        assert "no changelog entry with changes for version 2.0.0" in capsys.readouterr().err

    def test_check_reports_each_problem(self, tmp_path, capsys):
        path = tmp_path / "CHANGELOG.md"
        path.write_text("## [1.0.0]\n\n### Odd\n\n", encoding="utf-8")
        assert changelog["main"](["check", "--file", str(path)]) == 1
        err = capsys.readouterr().err
        assert "first section must be `## [Unreleased]`" in err
        assert "not one of Breaking, Added, Changed, Fixed" in err
        assert "needs a date" in err

    def test_notes_prints_the_release_page(self, good, capsys):
        assert changelog["main"](["notes", "1.1.0", "--file", str(good)]) == 0
        out = capsys.readouterr().out
        assert out.startswith("## 1.1.0 - 2026-10-11") and "- A." in out

    def test_notes_needs_a_version(self, good, capsys):
        assert changelog["main"](["notes", "--file", str(good)]) == 1
        assert "needs a version" in capsys.readouterr().err

    def test_notes_names_an_unknown_version(self, good, capsys):
        assert changelog["main"](["notes", "9.9.9", "--file", str(good)]) == 1
        assert "no changelog entry" in capsys.readouterr().err

    def test_a_group_without_an_item_and_a_release_without_a_group_are_problems(self):
        text = "## [Unreleased]\n\n### Added\n\n## [1.0.0] - 2026-10-10\n"
        problems = changelog["validate"](text)
        assert any("has no item" in p for p in problems)
        assert any("has no change group" in p for p in problems)

    def test_an_unreleased_section_has_no_date_and_versions_descend(self):
        text = (
            "## [Unreleased] - 2026-10-10\n\n## [1.0.0] - 2026-10-10\n\n### Added\n\n- A.\n\n"
            "## [1.1.0] - 2026-10-11\n\n### Added\n\n- B.\n"
        )
        problems = changelog["validate"](text)
        assert any("has no date" in p for p in problems)
        assert any("must be lower than the version above it" in p for p in problems)


class TestBuildWikiCommandLine:
    def test_hash_prints_twelve_hex_digits_for_a_page(self, capsys):
        assert build_wiki["main"](["--hash", "Home"]) == 0
        assert len(capsys.readouterr().out.strip()) == build_wiki["HASH_LENGTH"]

    def test_hash_of_an_unknown_page_fails(self, capsys):
        assert build_wiki["main"](["--hash", "Nope"]) == 1
        assert "unknown page" in capsys.readouterr().err

    def test_check_passes_on_the_committed_wiki(self, capsys):
        assert build_wiki["main"](["--check"]) == 0
        assert "up to date" in capsys.readouterr().out

    def test_check_lists_every_problem_and_the_command_that_fixes_it(self, monkeypatch, capsys):
        monkeypatch.setattr(build_wiki._module, "check_pages", lambda: ["Home.md: missing"])
        monkeypatch.setattr(build_wiki._module, "check_translations", lambda: [])
        assert build_wiki["main"](["--check"]) == 1
        err = capsys.readouterr().err
        assert "ERROR: wiki/Home.md: missing" in err
        assert "python tools/build_wiki.py" in err

    def test_generate_reports_the_changed_pages(self, monkeypatch, capsys):
        monkeypatch.setattr(build_wiki._module, "write_pages", lambda: ["Home.md"])
        assert build_wiki["main"]([]) == 0
        assert "Wrote 1 page(s): Home.md" in capsys.readouterr().out

    def test_generate_reports_a_build_error(self, monkeypatch, capsys):
        def broken():
            raise build_wiki["WikiBuildError"]("README.md is missing")

        monkeypatch.setattr(build_wiki._module, "write_pages", broken)
        assert build_wiki["main"]([]) == 1
        assert "ERROR: README.md is missing" in capsys.readouterr().err


def run_tool(name: str, **env: str) -> subprocess.CompletedProcess:
    """Run a tool as `python tools/<name>` with only the given environment."""
    environment = {"PATH": "", "SYSTEMROOT": "", **env}
    environment = {k: v for k, v in environment.items() if v != "" or k in env}
    return subprocess.run(
        [sys.executable, str(TOOLS / name)],
        env=environment,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


class TestRunAsAProcess:
    """The `if __name__ == "__main__"` block: exit code 1 and ERROR: on stderr."""

    def test_release_without_a_version_exits_1(self):
        result = run_tool("release.py")
        assert result.returncode == 1
        assert result.stderr.startswith("ERROR: [configuration]")

    def test_publish_wiki_without_a_repository_exits_1(self):
        result = run_tool("publish_wiki.py", WIKI_DIR=str(REPO_ROOT / "wiki"), GITEA_API_URL="https://x")
        assert result.returncode == 1
        assert "ERROR:" in result.stderr

    def test_sync_without_a_token_exits_1(self):
        result = run_tool("sync_github_metadata.py", GITEA_API_URL="https://x", SOURCE_REPOSITORY="o/r")
        assert result.returncode == 1
        assert "ERROR:" in result.stderr and "TOKEN_FOR_GITEA" in result.stderr

    def test_changelog_checks_the_committed_file(self):
        result = run_tool("changelog.py", **{})
        assert result.returncode != 0  # the command is required
        result = subprocess.run(
            [sys.executable, str(TOOLS / "changelog.py"), "check"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, result.stderr


class TestRemainingBranches:
    def test_notes_of_a_release_without_changes_is_not_a_page(self):
        text = "## [Unreleased]\n\n## [1.0.0] - 2026-10-10\n"
        with pytest.raises(LookupError):
            changelog["notes"](text, "1.0.0")

    @pytest.mark.parametrize("repository", [None, "", "owner", "/repo", "owner/"])
    def test_publish_refuses_a_malformed_repository(self, repository):
        with pytest.raises(publish["WorkflowError"]) as error:
            publish["split_repository"](repository)
        assert error.value.category == "configuration"

    def test_publish_treats_a_wiki_without_pages_as_empty(self):
        def send(url, headers=None):
            raise publish["WorkflowError"]("configuration", "not found")

        assert publish["list_wiki_titles"]("https://git.example/wiki", {}, send) == set()

    def test_publish_does_not_hide_a_failure_on_a_later_page(self):
        full = [{"sub_url": f"P-{n}"} for n in range(publish["PAGE_LIMIT"])]

        def send(url, headers=None):
            if "page=1&" in url:
                return full
            raise publish["WorkflowError"]("configuration", "gone")

        with pytest.raises(publish["WorkflowError"]):
            publish["list_wiki_titles"]("https://git.example/wiki", {}, send)
