"""Read, check and cut release notes from CHANGELOG.md (ADR-0006).

The changelog follows the convention of the release process in one of two
heading formats (ADR-0017); a file may use either:

    ## [Unreleased]                  keep-a-changelog format
    ### Breaking | Added | Changed | Fixed
    ## [1.2.0] - 2026-10-10

    ## Unreleased                    framework format (also `## [Unreleased]`)
    ## 0.18.0 (2026-10-28)           free text and any ### groups below it

The framework format is checked for the heading (semantic version and date),
descending order, a non-empty body and no duplicate version only.

Usage:
    python tools/changelog.py check [--file CHANGELOG.md]
    python tools/changelog.py notes 1.2.0 [--file CHANGELOG.md]
    python tools/changelog.py check --version 1.2.0     # the entry must exist

Exit codes: 0 correct, 1 a problem was found (each is printed).
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GROUPS = ("Breaking", "Added", "Changed", "Fixed")

_RELEASE = re.compile(r"^## \[(?P<name>[^\]]+)\](?: - (?P<date>\d{4}-\d{2}-\d{2}))?\s*$")
_PLAIN_RELEASE = re.compile(r"^## (?P<name>[^\s(\[]+)(?: \((?P<date>\d{4}-\d{2}-\d{2})\))?\s*$")
_GROUP = re.compile(r"^### (?P<name>.+?)\s*$")
_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


@dataclass
class Release:
    """One `## [x]` section of the changelog."""

    name: str
    date: str | None
    line: int
    groups: dict[str, list[str]] = field(default_factory=dict)
    plain: bool = False  # True for the framework format `## 0.18.0 (date)`
    heading: str = ""
    body: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """The entry says something: change groups (bracket format) or any text (plain format)."""
        if self.plain:
            return any(line.strip() for line in self.body)
        return bool(self.groups)

    @property
    def version(self) -> tuple[int, int, int] | None:
        match = _SEMVER.match(self.name)
        return tuple(int(part) for part in match.groups()) if match else None  # type: ignore[return-value]

    @property
    def is_unreleased(self) -> bool:
        return self.name == "Unreleased"


def parse(text: str) -> list[Release]:
    """Return the releases in file order; text before the first one is ignored."""
    releases: list[Release] = []
    group: str | None = None
    for number, line in enumerate(text.splitlines(), 1):
        release = _RELEASE.match(line)
        plain = None if release else _PLAIN_RELEASE.match(line)
        if release or plain:
            found = release or plain
            assert found is not None
            releases.append(Release(found["name"], found["date"], number, plain=plain is not None, heading=line.rstrip()))
            group = None
            continue
        if not releases:
            continue
        releases[-1].body.append(line)
        heading = _GROUP.match(line)
        if heading:
            group = heading["name"]
            releases[-1].groups.setdefault(group, [])
            continue
        if group is not None and line.startswith("- "):
            releases[-1].groups[group].append(line[2:].strip())
        elif group is not None and line.startswith("  ") and releases[-1].groups[group]:
            # a wrapped item: the lines that continue it belong to the same item
            releases[-1].groups[group][-1] += " " + line.strip()
    return releases


def _group_problems(release: Release, where: str) -> list[str]:
    problems: list[str] = []
    for group, items in release.groups.items():
        if group not in GROUPS:
            problems.append(f"{where}: group '{group}' is not one of {', '.join(GROUPS)}")
        if not items:
            problems.append(f"{where}: group '{group}' of [{release.name}] has no item")
    return problems


def _heading_example(release: Release) -> str:
    if release.plain:
        return f"`## {release.name} (YYYY-MM-DD)`"
    return f"`## [{release.name}] - YYYY-MM-DD`"


def validate(text: str) -> list[str]:
    """Return one message per breach of the convention."""
    problems: list[str] = []
    releases = parse(text)
    if not releases:
        return ["no release section: the file needs `## [Unreleased]` and one `## [x.y.z] - date` per release"]
    if not releases[0].plain and not releases[0].is_unreleased:
        problems.append(f"line {releases[0].line}: the first section must be `## [Unreleased]`")

    previous: tuple[int, int, int] | None = None
    seen: set[tuple[int, int, int]] = set()
    for release in releases:
        where = f"line {release.line}"
        if not release.plain:
            problems += _group_problems(release, where)
        if release.is_unreleased:
            if release.date:
                problems.append(f"{where}: [Unreleased] has no date")
            continue
        version = release.version
        if version is None:
            problems.append(f"{where}: '{release.name}' is not a version MAJOR.MINOR.PATCH")
            continue
        if not release.date:
            problems.append(f"{where}: [{release.name}] needs a date, {_heading_example(release)}")
        if not release.has_changes:
            problems.append(
                f"{where}: [{release.name}] has no text" if release.plain else f"{where}: [{release.name}] has no change group"
            )
        if previous is not None and version >= previous:
            duplicate = " (duplicate version)" if version in seen else ""
            problems.append(f"{where}: [{release.name}] must be lower than the version above it{duplicate}")
        seen.add(version)
        previous = version

    # a breaking entry needs a new major compared with the release before it
    # (keep-a-changelog format only; the framework format has free groups)
    released = [r for r in releases if not r.is_unreleased and r.version is not None and not r.plain]
    for newer, older in zip(released, released[1:]):
        if newer.groups.get("Breaking") and newer.version[0] <= older.version[0]:  # type: ignore[index]
            problems.append(
                f"line {newer.line}: [{newer.name}] lists Breaking changes but the major version "
                f"does not increase over [{older.name}]"
            )
        if (
            not newer.groups.get("Breaking")
            and newer.version[0] > older.version[0]  # type: ignore[index]
        ):
            problems.append(
                f"line {newer.line}: [{newer.name}] raises the major version but lists no Breaking change"
            )
    return problems


def notes(text: str, version: str) -> str:
    """Return the Markdown of the release page for ``version``."""
    for release in parse(text):
        if release.name == version:
            if not release.has_changes:
                break
            if release.plain:
                return "\n".join([release.heading, *release.body]).strip() + "\n"
            parts = [f"## {version}" + (f" - {release.date}" if release.date else "")]
            for group in GROUPS:
                items = release.groups.get(group)
                if items:
                    parts.append(f"### {group}\n" + "\n".join(f"- {item}" for item in items))
            return "\n\n".join(parts) + "\n"
    raise LookupError(f"no changelog entry with changes for version {version}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("check", "notes"))
    parser.add_argument("version", nargs="?", help="version for `notes`")
    parser.add_argument("--file", default=str(REPO_ROOT / "CHANGELOG.md"))
    parser.add_argument("--version", dest="must_have", help="for `check`: this version must have an entry")
    args = parser.parse_args(argv)

    text = Path(args.file).read_text(encoding="utf-8")
    if args.command == "notes":
        if not args.version:
            print("ERROR: `notes` needs a version", file=sys.stderr)
            return 1
        try:
            print(notes(text, args.version), end="")
        except LookupError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
        return 0

    problems = validate(text)
    if args.must_have and not any(r.name == args.must_have and r.has_changes for r in parse(text)):
        problems.append(f"no changelog entry with changes for version {args.must_have}")
    for problem in problems:
        print(f"ERROR: {args.file}: {problem}", file=sys.stderr)
    if not problems:
        print("CHANGELOG.md follows the convention.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
