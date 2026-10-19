"""Count the code files and the lines of code of a directory (ADR-0010).

A code file is a text file whose extension is in LANGUAGES. Every physical line
of it is exactly one of blank, comment or code; the lines of code are the code
lines only. The result is JSON:

    {"files": 3, "lines": 120, "comment": 14, "blank": 22,
     "languages": {"Python": {"files": 2, "lines": 100, "comment": 10, "blank": 20}}}

Usage:
    python tools/count_loc.py [--directory DIR] [--exclude PATTERNS] [--output FILE]

Exit codes: 0 counted, 1 the directory is not a directory (printed as
`::error::[configuration] ...`).
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_EXCLUDED_DIRS = frozenset(
    {
        "node_modules",
        "vendor",
        "third_party",
        "dist",
        "build",
        "out",
        "bin",
        "obj",
        "target",
        "venv",
        "__pycache__",
        "shared-scripts",
    }
)

_C_STYLE_CHAR = re.compile(r"'(?:\\.[^']*|[^'\\])'")


@dataclass(frozen=True)
class Language:
    """The comment and string rules of one language."""

    name: str
    extensions: tuple[str, ...]
    line_comment: str | None = None
    block: tuple[str, str] | None = None
    nested_block: bool = False
    hash_at_word_start: bool = False
    triple_quotes: bool = False
    backtick_strings: bool = False
    single_quote: str = (
        "string"  # "string", "char" (a literal of one character) or "none"
    )
    backslash_escapes: bool = True
    escapes_in_single_quotes: bool = True


def _c_family(name: str, *extensions: str, single_quote: str = "char") -> Language:
    return Language(
        name,
        extensions,
        line_comment="//",
        block=("/*", "*/"),
        single_quote=single_quote,
    )


LANGUAGES: tuple[Language, ...] = (
    Language("Python", (".py",), line_comment="#", triple_quotes=True),
    Language(
        "Shell",
        (".sh", ".bash"),
        line_comment="#",
        hash_at_word_start=True,
        escapes_in_single_quotes=False,
    ),
    Language(
        "PowerShell",
        (".ps1", ".psm1"),
        line_comment="#",
        block=("<#", "#>"),
        hash_at_word_start=True,
        backslash_escapes=False,
    ),
    _c_family("C", ".c", ".h"),
    _c_family("C++", ".cc", ".cpp", ".cxx", ".hh", ".hpp"),
    _c_family("C#", ".cs"),
    _c_family("Java", ".java"),
    Language(
        "JavaScript",
        (".js", ".mjs", ".jsx"),
        line_comment="//",
        block=("/*", "*/"),
        backtick_strings=True,
    ),
    Language(
        "TypeScript",
        (".ts", ".tsx"),
        line_comment="//",
        block=("/*", "*/"),
        backtick_strings=True,
    ),
    Language(
        "Go",
        (".go",),
        line_comment="//",
        block=("/*", "*/"),
        backtick_strings=True,
        single_quote="char",
    ),
    Language(
        "Rust",
        (".rs",),
        line_comment="//",
        block=("/*", "*/"),
        nested_block=True,
        single_quote="char",
    ),
    Language(
        "SQL",
        (".sql",),
        line_comment="--",
        block=("/*", "*/"),
        backslash_escapes=False,
    ),
)

_BY_EXTENSION = {ext: language for language in LANGUAGES for ext in language.extensions}
_WORD_START = " \t;|&("


def language_of(path: str) -> Language | None:
    """Return the language of a file name by its extension, or None."""
    return _BY_EXTENSION.get(os.path.splitext(path)[1].lower())


@dataclass
class _State:
    block_depth: int = 0
    triple: str | None = None
    backtick: bool = False


def _skip_string(line: str, start: int, quote: str, escapes: bool) -> int:
    """Return the index after the string that opens at start; the end of line if unclosed."""
    i = start + 1
    while i < len(line):
        char = line[i]
        if escapes and char == "\\":
            i += 2
            continue
        if char == quote:
            return i + 1
        i += 1
    return len(line)


def _scan_line(
    line: str,
    language: Language,
    state: _State,
    comments: list[str] | None = None,
) -> tuple[bool, bool]:
    """Scan one line; return (has_code, has_comment) and update the state.

    When ``comments`` is given, the text of every comment on the line is
    appended to it (the English-comments check, ADR-0012, reads that text).
    """
    has_code = False
    has_comment = False
    i = 0
    size = len(line)
    block = language.block
    while i < size:
        if state.block_depth:
            assert block is not None
            has_comment = True
            end = line.find(block[1], i)
            nested = line.find(block[0], i) if language.nested_block else -1
            if comments is not None:
                stop = nested if nested != -1 and (end == -1 or nested < end) else end
                comments.append(line[i : size if stop == -1 else stop])
            if nested != -1 and (end == -1 or nested < end):
                state.block_depth += 1
                i = nested + len(block[0])
            elif end == -1:
                return has_code, has_comment
            else:
                state.block_depth -= 1
                i = end + len(block[1])
            continue
        if state.triple is not None:
            has_code = True
            end = line.find(state.triple, i)
            if end == -1:
                return has_code, has_comment
            i = end + len(state.triple)
            state.triple = None
            continue
        if state.backtick:
            has_code = True
            end = line.find("`", i)
            if end == -1:
                return has_code, has_comment
            i = end + 1
            state.backtick = False
            continue
        char = line[i]
        if char in " \t\r\f\v":
            i += 1
            continue
        if block is not None and line.startswith(block[0], i):
            state.block_depth = 1
            has_comment = True
            i += len(block[0])
            continue
        comment = language.line_comment
        if comment is not None and line.startswith(comment, i):
            word_start = i == 0 or line[i - 1] in _WORD_START
            if word_start or not language.hash_at_word_start:
                if comments is not None:
                    comments.append(line[i + len(comment) :])
                return has_code, True
        if language.triple_quotes and (
            line.startswith('"""', i) or line.startswith("'''", i)
        ):
            state.triple = line[i : i + 3]
            has_code = True
            i += 3
            continue
        if char == '"':
            has_code = True
            i = _skip_string(line, i, '"', language.backslash_escapes)
            continue
        if char == "'" and language.single_quote == "string":
            has_code = True
            escapes = language.backslash_escapes and language.escapes_in_single_quotes
            i = _skip_string(line, i, "'", escapes)
            continue
        if char == "'" and language.single_quote == "char":
            has_code = True
            literal = _C_STYLE_CHAR.match(line, i)
            i = literal.end() if literal else i + 1
            continue
        if char == "`" and language.backtick_strings:
            has_code = True
            end = line.find("`", i + 1)
            if end == -1:
                state.backtick = True
                return has_code, has_comment
            i = end + 1
            continue
        has_code = True
        i += 1
    return has_code, has_comment


