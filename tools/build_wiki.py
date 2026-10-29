"""Build the English wiki pages in ``docs/wiki/`` from ``README.md`` and ``guides/``.

The wiki source lives in this repository (MIL-005). The English pages are
generated, never edited by hand; ``--check`` reports a page that differs from
what its sources produce.

Usage:
    python tools/build_wiki.py            # write the pages
    python tools/build_wiki.py --check    # exit 1 when a page is out of date
"""

import argparse
import hashlib
import posixpath
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = REPO_ROOT / "docs" / "wiki"
SOURCE_BASE_URL = "https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main"
GENERATOR = "tools/build_wiki.py"

# Leading emoji and symbols in README headings; removed so anchors stay stable.
_HEADING_SYMBOLS = re.compile(r"^(#{1,6})[ \t]+[←-\U0001FAFF️‍]+[ \t]*")
_FENCE = re.compile(r"^[ \t]*(```|~~~)")
_LINK_TARGET = re.compile(r"\]\(([^)\s]+)\)")
_H2 = re.compile(r"^##[ \t]+(.*?)[ \t]*$")


@dataclass(frozen=True)
class Page:
    """One generated wiki page."""

    name: str
    source: str
    sections: tuple[str, ...] | None = None  # H2 titles to keep; None keeps the file


PAGES: tuple[Page, ...] = (
    Page("Home", "README.md", ("Overview", "Workflows", "Requirements", "Setup", "Run", "Tests")),
    Page("Onboarding", "guides/onboarding.md"),
    Page("Credentials", "guides/credentials.md"),
    Page("Troubleshooting", "guides/troubleshooting.md"),
    Page("QualityChecksPythonShell", "guides/quality-checks.md"),
    Page("QualityChecksCpp", "guides/quality-checks-cpp.md"),
    Page("QualityChecksCSharp", "guides/quality-checks-csharp.md"),
    Page("CodeMetrics", "guides/code-metrics.md"),
    Page("EnglishComments", "guides/english-comments.md"),
    Page("OpenGrep", "guides/opengrep.md"),
    Page("Validate", "guides/validate.md"),
    Page("SyncMilestones", "guides/sync-milestones.md"),
    Page("Upgrading", "guides/upgrading.md"),
    Page("Capabilities", "README.md", ("Capabilities",)),
)

# Translations (ADR-0011): `<Page>-<code>` written by hand in docs/wiki/.
LANGUAGES: tuple[tuple[str, str], ...] = (("da", "Dansk"), ("ms", "Bahasa Melayu"))
HASH_LENGTH = 12
_TRANSLATION_HEADER = re.compile(
    r"^<!-- translation of (?P<page>\S+)\.md, source sha256 (?P<hash>[0-9a-f]+) -->$"
)

# The page a link to a source file should point to. The README is the home page.
_PAGE_FOR_SOURCE = {
    "README.md": "Home",
    "guides/onboarding.md": "Onboarding",
    "guides/credentials.md": "Credentials",
    "guides/troubleshooting.md": "Troubleshooting",
    "guides/quality-checks.md": "QualityChecksPythonShell",
    "guides/quality-checks-cpp.md": "QualityChecksCpp",
    "guides/quality-checks-csharp.md": "QualityChecksCSharp",
    "guides/code-metrics.md": "CodeMetrics",
    "guides/english-comments.md": "EnglishComments",
    "guides/opengrep.md": "OpenGrep",
    "guides/validate.md": "Validate",
    "guides/sync-milestones.md": "SyncMilestones",
    "guides/upgrading.md": "Upgrading",
}


class WikiBuildError(RuntimeError):
    """A source file or section needed for a page is missing."""


def strip_heading_symbols(line: str) -> str:
    """Remove the leading emoji from a heading line."""
    return _HEADING_SYMBOLS.sub(r"\1 ", line)


def rewrite_link(target: str, source: str) -> str:
    """Return the wiki form of a link target found in ``source``.

    Links to another generated page become wiki page links. Links to other
    repository files become absolute links to the file on ``main``, because the
    wiki has no copy of them. External links are unchanged.
    """
    if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
        return target
    path, hash_mark, fragment = target.partition("#")
    if not path:
        return "#" + fragment.lstrip("-")
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
    suffix = f"#{fragment}" if hash_mark else ""
    page = _PAGE_FOR_SOURCE.get(resolved)
    if page is not None:
        return page + suffix
    return f"{SOURCE_BASE_URL}/{resolved}{suffix}"


