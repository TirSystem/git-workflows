"""Offline tests for tools/changelog.py and the CHANGELOG.md of this repository."""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_SPEC = importlib.util.spec_from_file_location("changelog", REPO_ROOT / "tools" / "changelog.py")
assert _SPEC is not None and _SPEC.loader is not None
changelog = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(changelog)

GOOD = """# Changelog

## [Unreleased]

### Added

- A new optional input.

## [2.0.0] - 2026-12-01

### Breaking

- The input `languages` was renamed.

### Fixed

- A message.

## [1.1.0] - 2026-11-01

### Added

- A workflow.

## [1.0.0] - 2026-10-20

### Added

- The first release.
"""


class TestParse:
    def test_reads_releases_groups_and_items(self):
        releases = changelog.parse(GOOD)
        assert [r.name for r in releases] == ["Unreleased", "2.0.0", "1.1.0", "1.0.0"]
        assert releases[1].version == (2, 0, 0)
        assert releases[1].date == "2026-12-01"
        assert releases[1].groups["Breaking"] == ["The input `languages` was renamed."]
        assert releases[0].is_unreleased and releases[0].version is None


class TestValidate:
    def test_a_correct_changelog_has_no_problem(self):
        assert changelog.validate(GOOD) == []

    def test_requires_unreleased_first(self):
        text = GOOD.replace("## [Unreleased]\n\n### Added\n\n- A new optional input.\n\n", "")
        assert any("first section must be `## [Unreleased]`" in p for p in changelog.validate(text))

    def test_rejects_an_unknown_group(self):
        text = GOOD.replace("### Fixed", "### Misc")
        assert any("group 'Misc'" in p for p in changelog.validate(text))

    def test_rejects_an_empty_group(self):
        text = GOOD.replace("- A message.\n", "")
        assert any("has no item" in p for p in changelog.validate(text))

    def test_rejects_a_release_without_a_date(self):
        text = GOOD.replace("## [1.1.0] - 2026-11-01", "## [1.1.0]")
        assert any("needs a date" in p for p in changelog.validate(text))

    def test_rejects_a_name_that_is_not_a_version(self):
        text = GOOD.replace("## [1.1.0] - 2026-11-01", "## [v1.1] - 2026-11-01")
        assert any("not a version" in p for p in changelog.validate(text))

    def test_versions_must_descend(self):
        text = GOOD.replace("## [1.1.0]", "## [2.0.0]")
        assert any("must be lower than the version above" in p for p in changelog.validate(text))

    def test_breaking_needs_a_new_major(self):
        text = GOOD.replace("## [1.1.0] - 2026-11-01\n\n### Added\n\n- A workflow.",
                            "## [1.1.0] - 2026-11-01\n\n### Breaking\n\n- A rename.")
        assert any("lists Breaking changes but the major version does not increase" in p
                   for p in changelog.validate(text))

    def test_a_new_major_needs_a_breaking_change(self):
        text = GOOD.replace("### Breaking\n\n- The input `languages` was renamed.\n\n### Fixed",
                            "### Fixed")
        assert any("raises the major version but lists no Breaking change" in p
                   for p in changelog.validate(text))

    def test_an_empty_file_is_a_problem(self):
        assert changelog.validate("# Changelog\n")


class TestNotes:
    def test_prints_the_groups_in_the_fixed_order(self):
        text = changelog.notes(GOOD, "2.0.0")
        assert text.startswith("## 2.0.0 - 2026-12-01")
        assert text.index("### Breaking") < text.index("### Fixed")
        assert "The input `languages` was renamed." in text

    def test_an_unknown_version_is_an_error(self):
        with pytest.raises(LookupError):
            changelog.notes(GOOD, "3.0.0")


class TestCommandLine:
    def test_check_passes_for_a_good_file(self, tmp_path, capsys):
        path = tmp_path / "CHANGELOG.md"
        path.write_text(GOOD, encoding="utf-8")
        assert changelog.main(["check", "--file", str(path)]) == 0

    def test_check_version_fails_without_an_entry(self, tmp_path, capsys):
        path = tmp_path / "CHANGELOG.md"
        path.write_text(GOOD, encoding="utf-8")
        assert changelog.main(["check", "--file", str(path), "--version", "3.0.0"]) == 1
        assert "no changelog entry" in capsys.readouterr().err

    def test_notes_prints_the_entry(self, tmp_path, capsys):
        path = tmp_path / "CHANGELOG.md"
        path.write_text(GOOD, encoding="utf-8")
        assert changelog.main(["notes", "1.1.0", "--file", str(path)]) == 0
        assert "A workflow." in capsys.readouterr().out


