"""Find comments in source code that are not written in English (MIL-013, ADR-0012).

Run by .gitea/workflows/english-comments.yml. It reads the comments and docstrings
of the source files of the languages of ADR-0010, joins the lines of one comment
block, and judges the block with ``langid`` (restricted to a few candidate
languages) after removing everything that is not a word: paths, options,
identifiers, numbers and the words of the allowed-words file. A block with fewer
than ``--min-words`` words left is not judged.

Usage:
    python tools/english_comments.py check [--directory DIR] [--scope changed|all]
        [--base REF] [--exclude PATTERNS] [--allowed-words FILE]
        [--threshold P] [--min-words N] [--output FILE]

With ``--scope changed`` (the default) only the comments on lines that the
current branch added since ``--base`` (a git ref, for example ``origin/main``)
are checked, so a pull request is not blamed for a comment it did not write;
``--scope all`` checks every tracked file. A comment block that contains ``english-comments: ignore`` is
skipped (a quotation, a name).

Every finding is printed as ``::error file=PATH,line=N::...`` and as ``PATH:N:
looks Danish (0.93): "text"``; ``--output`` writes them as JSON for the
reporting step. Exit codes: 0 no finding, 1 at least one finding, 2 a setting
or a missing tool (printed as ``::error::[configuration] ...``).
"""

import argparse
import ast
import importlib.util
import io
import json
import re
import subprocess
import sys
import tokenize
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_THRESHOLD = 0.6
DEFAULT_MIN_WORDS = 3
MAX_FILE_BYTES = 1_000_000
CANDIDATES = ["en", "da", "no", "sv", "de", "fr", "ms", "id", "nl"]
LANGUAGE_NAMES = {
    "da": "Danish",
    "no": "Norwegian",
    "sv": "Swedish",
    "de": "German",
    "fr": "French",
    "ms": "Malay",
    "id": "Indonesian",
    "nl": "Dutch",
}
IGNORE_MARKER = re.compile(r"english-comments:\s*ignore", re.IGNORECASE)
# comments that configure a tool are not prose
_PRAGMA = re.compile(
    r"^(noqa|type:|pragma|shellcheck|fmt:|pylint|ruff:|mypy:|pyright:|eslint|prettier|"
    r"-\*-|vim:|coding[:=]|nosec|isort:|nolint|clang-format|cppcheck|lint:)",
    re.IGNORECASE,
)
_WORD = re.compile(r"^[^\W\d_]+(?:'[^\W\d_]+)?$")
_NOT_WORD_CHARS = re.compile(r"[\d_/\{}\[\]\"`=<>|$@#%&+^~*]")
_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


class CheckError(RuntimeError):
    """A setting or tool problem (exit code 2)."""


def _load_sibling(name: str):
    path = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


count_loc = _load_sibling("count_loc")


@dataclass(frozen=True)
class Finding:
    """A comment block that is probably not English."""

    path: str
    line: int
    end_line: int
    language: str
    probability: float
    text: str


def _clean(text: str) -> str:
    """Remove comment decoration (``*``, ``/``, ``#``, ``-``, ``=``) from both ends."""
    text = re.sub(r"^[/*!#<>=\-\s]+", "", text.strip())
    return re.sub(r"[*/\s]+$", "", text).strip()


def _python_comments(source: str) -> list[tuple[int, str]]:
    """Comments (tokenizer) and docstring lines (ast) of a Python file."""
    found: list[tuple[int, str]] = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            found.append((token.start[0], _clean(token.string)))
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            first = node.body[0] if node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                for offset, line in enumerate(first.value.value.splitlines()):
                    found.append((first.value.lineno + offset, _clean(line)))
    return found


def _scanned_comments(text: str, language) -> list[tuple[int, str]]:
    """Comments of any other language, from the scanner of the code counter."""
    state = count_loc._State()
    found: list[tuple[int, str]] = []
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for number, line in enumerate(lines, start=1):
        pieces: list[str] = []
        count_loc._scan_line(line, language, state, pieces)
        if number == 1 and pieces and pieces[0].startswith("!"):
            pieces = pieces[1:]  # a shebang line is not a comment
        joined = " ".join(_clean(piece) for piece in pieces).strip()
        if joined:
            found.append((number, joined))
    return found


