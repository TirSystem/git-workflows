"""Offline tests for tools/english_comments.py (MIL-013, ADR-0012).

The detector is measured on the corpus in tests/fixtures/comments/; the rates
of criterion 1 of MIL-013 are tests, so a change that lowers them fails.
"""

import csv
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from workflow_source import REPO_ROOT, load_script

ec = load_script(REPO_ROOT / "tools" / "english_comments.py", "english_comments")
CORPUS = REPO_ROOT / "tests" / "fixtures" / "comments"
GIT = shutil.which("git")


def corpus() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for name in ("english.tsv", "foreign.tsv"):
        with (CORPUS / name).open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t", quoting=csv.QUOTE_NONE)
            rows += [(row["lang"], row["text"]) for row in reader]
    return rows


@pytest.fixture(scope="module")
def results():
    found: dict[str, list[int]] = {}
    for language, text in corpus():
        counts = found.setdefault(language, [0, 0])
        counts[1] += 1
        counts[0] += ec.judge(text) is not None
    return found


class TestCorpusRates:
    """Criterion 1 of MIL-013: recall of at least 90 % for Danish and Malay, and at most
    one false positive per 200 English comments."""

    def test_the_corpus_has_the_size_the_milestone_asks_for(self, results):
        assert results["en"][1] >= 200
        assert results["da"][1] >= 40
        assert results["ms"][1] >= 40
        assert sum(v[1] for k, v in results.items() if k not in ("en", "da", "ms")) >= 40

    def test_english_comments_are_not_flagged(self, results):
        flagged, total = results["en"]
        assert flagged <= total // 200

    @pytest.mark.parametrize("language", ["da", "ms"])
    def test_danish_and_malay_are_found(self, results, language):
        flagged, total = results[language]
        assert flagged / total >= 0.90

    def test_other_languages_are_found(self, results):
        for language in ("de", "sv", "no", "fr"):
            flagged, total = results[language]
            assert flagged / total >= 0.80


class TestWords:
    def test_paths_options_identifiers_and_numbers_are_not_words(self):
        text = "Run tools/badges.py --metrics code-metrics.json with snake_case camelCase v2 DIR"
        assert ec.words(text) == ["Run", "with"]

    def test_json_and_code_characters_are_not_words(self):
        assert ec.words('{"files": 3, "lines": 120} x = 1 <a|b>') == []

    def test_a_label_and_an_acronym_are_dropped(self):
        assert ec.words("Usage: lint the JSON files") == ["lint", "the", "files"]

    def test_a_hyphenated_word_is_split_and_allowed_words_are_removed(self):
        assert ec.words("read-only access", frozenset({"access"})) == ["read", "only"]

    def test_a_hidden_file_is_not_a_word_but_an_ellipsis_is_kept(self):
        assert ec.words("needs a .clang-format file...") == ["needs", "file"]

    def test_quotes_inside_a_word_are_kept_once(self):
        assert ec.words("don't can't won''t") == ["don't", "can't"]


class TestExtract:
    def test_python_comments_and_docstrings(self):
        source = '"""Module line one.\n\nSecond paragraph."""\n\n# a comment\nx = 1  # trailing\n\ndef f():\n    """Doc of f."""\n'
        found = dict(ec.extract("a.py", source))
        assert found[1] == "Module line one."
        assert found[5] == "a comment"
        assert found[6] == "trailing"
        assert found[9] == "Doc of f."

    def test_python_that_does_not_parse_falls_back_to_the_scanner(self):
        assert dict(ec.extract("a.py", "def (:\n# still a comment\n")) == {2: "still a comment"}

    def test_shell_and_sql_line_comments(self):
        assert ec.extract("a.sh", "#!/bin/sh\n# real comment\necho '# not'\n") == [(2, "real comment")]
        assert ec.extract("a.sql", "SELECT 1; -- one row\n") == [(1, "one row")]

    def test_c_block_and_line_comments_lose_their_decoration(self):
        source = "/**\n * First line\n * second line\n */\nint x; // trailing\n/// doc\n"
        assert ec.extract("a.c", source) == [(2, "First line"), (3, "second line"), (5, "trailing"), (6, "doc")]

    def test_a_comment_inside_a_string_is_not_a_comment(self):
        assert ec.extract("a.c", 'char *s = "// not a comment";\n') == []

    def test_tool_pragmas_are_not_prose(self):
        source = "x = 1  # noqa: E501\n# type: ignore\n# pylint: disable=x\n# a real comment\n"
        assert ec.extract("a.py", source) == [(4, "a real comment")]

    def test_a_file_of_an_unknown_language_has_no_comments(self):
        assert ec.extract("notes.md", "# Heading\n") == []

    def test_consecutive_lines_are_one_group(self):
        lines = [(1, "a"), (2, "b"), (4, "c"), (5, "d"), (5, "e")]
        assert ec.groups(lines) == [[(1, "a"), (2, "b")], [(4, "c"), (5, "d"), (5, "e")]]


