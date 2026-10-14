"""Offline tests for tools/count_loc.py (ADR-0010): hand-counted fixtures per language."""

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_SPEC = importlib.util.spec_from_file_location(
    "count_loc", REPO_ROOT / "tools" / "count_loc.py"
)
assert _SPEC is not None and _SPEC.loader is not None
count_loc = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(count_loc)

LANGUAGE = {language.name: language for language in count_loc.LANGUAGES}

# name -> (source, code, comment, blank), counted by hand.
FIXTURES = {
    "Python": (
        "# a comment\n"
        "x = 1  # trailing comment\n"
        "\n"
        's = "a # not a comment"\n'
        "t = 'it''s # still a string'\n"
        '"""docstring\n'
        "# inside a string\n"
        "\n"
        '"""\n'
        "y = 2",  # no final newline
        7,
        1,
        2,
    ),
    "Shell": (
        "#!/usr/bin/env bash\n"
        "# comment\n"
        'echo "$#" ${#args[@]} a#b\n'
        "\n"
        "  # indented comment\n"
        "echo 'it # stays' # but this is a comment\n"
        "ls | wc -l;# after a semicolon\n",
        3,
        3,
        1,
    ),
    "PowerShell": (
        '<# block\ncomment #>\nWrite-Host "a # b"\n# line\n$x = 1 # trailing\n',
        2,
        3,
        0,
    ),
    "C": (
        "/* header\n"
        " * text\n"
        " */\n"
        "#include <stdio.h>\n"
        "\n"
        "int main(void) { /* inline */ return 0; }\n"
        "char quote = '\"'; // a double quote in a char\n"
        'const char *url = "http://example.com";\n'
        "// done\n",
        4,
        4,
        1,
    ),
    "C++": (
        'int a = 0; // one\n/* block */\nauto s = "/* not a comment */";\n',
        2,
        1,
        0,
    ),
    "C#": (
        "// line\n"
        "using System;\n"
        "/// <summary>doc</summary>\n"
        'class A { string s = "// no"; }\n',
        2,
        2,
        0,
    ),
    "Java": (
        "/** doc */\nclass A {\n  // c\n  int x; /* t */\n}\n",
        3,
        2,
        0,
    ),
    "JavaScript": (
        "const a = `line one\n"
        "// in a template\n"
        "line three`;\n"
        "// real comment\n"
        "const b = 'x // y';\n"
        "/* a */ /* b */\n",
        4,
        2,
        0,
    ),
    "TypeScript": (
        "let n: number = 1; // c\n\n/*\n * block\n */\n",
        1,
        3,
        1,
    ),
    "Go": (
        "package main\n// c\nvar r = '/'\nvar raw = `// not a comment\n`\n",
        4,
        1,
        0,
    ),
    "Rust": (
        "/* outer /* nested */ still a comment */\n"
        "fn f<'a>(x: &'a str) -> &'a str { x } // lifetimes\n"
        "let c = '\\'';\n"
        "// end\n",
        2,
        2,
        0,
    ),
    "SQL": (
        "-- query\n"
        "SELECT '-- not a comment' FROM t; -- but this is\n"
        "/* a\n"
        "   block */\n"
        "\n",
        1,
        3,
        1,
    ),
}


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_fixture_counts_equal_the_hand_count(name):
    source, code, comment, blank = FIXTURES[name]
    assert count_loc.classify_text(source, LANGUAGE[name]) == (code, comment, blank)


def test_every_language_has_a_fixture():
    assert set(FIXTURES) == set(LANGUAGE)


class TestClassify:
    def test_empty_text_has_no_lines(self):
        assert count_loc.classify_text("", LANGUAGE["Python"]) == (0, 0, 0)

    def test_windows_line_endings_are_one_line_each(self):
        assert count_loc.classify_text("a = 1\r\n# c\r\n\r\n", LANGUAGE["Python"]) == (
            1,
            1,
            1,
        )

    def test_blank_line_inside_a_block_comment_is_blank(self):
        assert count_loc.classify_text("/*\n\n*/\n", LANGUAGE["C"]) == (0, 2, 1)

    def test_code_after_a_closing_block_comment_is_code(self):
        assert count_loc.classify_text("/* a\n b */ x();\n", LANGUAGE["C"]) == (1, 1, 0)

    def test_unterminated_string_ends_at_end_of_line(self):
        assert count_loc.classify_text('s = "open // x\n// c\n', LANGUAGE["C"]) == (
            1,
            1,
            0,
        )

    def test_unterminated_backtick_string_continues(self):
        assert count_loc.classify_text("a = `x\n// y\n", LANGUAGE["JavaScript"]) == (
            2,
            0,
            0,
        )

    def test_escaped_quote_does_not_end_the_string(self):
        assert count_loc.classify_text('s = "a \\" // b";\n', LANGUAGE["C"]) == (
            1,
            0,
            0,
        )