def extract(path: str, text: str) -> list[tuple[int, str]]:
    """Return (line, text) for every comment line of a source file, sorted by line.

    A file of a language the code counter does not know has no comments here.
    """
    language = count_loc.language_of(path)
    if language is None:
        return []
    if language.name == "Python":
        try:
            found = _python_comments(text)
        except (SyntaxError, tokenize.TokenError):
            found = _scanned_comments(text, language)
    else:
        found = _scanned_comments(text, language)
    return sorted((n, t) for n, t in found if t and not _PRAGMA.match(t))


def blocks(lines: list[tuple[int, str]]) -> list[tuple[int, int, str]]:
    """Join comment lines on consecutive line numbers: (first line, last line, text)."""
    joined: list[tuple[int, int, str]] = []
    for number, text in lines:
        if joined and joined[-1][1] in (number, number - 1):
            first, _, previous = joined[-1]
            joined[-1] = (first, number, f"{previous} {text}")
        else:
            joined.append((number, number, text))
    return joined


def words(text: str, allowed: frozenset[str] = frozenset()) -> list[str]:
    """The words of a comment: no URLs, paths, options, identifiers or allowed words."""
    out: list[str] = []
    tokens = text.split()
    if tokens and tokens[0].endswith(":") and tokens[0][:-1].isalpha():
        tokens = tokens[1:]  # a label such as "Usage:" or "Note:" is not prose
    for token in tokens:
        if len(token) > 1 and token[0] == "." and token[1].isalpha():
            continue  # a hidden file such as .clang-format
        token = token.strip("().,;:!?")
        # a token with code characters (quotes, braces, `=`, `/`, `_`, digits) is not a word
        if not token or _NOT_WORD_CHARS.search(token) or "::" in token:
            continue
        if token.startswith("-") or "." in token or (len(token) > 1 and token.isupper()):
            continue  # an option, a file name, an acronym or a constant
        if re.search(r"[a-z][A-Z]", token):
            continue
        for part in token.split("-"):
            if len(part) > 1 and _WORD.match(part) and part.lower() not in allowed:
                out.append(part)
    return out


_identifier = None


def _identifier_model():
    global _identifier
    if _identifier is None:
        try:
            from langid.langid import LanguageIdentifier, model
        except ImportError:
            raise CheckError("langid is not installed (pip install langid==1.1.6).") from None
        _identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        _identifier.set_languages(CANDIDATES)
    return _identifier


def judge(
    text: str,
    allowed: frozenset[str] = frozenset(),
    threshold: float = DEFAULT_THRESHOLD,
    min_words: int = DEFAULT_MIN_WORDS,
) -> tuple[str, float] | None:
    """Return (language code, probability) when the text is not English, else None."""
    kept = words(text, allowed)
    if len(kept) < min_words:
        return None
    code, probability = _identifier_model().classify(" ".join(kept))
    if code != "en" and probability >= threshold:
        return code, float(probability)
    return None


def check_text(
    path: str,
    text: str,
    lines: set[int] | None = None,
    allowed: frozenset[str] = frozenset(),
    threshold: float = DEFAULT_THRESHOLD,
    min_words: int = DEFAULT_MIN_WORDS,
) -> list[Finding]:
    """Findings of one file; with ``lines`` only the blocks that touch those line numbers."""
    findings: list[Finding] = []
    for first, last, body in blocks(extract(path, text)):
        if IGNORE_MARKER.search(body):
            continue
        if lines is not None and not any(first <= n <= last for n in lines):
            continue
        verdict = judge(body, allowed, threshold, min_words)
        if verdict:
            findings.append(Finding(path, first, last, verdict[0], round(verdict[1], 2), body))
    return findings


def read_allowed_words(path: str | None) -> frozenset[str]:
    """Words, one per line, ``#`` starts a comment; the file may be missing only when not named."""
    if not path:
        return frozenset()
    try:
        content = Path(path).read_text(encoding="utf-8")
    except OSError:
        raise CheckError(f"allowed-words file '{path}' cannot be read.") from None
    return frozenset(
        line.split("#", 1)[0].strip().lower()
        for line in content.splitlines()
        if line.split("#", 1)[0].strip()
    )