class TestCheckText:
    DANISH = "# Denne funktion beregner totalen for kurven og gemmer resultatet\n"

    def test_a_danish_comment_is_a_finding_with_its_line(self):
        findings = ec.check_text("a.py", "x = 1\n" + self.DANISH)
        assert [(f.path, f.line, f.language) for f in findings] == [("a.py", 2, "da")]

    def test_an_english_comment_is_not(self):
        assert ec.check_text("a.py", "# This function adds the totals of the basket together\n") == []

    def test_only_the_blocks_on_the_given_lines_are_checked(self):
        text = self.DANISH + "x = 1\n" + self.DANISH
        assert [f.line for f in ec.check_text("a.py", text, {3})] == [3]
        assert ec.check_text("a.py", text, {2}) == []

    def test_a_danish_line_next_to_an_english_line_is_still_found(self):
        english = "# This function adds the totals of the basket together and returns the sum\n"
        findings = ec.check_text("a.py", english + self.DANISH)
        assert [(f.line, f.end_line, f.language) for f in findings] == [(2, 2, "da")]

    def test_a_sentence_cut_over_short_lines_is_judged_as_a_whole(self):
        text = "# Denne funktion\n# beregner totalen\n# for kurven\n# og gemmer resultatet\n"
        [finding] = ec.check_text("a.py", text)
        assert (finding.line, finding.end_line, finding.language) == (1, 4, "da")

    def test_only_a_flagged_line_is_reported_when_the_block_is_mixed(self):
        text = self.DANISH + "# and this line is plain English text about the totals\n"
        assert [f.line for f in ec.check_text("a.py", text, {2})] == []

    def test_the_marker_skips_the_block(self):
        text = self.DANISH.rstrip() + "  # english-comments: ignore\n"
        assert ec.check_text("a.py", text) == []

    def test_allowed_words_are_not_judged(self):
        allowed = frozenset(self.DANISH.lower().replace("#", "").replace(",", "").split())
        assert ec.check_text("a.py", self.DANISH, allowed=allowed) == []

    def test_a_short_comment_is_not_judged(self):
        assert ec.check_text("a.py", "# ret fejlen\n") == []

    def test_json_in_a_docstring_is_not_french(self):
        source = '"""Count.\n\n    {"files": 3, "lines": 120, "comment": 14, "blank": 22,\n    "languages": {"Python": {"files": 2, "lines": 100}}}\n"""\n'
        assert ec.check_text("a.py", source) == []

    def test_usage_lines_with_options_are_not_judged(self):
        text = "# Usage: lint-action-scripts.sh [<directory>] (default: actions)\n"
        assert ec.check_text("a.sh", text) == []

    def test_describe_names_the_language_and_cuts_a_long_text(self):
        finding = ec.Finding("a.py", 1, 1, "da", 0.93, "x " * 100)
        message = ec.describe(finding)
        assert message.startswith('looks Danish (0.93): "') and message.endswith('..."')


class TestAllowedWords:
    def test_words_one_per_line_with_comments(self, tmp_path):
        file = tmp_path / "allowed.txt"
        file.write_text("Kubernetes\n# a comment\nSkat  # a Danish tax name\n\n", encoding="utf-8")
        assert ec.read_allowed_words(str(file)) == {"kubernetes", "skat"}

    def test_no_file_named_is_no_words(self):
        assert ec.read_allowed_words(None) == frozenset()

    def test_an_unreadable_file_is_an_error(self, tmp_path):
        with pytest.raises(ec.CheckError):
            ec.read_allowed_words(str(tmp_path / "missing.txt"))


