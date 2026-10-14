"""Read a Cobertura coverage report and write the code metrics badges (ADR-0010).

Usage:
    python tools/badges.py --metrics code-metrics.json --output-dir DIR
        [--coverage-report coverage.xml] [--coverage-warn 60] [--coverage-good 80]

Writes `code-files.svg`, `code-lines.svg`, `code-metrics.json` and, when a report
is given, `coverage.svg` into DIR. The same input gives the same bytes.

Exit codes: 0 written, 1 a configuration problem (printed as
`::error::[configuration] ...`, nothing is written).
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ElementTree
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

BLUE = "#007ec6"
RED = "#e05d44"
YELLOW = "#dfb317"
GREEN = "#44cc11"
LABEL_COLOR = "#555555"
CHAR_WIDTH = 6
PADDING = 10
HEIGHT = 20


class ConfigurationError(Exception):
    """An input is invalid; the message is printed as a `[configuration]` failure."""


def read_coverage(path: Path) -> int:
    """Return the line coverage of a Cobertura XML report as a whole percent, half up."""
    if not path.is_file():
        raise ConfigurationError(f"coverage-report '{path}' does not exist.")
    data = path.read_bytes()
    if b"<!ENTITY" in data:
        raise ConfigurationError(
            f"coverage-report '{path}' declares entities, which are refused."
        )
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as error:
        raise ConfigurationError(
            f"coverage-report '{path}' is not well-formed XML: {error}."
        ) from error
    if root.tag != "coverage":
        raise ConfigurationError(
            f"coverage-report '{path}' is not a Cobertura report (root element '{root.tag}')."
        )
    covered, valid = root.get("lines-covered"), root.get("lines-valid")
    try:
        if covered is not None and valid is not None:
            covered_lines, valid_lines = int(covered), int(valid)
            if valid_lines <= 0:
                raise ConfigurationError(
                    f"coverage-report '{path}' has no valid lines."
                )
            if not 0 <= covered_lines <= valid_lines:
                raise ConfigurationError(
                    f"coverage-report '{path}' has lines-covered outside 0..lines-valid."
                )
            fraction = Decimal(covered_lines) / Decimal(valid_lines)
        else:
            rate = root.get("line-rate")
            if rate is None:
                raise ConfigurationError(
                    f"coverage-report '{path}' has neither lines-valid and lines-covered nor line-rate."
                )
            fraction = Decimal(rate)
            if not Decimal(0) <= fraction <= Decimal(1):
                raise ConfigurationError(
                    f"coverage-report '{path}' has a line-rate outside 0..1."
                )
    except (ValueError, InvalidOperation) as error:
        raise ConfigurationError(
            f"coverage-report '{path}' has a value that is not a number."
        ) from error
    return int((fraction * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def coverage_color(percent: int, warn: float, good: float) -> str:
    """Return red below warn, yellow from warn to below good, green from good."""
    if percent < warn:
        return RED
    if percent < good:
        return YELLOW
    return GREEN


def _luminance(color: str) -> float:
    channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _text_color(background: str) -> str:
    """Black or white, whichever has the higher contrast on the background."""
    lum = _luminance(background)
    return "#ffffff" if (1.05 / (lum + 0.05)) >= ((lum + 0.05) / 0.05) else "#000000"


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render(label: str, value: str, color: str) -> str:
    """Return a flat two-part SVG badge; the width follows the number of characters."""
    label_width = CHAR_WIDTH * len(label) + PADDING
    value_width = CHAR_WIDTH * len(value) + PADDING
    total = label_width + value_width
    text = _escape(f"{label}: {value}")
    label_x = label_width / 2
    value_x = label_width + value_width / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="{HEIGHT}" '
        f'role="img" aria-label="{text}">\n'
        f"<title>{text}</title>\n"
        f'<rect width="{label_width}" height="{HEIGHT}" fill="{LABEL_COLOR}"/>\n'
        f'<rect x="{label_width}" width="{value_width}" height="{HEIGHT}" fill="{color}"/>\n'
        '<g font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11" '
        'text-anchor="middle">\n'
        f'<text x="{label_x:g}" y="14" fill="{_text_color(LABEL_COLOR)}">{_escape(label)}</text>\n'
        f'<text x="{value_x:g}" y="14" fill="{_text_color(color)}">{_escape(value)}</text>\n'
        "</g>\n"
        "</svg>\n"
    )


def _threshold(name: str, text: str) -> float:
    try:
        value = float(text)
    except ValueError as error:
        raise ConfigurationError(
            f"{name} '{text}' is not a number from 0 to 100."
        ) from error
    if not 0 <= value <= 100:
        raise ConfigurationError(f"{name} '{text}' is not a number from 0 to 100.")
    return value


def write_badges(
    file_count: int,
    line_count: int,
    metrics_json: str,
    output_dir: Path,
    coverage: int | None,
    warn: float,
    good: float,
) -> list[Path]:
    """Write the badge files and the metrics JSON; return the paths in a fixed order."""
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "code-files.svg": render("code files", f"{file_count:,}", BLUE),
        "code-lines.svg": render("lines of code", f"{line_count:,}", BLUE),
    }
    if coverage is not None:
        files["coverage.svg"] = render(
            "coverage", f"{coverage}%", coverage_color(coverage, warn, good)
        )
    files["code-metrics.json"] = metrics_json
    paths = []
    for name, content in files.items():
        path = output_dir / name
        path.write_text(content, encoding="utf-8", newline="\n")
        paths.append(path)
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--metrics", required=True, help="JSON written by count_loc.py")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--coverage-report", default="")
    parser.add_argument("--coverage-warn", default="60")
    parser.add_argument("--coverage-good", default="80")
    args = parser.parse_args(argv)
    try:
        warn = _threshold("coverage-warn", args.coverage_warn)
        good = _threshold("coverage-good", args.coverage_good)
        if warn > good:
            raise ConfigurationError(
                f"coverage-warn {args.coverage_warn} is above coverage-good {args.coverage_good}."
            )
        coverage = (
            read_coverage(Path(args.coverage_report)) if args.coverage_report else None
        )
        metrics = json.loads(Path(args.metrics).read_text(encoding="utf-8"))
        file_count, line_count = int(metrics["files"]), int(metrics["lines"])
    except ConfigurationError as error:
        print(f"::error::[configuration] {error}")
        return 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(
            f"::error::[configuration] metrics file '{args.metrics}' cannot be read: {error}"
        )
        return 1
    if file_count == 0:
        print("::notice::No code files were found; the badges show 0.")
    if coverage is None:
        print("::notice::No coverage-report given; no coverage badge is written.")
    metrics_json = json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    written = write_badges(
        file_count,
        line_count,
        metrics_json,
        Path(args.output_dir),
        coverage,
        warn,
        good,
    )
    for path in written:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