def convert_markdown(text: str, source: str) -> str:
    """Strip heading emoji and rewrite links, leaving fenced code untouched."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        line = strip_heading_symbols(line)
        line = _LINK_TARGET.sub(
            lambda match: f"]({rewrite_link(match.group(1), source)})", line
        )
        out.append(line)
    return "\n".join(out)


def split_h2_sections(text: str) -> tuple[list[str], dict[str, list[str]]]:
    """Return the lines before the first H2 and the lines of each H2 section.

    A section keeps its heading line and everything up to the next H2, so its
    H3 and deeper headings stay with it. Fenced code is not scanned.
    """
    preamble: list[str] = []
    sections: dict[str, list[str]] = {}
    current: list[str] = preamble
    in_fence = False
    for line in text.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
        match = None if in_fence else _H2.match(line)
        if match:
            title = _HEADING_SYMBOLS.sub("## ", line)[3:].strip()
            current = sections.setdefault(title, [])
        current.append(line)
    return preamble, sections


def language_switcher(page_name: str, current: str | None = None) -> str:
    """Return the line that links a page to its other languages (QC-WIKI-001).

    The current language is bold; ``current`` is a language code, or None for
    the English page.
    """
    items = ["**English**" if current is None else f"[English]({page_name})"]
    for code, label in LANGUAGES:
        items.append(f"**{label}**" if code == current else f"[{label}]({page_name}-{code})")
    return " · ".join(items)


def source_hash(content: bytes) -> str:
    """Return the short content hash a translation records for its source."""
    return hashlib.sha256(content).hexdigest()[:HASH_LENGTH]


def render_page(page: Page, repo_root: Path = REPO_ROOT) -> str:
    """Return the full Markdown of one wiki page."""
    source_path = repo_root / page.source
    try:
        text = source_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise WikiBuildError(f"{page.name}: source {page.source} is missing") from None

    if page.sections is None:
        body_lines = text.splitlines()
    else:
        preamble, sections = split_h2_sections(text)
        body_lines = list(preamble) if page.name == "Home" else []
        for title in page.sections:
            if title not in sections:
                raise WikiBuildError(
                    f"{page.name}: section '{title}' not found in {page.source}"
                )
            body_lines += [""] + sections[title]

    banner = (
        f"<!-- Generated from {page.source} by {GENERATOR}. "
        "Edit the source, not this page. -->\n\n"
        f"> This page is generated from [`{page.source}`]"
        f"({SOURCE_BASE_URL}/{page.source}). Changes made here are overwritten "
        "the next time the wiki is published.\n\n"
        f"{language_switcher(page.name)}\n\n"
    )
    body = convert_markdown("\n".join(body_lines), page.source).strip("\n")
    return banner + body + "\n"


# Sidebar (QC-WIKI-001): the title, one list of the English pages, the related
# wikis, and the languages last.
SIDEBAR_TITLE = "git-workflows"
SIDEBAR_LABELS: tuple[str, ...] = (
    "Home",
    "Onboarding",
    "Credentials",
    "Troubleshooting",
    "Quality checks (Python, shell)",
    "Quality checks (C and C++)",
    "Quality checks (C#)",
    "Code metrics",
    "English comments",
    "OpenGrep",
    "Validate",
    "Sync milestones",
    "Upgrading",
    "Capabilities",
)
SIDEBAR_RELATED: tuple[tuple[str, str], ...] = (
    ("Framework wiki", "https://git.tirsystem.com/TirSystem/sqa-qc-framework/wiki"),
)
# The word for "Home" in each language, the text of its link in `Languages`.
HOME_LABELS = {"da": "Hjem", "ms": "Utama"}
SIDEBAR_NAME = "_Sidebar.md"


def render_sidebar() -> str:
    """Return the navigation shown beside every wiki page.

    Gitea lists subpages only through a ``_Sidebar`` page, so without it a
    visitor sees the home page and no way to the others. The page list appears
    once; a translation's pages are reached from its Home and its language line.
    """
    assert len(SIDEBAR_LABELS) == len(PAGES), "one sidebar label per page"
    lines = [
        f"<!-- Generated by {GENERATOR}. Edit the generator, not this page. -->",
        "",
        f"**{SIDEBAR_TITLE}**",
        "",
    ]
    lines += [f"- [{text}]({page.name})" for text, page in zip(SIDEBAR_LABELS, PAGES)]
    if SIDEBAR_RELATED:
        lines += ["", "**Related**", ""]
        lines += [f"- [{text}]({url})" for text, url in SIDEBAR_RELATED]
    lines += ["", "**Languages**", "", "- English: [Home](Home)"]
    lines += [f"- {label}: [{HOME_LABELS[code]}](Home-{code})" for code, label in LANGUAGES]
    return chr(10).join(lines) + chr(10)


def build_all(repo_root: Path = REPO_ROOT) -> dict[str, str]:
    """Return ``{file name: content}`` for every English page and the sidebar."""
    pages = {f"{page.name}.md": render_page(page, repo_root) for page in PAGES}
    pages[SIDEBAR_NAME] = render_sidebar()
    return pages


def write_pages(wiki_dir: Path = WIKI_DIR, repo_root: Path = REPO_ROOT) -> list[str]:
    """Write every page; return the names of the files that changed."""
    changed: list[str] = []
    wiki_dir.mkdir(parents=True, exist_ok=True)
    for name, content in build_all(repo_root).items():
        path = wiki_dir / name
        current = path.read_bytes() if path.exists() else None
        if current != content.encode("utf-8"):
            path.write_bytes(content.encode("utf-8"))
            changed.append(name)
    return changed


def check_pages(wiki_dir: Path = WIKI_DIR, repo_root: Path = REPO_ROOT) -> list[str]:
    """Return a message for every page that is missing or out of date."""
    problems: list[str] = []
    for name, content in build_all(repo_root).items():
        path = wiki_dir / name
        if not path.exists():
            problems.append(f"{name}: missing")
        elif path.read_bytes() != content.encode("utf-8"):
            problems.append(f"{name}: differs from its source")
    return problems


def check_translations(
    wiki_dir: Path = WIKI_DIR, repo_root: Path = REPO_ROOT
) -> list[str]:
    """Return a message for every translation that is missing or stale.

    A translation is stale when the hash it records no longer matches the
    English page it follows (the English page changed after it was written).
    """
    problems: list[str] = []
    english = build_all(repo_root)
    for page in PAGES:
        current = source_hash(english[f"{page.name}.md"].encode("utf-8"))
        for code, _label in LANGUAGES:
            name = f"{page.name}-{code}.md"
            path = wiki_dir / name
            if not path.exists():
                problems.append(f"{name}: missing")
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            match = _TRANSLATION_HEADER.match(lines[0]) if lines else None
            if match is None or match.group("page") != page.name:
                problems.append(f"{name}: first line is not the translation header")
            elif match.group("hash") != current:
                problems.append(
                    f"{name}: stale, follows {match.group('hash')} but "
                    f"{page.name}.md is {current}"
                )
    return problems


def main(argv: list[str] | None = None) -> int:
    """Run the generator; return the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="report pages that differ from their sources or stale translations, exit 1",
    )
    parser.add_argument(
        "--hash",
        metavar="PAGE",
        help="print the source hash a translation of PAGE must record",
    )
    args = parser.parse_args(argv)
    try:
        if args.hash:
            content = build_all().get(f"{args.hash}.md")
            if content is None:
                raise WikiBuildError(f"unknown page '{args.hash}'")
            print(source_hash(content.encode("utf-8")))
            return 0
        if args.check:
            problems = check_pages() + check_translations()
            for problem in problems:
                print(f"ERROR: docs/wiki/{problem}", file=sys.stderr)
            if problems:
                print(f"Run `python {GENERATOR}` and commit docs/wiki/.", file=sys.stderr)
                return 1
            print("Wiki pages are up to date.")
            return 0
        changed = write_pages()
    except WikiBuildError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {len(changed)} page(s): {', '.join(changed) or 'none changed'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
