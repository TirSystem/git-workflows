"""Offline tests for tools/badges.py (ADR-0010): the coverage reader and the SVG renderer."""

import importlib.util
import json
import xml.etree.ElementTree as ElementTree
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
_SPEC = importlib.util.spec_from_file_location(
    "badges", REPO_ROOT / "tools" / "badges.py"
)
assert _SPEC is not None and _SPEC.loader is not None
badges = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(badges)

DTD = (
    '<!DOCTYPE coverage SYSTEM "http://cobertura.sourceforge.net/xml/coverage-04.dtd">'
)


def report(
    tmp_path: Path, attributes: str, root: str = "coverage", prolog: str = ""
) -> Path:
    path = tmp_path / "coverage.xml"
    path.write_text(
        f'<?xml version="1.0" ?>\n{prolog}<{root} {attributes}><packages/></{root}>\n'
    )
    return path


class TestReadCoverage:
    @pytest.mark.parametrize(
        ("covered", "valid", "percent"),
        [
            (0, 10, 0),
            (1, 3, 33),
            (2, 3, 67),
            (5, 8, 63),
            (87, 100, 87),
            (1, 200, 1),
            (10, 10, 100),
        ],
    )
    def test_percent_is_covered_over_valid_rounded_half_up(
        self, tmp_path, covered, valid, percent
    ):
        path = report(
            tmp_path, f'lines-covered="{covered}" lines-valid="{valid}" line-rate="0"'
        )
        assert badges.read_coverage(path) == percent

    def test_the_half_rounds_up(self, tmp_path):
        assert (
            badges.read_coverage(report(tmp_path, 'lines-covered="1" lines-valid="8"'))
            == 13
        )

    def test_line_rate_is_used_when_the_counts_are_absent(self, tmp_path):
        assert badges.read_coverage(report(tmp_path, 'line-rate="0.875"')) == 88

    def test_a_document_type_declaration_is_accepted(self, tmp_path):
        path = report(tmp_path, 'lines-covered="9" lines-valid="10"', prolog=DTD + "\n")
        assert badges.read_coverage(path) == 90

    def test_missing_file_names_the_file(self, tmp_path):
        with pytest.raises(badges.ConfigurationError, match="nope.xml' does not exist"):
            badges.read_coverage(tmp_path / "nope.xml")

    def test_malformed_xml_names_the_file(self, tmp_path):
        path = tmp_path / "bad.xml"
        path.write_text("<coverage lines-valid=")
        with pytest.raises(
            badges.ConfigurationError, match="bad.xml' is not well-formed"
        ):
            badges.read_coverage(path)

    def test_other_xml_is_not_a_cobertura_report(self, tmp_path):
        with pytest.raises(badges.ConfigurationError, match="not a Cobertura report"):
            badges.read_coverage(report(tmp_path, 'lines-valid="1"', root="testsuite"))

    def test_no_valid_lines_is_a_failure_and_not_zero_percent(self, tmp_path):
        with pytest.raises(badges.ConfigurationError, match="has no valid lines"):
            badges.read_coverage(report(tmp_path, 'lines-covered="0" lines-valid="0"'))

    def test_covered_above_valid_is_refused(self, tmp_path):
        with pytest.raises(badges.ConfigurationError, match="outside 0..lines-valid"):
            badges.read_coverage(report(tmp_path, 'lines-covered="5" lines-valid="4"'))

    def test_report_without_any_rate_is_refused(self, tmp_path):
        with pytest.raises(badges.ConfigurationError, match="neither lines-valid"):
            badges.read_coverage(report(tmp_path, 'branch-rate="1"'))

    def test_line_rate_outside_zero_to_one_is_refused(self, tmp_path):
        with pytest.raises(badges.ConfigurationError, match="outside 0..1"):
            badges.read_coverage(report(tmp_path, 'line-rate="1.5"'))

    def test_values_that_are_not_numbers_are_refused(self, tmp_path):
        with pytest.raises(badges.ConfigurationError, match="not a number"):
            badges.read_coverage(report(tmp_path, 'lines-covered="a" lines-valid="b"'))
        with pytest.raises(badges.ConfigurationError, match="not a number"):
            badges.read_coverage(report(tmp_path, 'line-rate="high"'))

    def test_entity_declarations_are_refused(self, tmp_path):
        prolog = '<!DOCTYPE coverage [<!ENTITY x "y">]>\n'
        with pytest.raises(badges.ConfigurationError, match="declares entities"):
            badges.read_coverage(
                report(tmp_path, 'lines-covered="1" lines-valid="2"', prolog=prolog)
            )


class TestColor:
    @pytest.mark.parametrize(
        ("percent", "color"),
        [
            (0, badges.RED),
            (59, badges.RED),
            (60, badges.YELLOW),
            (79, badges.YELLOW),
            (80, badges.GREEN),
            (100, badges.GREEN),
        ],
    )
    def test_thresholds_are_warn_and_good(self, percent, color):
        assert badges.coverage_color(percent, 60, 80) == color

    def test_thresholds_can_be_moved(self):
        assert badges.coverage_color(50, 40, 50) == badges.GREEN
        assert badges.coverage_color(39, 40, 50) == badges.RED


