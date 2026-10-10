"""Build the English wiki pages in ``wiki/`` from ``README.md`` and ``guides/``.

The wiki source lives in this repository (MIL-005). The English pages are
generated, never edited by hand; ``--check`` reports a page that differs from
what its sources produce.

Usage:
    python tools/build_wiki.py            # write the pages
    python tools/build_wiki.py --check    # exit 1 when a page is out of date
"""

import argparse
import posixpath
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
SOURCE_BASE_URL = "https://git.tirsystem.com/TirSystem/github-action/src/branch/main"
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
    Page("Home", "README.md", ("Overview", "Requirements", "Setup", "Run", "Tests")),
    Page("Onboarding", "guides/onboarding.md"),
    Page("Credentials", "guides/credentials.md"),
    Page("Troubleshooting", "guides/troubleshooting.md"),
    Page("Capabilities", "README.md", ("Capabilities",)),
)

# The page a link to a source file should point to. The README is the home page.
_PAGE_FOR_SOURCE = {
    "README.md": "Home",
    "guides/onboarding.md": "Onboarding",
    "guides/credentials.md": "Credentials",
    "guides/troubleshooting.md": "Troubleshooting",
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
    )
    body = convert_markdown("\n".join(body_lines), page.source).strip("\n")
    return banner + body + "\n"


def build_all(repo_root: Path = REPO_ROOT) -> dict[str, str]:
    """Return ``{file name: content}`` for every English page."""
    return {f"{page.name}.md": render_page(page, repo_root) for page in PAGES}


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


def main(argv: list[str] | None = None) -> int:
    """Run the generator; return the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="report pages that differ from their sources and exit 1",
    )
    args = parser.parse_args(argv)
    try:
        if args.check:
            problems = check_pages()
            for problem in problems:
                print(f"ERROR: wiki/{problem}", file=sys.stderr)
            if problems:
                print(f"Run `python {GENERATOR}` and commit wiki/.", file=sys.stderr)
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