def run_git(directory: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=directory, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    """A repository with a base commit on main and a branch that adds comments."""
    if GIT is None:
        pytest.skip("git is needed")
    run_git(tmp_path, "init", "-q", "-b", "main")
    run_git(tmp_path, "config", "user.email", "t@example.org")
    run_git(tmp_path, "config", "user.name", "t")
    run_git(tmp_path, "config", "commit.gpgsign", "false")
    (tmp_path / "old.py").write_bytes(b"# Denne gamle funktion beregner totalen for kurven\nx = 1\n")
    run_git(tmp_path, "add", ".")
    run_git(tmp_path, "commit", "-q", "-m", "base")
    run_git(tmp_path, "checkout", "-q", "-b", "feature")
    return tmp_path


def commit_file(repo: Path, name: str, content: bytes) -> None:
    (repo / name).write_bytes(content)
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-q", "-m", name)


class TestRepository:
    def test_only_the_comments_a_branch_adds_are_checked(self, repo, capsys):
        commit_file(repo, "new.py", b"# Denne funktion beregner totalen for kurven\n")
        code = ec.main(["check", "--directory", str(repo), "--base", "main", "--output", str(repo / "f.json")])
        out = capsys.readouterr().out
        assert code == 1
        assert "::error file=new.py,line=1::[english-comments] looks Danish" in out
        assert "old.py" not in out  # the old Danish comment is not this branch's
        saved = json.loads((repo / "f.json").read_text(encoding="utf-8"))
        assert [(f["path"], f["line"], f["language"]) for f in saved] == [("new.py", 1, "da")]

    def test_an_added_line_in_an_old_file_is_checked_and_the_old_ones_are_not(self, repo):
        commit_file(repo, "old.py", b"# Denne gamle funktion beregner totalen for kurven\nx = 1\n# Hold the lock while the file is written\n")
        findings, files = ec.check_repository(repo, "main", False, [], frozenset(), 0.6, 3)
        assert findings == [] and files == 1

    def test_a_clean_branch_exits_zero(self, repo, capsys):
        commit_file(repo, "new.py", b"# This function adds the totals of the basket together\n")
        assert ec.main(["check", "--directory", str(repo), "--base", "main"]) == 0
        assert "All comments are in English: 1 file(s) checked." in capsys.readouterr().out

    def test_scope_all_checks_every_tracked_file(self, repo, capsys):
        assert ec.main(["check", "--directory", str(repo), "--scope", "all"]) == 1
        assert "old.py:1" in capsys.readouterr().out

    def test_excluded_binary_unknown_and_large_files_are_skipped(self, repo, monkeypatch):
        danish = b"# Denne funktion beregner totalen for kurven og gemmer resultatet\n"
        (repo / "vendor").mkdir()
        commit_file(repo, "vendor/skip.py", danish)
        commit_file(repo, "skipme.py", danish)
        commit_file(repo, "bin.py", danish + b"\x00")
        commit_file(repo, "notes.md", b"# Denne funktion beregner totalen for kurven\n")
        monkeypatch.setattr(ec, "MAX_FILE_BYTES", 10)
        commit_file(repo, "big.py", danish)
        findings, files = ec.check_repository(repo, "main", False, ["skipme.py"], frozenset(), 0.6, 3)
        assert (findings, files) == ([], 0)

    def test_a_deleted_file_in_the_selection_is_skipped(self, repo):
        commit_file(repo, "gone.py", b"x = 1\n")
        (repo / "gone.py").unlink()
        findings, files = ec.check_repository(repo, "main", False, [], frozenset(), 0.6, 3)
        assert findings == []

    def test_changed_lines_reads_every_hunk(self, repo):
        commit_file(repo, "h.py", b"a\nb\nc\nd\n")
        commit_file(repo, "h.py", b"a\nB\nc\nD\nE\n")
        assert ec.changed_lines(repo, "main")["h.py"] == {1, 2, 3, 4, 5}


class TestMain:
    def test_a_missing_base_is_a_configuration_error(self, repo, capsys):
        assert ec.main(["check", "--directory", str(repo)]) == 2
        assert "::error::[configuration] give --base" in capsys.readouterr().out

    def test_an_unknown_base_is_a_configuration_error(self, repo, capsys):
        assert ec.main(["check", "--directory", str(repo), "--base", "nope"]) == 2
        assert "failed: fatal" in capsys.readouterr().out

    def test_a_missing_directory_is_a_configuration_error(self, tmp_path, capsys):
        assert ec.main(["check", "--directory", str(tmp_path / "x"), "--scope", "all"]) == 2
        assert "does not exist" in capsys.readouterr().out

    @pytest.mark.parametrize("flags", [["--threshold", "0"], ["--threshold", "1.5"], ["--min-words", "0"]])
    def test_bad_numbers_are_a_configuration_error(self, tmp_path, capsys, flags):
        assert ec.main(["check", "--directory", str(tmp_path), "--scope", "all", *flags]) == 2
        assert "threshold" in capsys.readouterr().out

    def test_langid_missing_is_a_configuration_error(self, repo, monkeypatch, capsys):
        commit_file(repo, "new.py", b"# Denne funktion beregner totalen for kurven og gemmer resultatet\n")
        monkeypatch.setattr(ec, "_identifier", None)
        monkeypatch.setitem(__import__("sys").modules, "langid.langid", None)
        assert ec.main(["check", "--directory", str(repo), "--base", "main"]) == 2
        assert "langid is not installed" in capsys.readouterr().out
