"""Offline tests for tools/build_wiki.py."""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_SPEC = importlib.util.spec_from_file_location(
    "build_wiki", REPO_ROOT / "tools" / "build_wiki.py"
)
assert _SPEC is not None and _SPEC.loader is not None
build_wiki = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(build_wiki)

BASE = build_wiki.SOURCE_BASE_URL


class TestStripHeadingSymbols:
    @pytest.mark.parametrize(
        ("line", "expected"),
        [
            ("## 🧭 Overview", "## Overview"),
            ("## 🛠️ Setup", "## Setup"),
            ("## ▶️ Run", "## Run"),
            ("#### 🕒 Cron", "#### Cron"),
            ("## Plain", "## Plain"),
            ("## `code` heading", "## `code` heading"),
        ],
    )
    def test_removes_leading_emoji_only(self, line, expected):
        assert build_wiki.strip_heading_symbols(line) == expected


class TestRewriteLink:
    @pytest.mark.parametrize(
        ("target", "source", "expected"),
        [
            ("guides/credentials.md", "README.md", "Credentials"),
            ("guides/onboarding.md#runners", "README.md", "Onboarding#runners"),
            ("troubleshooting.md", "guides/credentials.md", "Troubleshooting"),
            ("onboarding.md#runners", "guides/troubleshooting.md", "Onboarding#runners"),
            ("#-requirements", "README.md", "#requirements"),
            ("#runners", "guides/onboarding.md", "#runners"),
            ("https://example.test/a", "README.md", "https://example.test/a"),
            ("mailto:a@example.test", "README.md", "mailto:a@example.test"),
            ("docs/project-plan.md", "README.md", f"{BASE}/docs/project-plan.md"),
            ("../docs/project-plan.md", "guides/onboarding.md", f"{BASE}/docs/project-plan.md"),
            (
                ".gitea/scoped_workflows/sync-github-metadata.yml",
                "README.md",
                f"{BASE}/.gitea/scoped_workflows/sync-github-metadata.yml",
            ),
            ("../README.md", "guides/onboarding.md", "Home"),
        ],
    )
    def test_rewrites_by_target_kind(self, target, source, expected):
        assert build_wiki.rewrite_link(target, source) == expected


class TestConvertMarkdown:
    def test_leaves_fenced_code_untouched(self):
        text = "## 🧭 Title\n```bash\n## 🧭 not a heading\n[x](guides/a.md)\n```\n"
        converted = build_wiki.convert_markdown(text, "README.md")
        assert converted.splitlines()[0] == "## Title"
        assert "## 🧭 not a heading" in converted
        assert "[x](guides/a.md)" in converted

    def test_rewrites_links_outside_code(self):
        text = "See [guide](guides/credentials.md) and [plan](docs/project-plan.md)."
        converted = build_wiki.convert_markdown(text, "README.md")
        assert f"[guide](Credentials) and [plan]({BASE}/docs/project-plan.md)" in converted


class TestSplitH2Sections:
    def test_keeps_subsections_and_ignores_h2_in_code(self):
        text = (
            "# Title\nintro\n"
            "## 🧭 One\na\n### Sub\nb\n"
            "## Two\n```\n## not a section\n```\n"
        )
        preamble, sections = build_wiki.split_h2_sections(text)
        assert preamble == ["# Title", "intro"]
        assert list(sections) == ["One", "Two"]
        assert "### Sub" in sections["One"]
        assert "## not a section" in sections["Two"]


def _write_sources(root: Path) -> None:
    (root / "guides").mkdir()
    (root / "README.md").write_text(
        "# 🚀 Name\nIntro.\n\n## 📚 Table of Contents\n- [x](#-overview)\n\n"
        "## 🧭 Overview\nSee [credentials](guides/credentials.md).\n\n"
        "## 📋 Requirements\nNeeds a runner.\n\n## 🛠️ Setup\nRun [it](#-requirements).\n\n"
        "## ▶️ Run\nGo.\n\n## 🧪 Tests\nPytest.\n\n## 🟢 Capabilities\nA table.\n\n"
        "### 🔄 Sync\nDetails.\n\n## 📄 License\nMIT.\n",
        encoding="utf-8",
    )
    for name in ("onboarding", "credentials", "troubleshooting"):
        (root / "guides" / f"{name}.md").write_text(
            f"# {name.title()}\nBody.\n", encoding="utf-8"
        )


class TestRenderPage:
    @pytest.fixture()
    def repo(self, tmp_path):
        _write_sources(tmp_path)
        return tmp_path

    def test_home_keeps_overview_to_tests_and_drops_the_rest(self, repo):
        home = build_wiki.render_page(build_wiki.PAGES[0], repo)
        assert "# Name" in home
        assert "## Overview" in home
        assert "[credentials](Credentials)" in home
        assert "Run [it](#requirements)." in home
        assert "Table of Contents" not in home
        assert "Capabilities" not in home
        assert "License" not in home

    def test_capabilities_page_keeps_its_subsections(self, repo):
        page = next(p for p in build_wiki.PAGES if p.name == "Capabilities")
        text = build_wiki.render_page(page, repo)
        assert "## Capabilities" in text
        assert "### Sync" in text
        assert "## Overview" not in text

    def test_every_page_names_its_source_and_warns(self, repo):
        for page in build_wiki.PAGES:
            text = build_wiki.render_page(page, repo)
            assert f"Generated from {page.source}" in text
            assert "overwritten" in text

    def test_missing_section_is_an_error(self, repo):
        (repo / "README.md").write_text("# Name\n", encoding="utf-8")
        with pytest.raises(build_wiki.WikiBuildError, match="section 'Overview'"):
            build_wiki.render_page(build_wiki.PAGES[0], repo)

    def test_missing_source_is_an_error(self, repo):
        (repo / "guides" / "onboarding.md").unlink()
        page = next(p for p in build_wiki.PAGES if p.name == "Onboarding")
        with pytest.raises(build_wiki.WikiBuildError, match="is missing"):
            build_wiki.render_page(page, repo)


class TestWriteAndCheck:
    @pytest.fixture()
    def repo(self, tmp_path):
        root = tmp_path / "repo"
        root.mkdir()
        _write_sources(root)
        return root

    def test_write_then_check_passes(self, repo, tmp_path):
        wiki = tmp_path / "wiki"
        changed = build_wiki.write_pages(wiki, repo)
        assert sorted(changed) == sorted(f"{p.name}.md" for p in build_wiki.PAGES)
        assert build_wiki.check_pages(wiki, repo) == []
        assert build_wiki.write_pages(wiki, repo) == []

    def test_check_reports_missing_and_changed_pages(self, repo, tmp_path):
        wiki = tmp_path / "wiki"
        build_wiki.write_pages(wiki, repo)
        (wiki / "Home.md").write_text("edited by hand\n", encoding="utf-8")
        (wiki / "Credentials.md").unlink()
        problems = build_wiki.check_pages(wiki, repo)
        assert "Home.md: differs from its source" in problems
        assert "Credentials.md: missing" in problems

    def test_check_detects_a_changed_source(self, repo, tmp_path):
        wiki = tmp_path / "wiki"
        build_wiki.write_pages(wiki, repo)
        (repo / "guides" / "onboarding.md").write_text("# Changed\n", encoding="utf-8")
        assert build_wiki.check_pages(wiki, repo) == [
            "Onboarding.md: differs from its source"
        ]


def test_committed_wiki_pages_are_current():
    """The pages in wiki/ match what README.md and guides/ produce."""
    assert build_wiki.check_pages() == []