def classify_text(text: str, language: Language) -> tuple[int, int, int]:
    """Return (code, comment, blank) line counts of the text of a file."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    state = _State()
    code = comment = blank = 0
    for line in lines:
        has_code, _ = _scan_line(line, language, state)
        if line.strip() == "":
            blank += 1
        elif has_code:
            code += 1
        else:
            comment += 1
    return code, comment, blank


def _pattern_regex(pattern: str) -> re.Pattern[str]:
    """Translate an exclude pattern: `*` stops at `/`, `**` crosses it, `?` is one character."""
    out = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if pattern.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        out.append(
            "[^/]*" if char == "*" else "[^/]" if char == "?" else re.escape(char)
        )
        i += 1
    return re.compile("".join(out) + r"\Z")


class Excludes:
    """The exclude patterns of the caller; a pattern without `/` matches a name anywhere."""

    def __init__(self, patterns: list[str]) -> None:
        self._names: list[re.Pattern[str]] = []
        self._paths: list[re.Pattern[str]] = []
        for pattern in patterns:
            pattern = pattern.strip().strip("/")
            if not pattern:
                continue
            target = self._paths if "/" in pattern else self._names
            target.append(_pattern_regex(pattern))

    def matches(self, name: str, relative: str) -> bool:
        return any(rx.match(name) for rx in self._names) or any(
            rx.match(relative) for rx in self._paths
        )


def _is_text(data: bytes) -> bool:
    return b"\x00" not in data


def count(directory: Path, patterns: list[str] | None = None) -> dict[str, object]:
    """Count the code files under directory; see the module docstring for the result."""
    excludes = Excludes(patterns or [])
    totals = {"files": 0, "lines": 0, "comment": 0, "blank": 0}
    per_language: dict[str, dict[str, int]] = {}
    root = str(directory)
    for current, dirs, files in os.walk(root, followlinks=False):
        relative_dir = os.path.relpath(current, root).replace(os.sep, "/")
        prefix = "" if relative_dir == "." else relative_dir + "/"
        dirs[:] = sorted(
            name
            for name in dirs
            if not name.startswith(".")
            and name not in DEFAULT_EXCLUDED_DIRS
            and not excludes.matches(name, prefix + name)
        )
        for name in sorted(files):
            full = os.path.join(current, name)
            language = language_of(name)
            if (
                language is None
                or os.path.islink(full)
                or excludes.matches(name, prefix + name)
            ):
                continue
            data = Path(full).read_bytes()
            if not _is_text(data):
                continue
            text = data.decode("utf-8", errors="replace").lstrip("﻿")
            code, comment, blank = classify_text(text, language)
            entry = per_language.setdefault(
                language.name, {"files": 0, "lines": 0, "comment": 0, "blank": 0}
            )
            for target in (entry, totals):
                target["files"] += 1
                target["lines"] += code
                target["comment"] += comment
                target["blank"] += blank
    return {**totals, "languages": dict(sorted(per_language.items()))}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--directory", default=".", help="directory to count (default .)"
    )
    parser.add_argument("--exclude", default="", help="comma list of exclude patterns")
    parser.add_argument(
        "--output", help="write the JSON here instead of standard output"
    )
    args = parser.parse_args(argv)
    directory = Path(args.directory)
    if not directory.is_dir():
        print(
            f"::error::[configuration] working-directory '{args.directory}' does not exist."
        )
        return 1
    result = count(directory, [p for p in args.exclude.split(",") if p.strip()])
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