class TestPatterns:
    def test_star_stops_at_a_slash_and_double_star_does_not(self):
        excludes = count_loc.Excludes(["src/*.py", "docs/**"])
        assert excludes.matches("a.py", "src/a.py")
        assert not excludes.matches("a.py", "src/sub/a.py")
        assert excludes.matches("x.py", "docs/a/b/x.py")

    def test_name_pattern_matches_anywhere(self):
        excludes = count_loc.Excludes(["gen_*", "?.py"])
        assert excludes.matches("gen_a.py", "deep/er/gen_a.py")
        assert excludes.matches("a.py", "x/a.py")
        assert not excludes.matches("ab.py", "x/ab.py")

    def test_empty_patterns_are_ignored(self):
        assert not count_loc.Excludes(["", " / "]).matches("a.py", "a.py")


def write(root: Path, name: str, content: str | bytes) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


class TestCount:
    def test_counts_files_and_lines_per_language(self, tmp_path):
        write(tmp_path, "a.py", "x = 1\n# c\n\n")
        write(tmp_path, "pkg/b.py", "y = 2\n")
        write(tmp_path, "run.sh", "echo hi\n")
        write(tmp_path, "README.md", "# not code\n")
        result = count_loc.count(tmp_path)
        assert result == {
            "files": 3,
            "lines": 3,
            "comment": 1,
            "blank": 1,
            "languages": {
                "Python": {"files": 2, "lines": 2, "comment": 1, "blank": 1},
                "Shell": {"files": 1, "lines": 1, "comment": 0, "blank": 0},
            },
        }

    def test_default_excludes_hidden_vendored_and_shared_script_directories(
        self, tmp_path
    ):
        write(tmp_path, "keep.py", "a = 1\n")
        for directory in (
            ".git",
            ".venv",
            "node_modules",
            "vendor",
            "shared-scripts",
            "build",
        ):
            write(tmp_path, f"{directory}/skip.py", "b = 2\n")
        assert count_loc.count(tmp_path)["files"] == 1

    def test_exclude_patterns_add_to_the_defaults(self, tmp_path):
        write(tmp_path, "keep.py", "a = 1\n")
        write(tmp_path, "gen/out.py", "b = 2\n")
        write(tmp_path, "src/gen_x.py", "c = 3\n")
        write(tmp_path, "src/keep2.py", "d = 4\n")
        result = count_loc.count(tmp_path, ["gen", "gen_*"])
        assert result["files"] == 2

    def test_binary_file_with_a_code_extension_is_not_counted(self, tmp_path):
        write(tmp_path, "blob.py", b"a = 1\n\x00\x01")
        assert count_loc.count(tmp_path)["files"] == 0

    def test_invalid_utf8_and_a_byte_order_mark_are_read(self, tmp_path):
        write(tmp_path, "a.py", b"\xef\xbb\xbfx = 1\n\xff\xfe = 2\n")
        assert count_loc.count(tmp_path)["lines"] == 2

    def test_empty_code_file_is_a_file_with_no_lines(self, tmp_path):
        write(tmp_path, "empty.py", "")
        result = count_loc.count(tmp_path)
        assert (result["files"], result["lines"]) == (1, 0)

    def test_directory_without_code_files_counts_zero(self, tmp_path):
        write(tmp_path, "notes.txt", "hello\n")
        result = count_loc.count(tmp_path)
        assert result == {
            "files": 0,
            "lines": 0,
            "comment": 0,
            "blank": 0,
            "languages": {},
        }

    def test_symbolic_link_is_not_followed(self, tmp_path):
        real = tmp_path / "real"
        write(real, "a.py", "x = 1\n")
        link = tmp_path / "link.py"
        try:
            link.symlink_to(real / "a.py")
        except (OSError, NotImplementedError):
            pytest.skip("symbolic links are not available here")
        assert count_loc.count(real)["files"] == 1
        assert count_loc.count(tmp_path)["files"] == 1  # real/a.py only, not link.py


class TestMain:
    def test_prints_json_to_standard_output(self, tmp_path, capsys):
        write(tmp_path, "a.py", "x = 1\n")
        assert count_loc.main(["--directory", str(tmp_path)]) == 0
        out = json.loads(capsys.readouterr().out)
        assert out["files"] == 1 and out["lines"] == 1

    def test_writes_the_output_file_with_lf_endings(self, tmp_path):
        write(tmp_path, "src/a.py", "x = 1\n")
        target = tmp_path / "result.json"
        assert (
            count_loc.main(
                ["--directory", str(tmp_path / "src"), "--output", str(target)]
            )
            == 0
        )
        data = target.read_bytes()
        assert b"\r" not in data and json.loads(data)["files"] == 1

    def test_exclude_option_is_a_comma_list(self, tmp_path, capsys):
        write(tmp_path, "a.py", "x = 1\n")
        write(tmp_path, "b.py", "y = 1\n")
        write(tmp_path, "c.py", "z = 1\n")
        assert (
            count_loc.main(["--directory", str(tmp_path), "--exclude", "a.py, b.py"])
            == 0
        )
        assert json.loads(capsys.readouterr().out)["files"] == 1

    def test_missing_directory_is_a_configuration_error(self, tmp_path, capsys):
        assert count_loc.main(["--directory", str(tmp_path / "nope")]) == 1
        assert "::error::[configuration]" in capsys.readouterr().out