class TestRender:
    def test_is_valid_xml_with_title_and_text_alternative(self):
        svg = badges.render("code files", "1,234", badges.BLUE)
        root = ElementTree.fromstring(svg)
        ns = "{http://www.w3.org/2000/svg}"
        assert root.tag == ns + "svg"
        assert root.get("role") == "img"
        assert root.get("aria-label") == "code files: 1,234"
        assert root.find(ns + "title").text == "code files: 1,234"

    def test_same_input_gives_the_same_bytes_and_has_no_script_or_link(self):
        first = badges.render("coverage", "87%", badges.GREEN)
        assert first == badges.render("coverage", "87%", badges.GREEN)
        for forbidden in (
            "<script",
            "href",
            "<image",
            "<style",
            "http://www.w3.org/1999/xlink",
        ):
            assert forbidden not in first

    def test_width_follows_the_number_of_characters(self):
        narrow = ElementTree.fromstring(badges.render("a", "1", badges.BLUE)).get(
            "width"
        )
        wide = ElementTree.fromstring(badges.render("a", "1,000", badges.BLUE)).get(
            "width"
        )
        assert int(wide) - int(narrow) == 4 * badges.CHAR_WIDTH

    def test_text_is_escaped(self):
        svg = badges.render("a<b", 'c&"d', badges.BLUE)
        assert "a&lt;b" in svg and "c&amp;&quot;d" in svg
        ElementTree.fromstring(svg)

    def test_text_colour_has_the_better_contrast(self):
        assert badges._text_color("#555555") == "#ffffff"
        assert badges._text_color(badges.GREEN) == "#000000"


def metrics_file(tmp_path: Path, files: int = 3, lines: int = 1200) -> Path:
    path = tmp_path / "metrics.json"
    path.write_text(
        json.dumps(
            {"files": files, "lines": lines, "comment": 5, "blank": 6, "languages": {}}
        )
    )
    return path


class TestMain:
    def test_writes_three_badges_and_the_metrics(self, tmp_path, capsys):
        out = tmp_path / "out"
        cov = report(tmp_path, 'lines-covered="87" lines-valid="100"')
        code = badges.main(
            [
                "--metrics",
                str(metrics_file(tmp_path)),
                "--output-dir",
                str(out),
                "--coverage-report",
                str(cov),
            ]
        )
        assert code == 0
        assert sorted(p.name for p in out.iterdir()) == [
            "code-files.svg",
            "code-lines.svg",
            "code-metrics.json",
            "coverage.svg",
        ]
        assert (
            'aria-label="lines of code: 1,200"' in (out / "code-lines.svg").read_text()
        )
        assert 'aria-label="coverage: 87%"' in (out / "coverage.svg").read_text()
        assert f'fill="{badges.GREEN}"' in (out / "coverage.svg").read_text()
        assert b"\r" not in (out / "code-files.svg").read_bytes()
        assert "wrote" in capsys.readouterr().out

    def test_output_is_byte_identical_on_a_second_run(self, tmp_path):
        args = [
            "--metrics",
            str(metrics_file(tmp_path)),
            "--output-dir",
            str(tmp_path / "o"),
        ]
        badges.main(args)
        first = {p.name: p.read_bytes() for p in (tmp_path / "o").iterdir()}
        badges.main(args)
        assert first == {p.name: p.read_bytes() for p in (tmp_path / "o").iterdir()}

    def test_without_a_report_no_coverage_badge_and_a_notice(self, tmp_path, capsys):
        out = tmp_path / "out"
        assert (
            badges.main(
                ["--metrics", str(metrics_file(tmp_path)), "--output-dir", str(out)]
            )
            == 0
        )
        assert not (out / "coverage.svg").exists()
        assert "::notice::No coverage-report given" in capsys.readouterr().out

    def test_a_bad_report_fails_and_writes_nothing(self, tmp_path, capsys):
        out = tmp_path / "out"
        code = badges.main(
            [
                "--metrics",
                str(metrics_file(tmp_path)),
                "--output-dir",
                str(out),
                "--coverage-report",
                str(tmp_path / "missing.xml"),
            ]
        )
        assert code == 1
        assert "::error::[configuration] coverage-report" in capsys.readouterr().out
        assert not out.exists()

    @pytest.mark.parametrize(
        ("warn", "good", "message"),
        [
            ("x", "80", "coverage-warn 'x'"),
            ("60", "101", "coverage-good '101'"),
            ("-1", "80", "coverage-warn '-1'"),
            ("90", "80", "above coverage-good"),
        ],
    )
    def test_invalid_thresholds_fail(self, tmp_path, capsys, warn, good, message):
        code = badges.main(
            [
                "--metrics",
                str(metrics_file(tmp_path)),
                "--output-dir",
                str(tmp_path / "o"),
                "--coverage-warn",
                warn,
                "--coverage-good",
                good,
            ]
        )
        assert code == 1
        assert message in capsys.readouterr().out

    def test_unreadable_metrics_fail(self, tmp_path, capsys):
        bad = tmp_path / "m.json"
        bad.write_text('{"files": 1}')
        code = badges.main(["--metrics", str(bad), "--output-dir", str(tmp_path / "o")])
        assert code == 1
        assert "cannot be read" in capsys.readouterr().out