def test_the_changelog_of_this_repository_follows_the_convention():
    text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert changelog.validate(text) == []
    assert changelog.parse(text)[0].is_unreleased


def test_wrapped_item_is_one_item_in_the_notes():
    text = "## [Unreleased]\n\n## [1.0.0] - 2026-10-10\n\n### Added\n\n- A long item that\n  continues here.\n- Next.\n"
    assert changelog.parse(text)[1].groups["Added"] == ["A long item that continues here.", "Next."]
    assert "- A long item that continues here.\n" in changelog.notes(text, "1.0.0")


FRAMEWORK = (REPO_ROOT / "tests" / "fixtures" / "framework-changelog.md").read_text(encoding="utf-8")


class TestFrameworkFormat:
    """The heading `## 0.18.0 (2026-10-28)` of the framework repository."""

    def test_reads_plain_headings_and_both_unreleased_spellings(self):
        releases = changelog.parse(FRAMEWORK)
        assert [r.name for r in releases] == ["Unreleased", "0.18.0", "0.17.1"]
        assert releases[1].date == "2026-10-28" and releases[1].version == (0, 18, 0)
        assert releases[1].plain and releases[0].is_unreleased
        assert changelog.parse("## [Unreleased]\n")[0].is_unreleased

    def test_a_framework_changelog_is_correct(self):
        assert changelog.validate(FRAMEWORK) == []

    def test_notes_are_the_section_text(self):
        text = changelog.notes(FRAMEWORK, "0.18.0")
        assert text.startswith("## 0.18.0 (2026-10-28)\n")
        assert "A minor release" in text and "### Changed" in text
        assert "0.17.1" not in text and text.endswith("\n")

    def test_a_group_name_is_free(self):
        assert changelog.validate(FRAMEWORK.replace("### Changed", "### Misc")) == []

    def test_a_heading_without_a_date_is_a_problem(self):
        problems = changelog.validate(FRAMEWORK.replace("## 0.17.1 (2026-10-27)", "## 0.17.1"))
        assert any("needs a date, `## 0.17.1 (YYYY-MM-DD)`" in p for p in problems)

    def test_a_heading_that_is_not_a_version_is_a_problem(self):
        problems = changelog.validate(FRAMEWORK.replace("## 0.17.1 (2026-10-27)", "## v0.17 (2026-10-27)"))
        assert any("not a version" in p for p in problems)

    def test_versions_must_descend(self):
        problems = changelog.validate(FRAMEWORK.replace("## 0.17.1", "## 0.19.0"))
        assert any("must be lower than the version above" in p for p in problems)

    def test_a_duplicate_version_is_a_problem(self):
        problems = changelog.validate(FRAMEWORK.replace("## 0.17.1", "## 0.18.0"))
        assert any("duplicate version" in p for p in problems)

    def test_an_empty_body_is_a_problem_and_has_no_notes(self):
        text = FRAMEWORK.rstrip() + "\n\n## 0.17.0 (2026-10-01)\n"
        assert any("[0.17.0] has no text" in p for p in changelog.validate(text))
        with pytest.raises(LookupError):
            changelog.notes(text, "0.17.0")

    def test_a_major_without_breaking_group_is_allowed(self):
        text = "## Unreleased\n\n## 1.0.0 (2026-10-02)\n\nText.\n\n## 0.9.0 (2026-10-01)\n\nText.\n"
        assert changelog.validate(text) == []

    def test_the_file_may_start_without_unreleased(self):
        assert changelog.validate("## 0.1.0 (2026-10-01)\n\nText.\n") == []

    def test_check_version_reads_the_framework_format(self, tmp_path):
        path = tmp_path / "CHANGELOG.md"
        path.write_text(FRAMEWORK, encoding="utf-8")
        assert changelog.main(["check", "--file", str(path), "--version", "0.18.0"]) == 0
        assert changelog.main(["check", "--file", str(path), "--version", "0.19.0"]) == 1

    def test_notes_command_prints_the_section(self, tmp_path, capsys):
        path = tmp_path / "CHANGELOG.md"
        path.write_text(FRAMEWORK, encoding="utf-8")
        assert changelog.main(["notes", "0.17.1", "--file", str(path)]) == 0
        assert "A broken link in the wiki." in capsys.readouterr().out