def _git(directory: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=off", *args],
        cwd=directory,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        raise CheckError(f"git {' '.join(args[:2])} failed: {result.stderr.strip()[:200]}")
    return result.stdout


def changed_lines(directory: Path, base: str) -> dict[str, set[int]]:
    """Added or changed line numbers per file since the merge base with ``base``."""
    out = _git(directory, "diff", "-U0", "--no-color", "--diff-filter=ACMR", f"{base}...HEAD")
    result: dict[str, set[int]] = {}
    current: set[int] | None = None
    for line in out.splitlines():
        if line.startswith("+++ "):
            name = line[4:]
            current = result.setdefault(name[2:], set()) if name.startswith("b/") else None
            continue
        hunk = _HUNK.match(line)
        if hunk and current is not None:
            start = int(hunk.group(1))
            size = int(hunk.group(2)) if hunk.group(2) is not None else 1
            current.update(range(start, start + size))
    return result


def tracked_files(directory: Path) -> list[str]:
    return [name for name in _git(directory, "ls-files").splitlines() if name]


def _excluded(path: str, excludes) -> bool:
    parts = path.split("/")
    if any(part in count_loc.DEFAULT_EXCLUDED_DIRS for part in parts[:-1]):
        return True
    return excludes.matches(parts[-1], path)


def check_repository(
    directory: Path,
    base: str | None,
    check_all: bool,
    patterns: list[str],
    allowed: frozenset[str],
    threshold: float,
    min_words: int,
) -> tuple[list[Finding], int]:
    """Return (findings, number of files read)."""
    excludes = count_loc.Excludes(patterns)
    if check_all:
        selection: dict[str, set[int] | None] = {name: None for name in tracked_files(directory)}
    else:
        if not base:
            raise CheckError("give --base (a git ref such as origin/main) or --all.")
        selection = dict(changed_lines(directory, base))
    findings: list[Finding] = []
    read = 0
    for name in sorted(selection):
        if count_loc.language_of(name) is None or _excluded(name, excludes):
            continue
        target = directory / name
        if not target.is_file() or target.stat().st_size > MAX_FILE_BYTES:
            continue
        data = target.read_bytes()
        if not count_loc._is_text(data):
            continue
        read += 1
        text = data.decode("utf-8", errors="replace")
        findings += check_text(name, text, selection[name], allowed, threshold, min_words)
    return findings, read


def describe(finding: Finding) -> str:
    name = LANGUAGE_NAMES.get(finding.language, finding.language)
    shown = finding.text if len(finding.text) <= 120 else finding.text[:117] + "..."
    return f'looks {name} ({finding.probability}): "{shown}"'


def _split(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,\n]", value) if item.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check that source code comments are in English.")
    parser.add_argument("command", choices=["check"])
    parser.add_argument("--directory", default=".")
    parser.add_argument("--base", default="")
    parser.add_argument("--scope", choices=["changed", "all"], default="changed")
    parser.add_argument("--exclude", default="")
    parser.add_argument("--allowed-words", default="")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--min-words", type=int, default=DEFAULT_MIN_WORDS)
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    try:
        if not 0.0 < args.threshold <= 1.0 or args.min_words < 1:
            raise CheckError("threshold must be above 0 and at most 1, and min-words at least 1.")
        directory = Path(args.directory)
        if not directory.is_dir():
            raise CheckError(f"directory '{args.directory}' does not exist.")
        allowed = read_allowed_words(args.allowed_words or None)
        findings, files = check_repository(
            directory,
            args.base or None,
            args.scope == "all",
            _split(args.exclude),
            allowed,
            args.threshold,
            args.min_words,
        )
    except CheckError as error:
        print(f"::error::[configuration] {error}")
        return 2
    for finding in findings:
        message = describe(finding)
        print(f"::error file={finding.path},line={finding.line}::[english-comments] {message}")
        print(f"{finding.path}:{finding.line}: {message}")
    if args.output:
        Path(args.output).write_text(
            json.dumps([asdict(f) for f in findings], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    summary = f"{len(findings)} comment(s) not in English in {files} file(s) checked."
    print(summary if findings else f"All comments are in English: {files} file(s) checked.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
