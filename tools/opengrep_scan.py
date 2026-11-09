"""Steps of the scoped workflow .gitea/scoped_workflows/opengrep.yml (ADR-0015).

The workflow checks out the repository, fetches this file into shared-scripts/
and runs one command per step:

  opengrep_scan.py install   download the pinned OpenGrep binary, verify its
                             sha256 and fetch the pinned rules
  opengrep_scan.py run       scan the repository, print the findings, fail on ERROR

Settings are fixed by the ADR; only the paths come from the environment:
  OPENGREP_HOME   where the binary and the rules go (default .opengrep)
  OPENGREP_BIN    the opengrep command, for tests (default <home>/opengrep)
  OPENGREP_REPORT where the JSON report is written (default opengrep-report.json)

Every failure is printed as ::error::[category] message.
"""

import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

OPENGREP_VERSION = "v1.33.0"
OPENGREP_SHA256 = "2545812755572e1355ea60f96288f82a26eebed7fc8b512430d49d5667214c24"
OPENGREP_URL = (
    f"https://github.com/opengrep/opengrep/releases/download/{OPENGREP_VERSION}/opengrep_manylinux_x86"
)
RULES_REPOSITORY = "https://github.com/opengrep/opengrep-rules"
RULES_COMMIT = "f1d2b562b414783763fd02a6ed2736eaed622efa"
# The rules checkout holds non-rule YAML, so each rule directory is a --config.
RULE_DIRECTORIES = (
    "python",
    "bash",
    "c",
    "csharp",
    "yaml",
    "generic",
    "dockerfile",
    "javascript",
    "typescript",
    "terraform",
    "go",
    "java",
)
# The rule directory that is always scanned: its rules do not depend on a language.
ALWAYS_SCANNED_DIRECTORY = "generic"
# OpenGrep language name -> file name endings (lower case) of the files in that language.
# A language that is not here makes its rule directory run (fail safe).
LANGUAGE_EXTENSIONS = {
    "python": (".py", ".pyi"),
    "py": (".py", ".pyi"),
    "bash": (".sh", ".bash"),
    "sh": (".sh", ".bash"),
    "c": (".c", ".h"),
    "cpp": (".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx", ".h"),
    "csharp": (".cs",),
    "yaml": (".yaml", ".yml"),
    "json": (".json",),
    "dockerfile": ("dockerfile",),
    "docker": ("dockerfile",),
    "javascript": (".js", ".jsx", ".mjs", ".cjs"),
    "js": (".js", ".jsx", ".mjs", ".cjs"),
    "typescript": (".ts", ".tsx", ".mts", ".cts"),
    "ts": (".ts", ".tsx", ".mts", ".cts"),
    "terraform": (".tf", ".hcl"),
    "hcl": (".tf", ".hcl"),
    "go": (".go",),
    "golang": (".go",),
    "java": (".java",),
}
INLINE_LANGUAGES = re.compile(r"^\s*languages:\s*\[([^\]]*)\]", re.MULTILINE)
BLOCK_LANGUAGES = re.compile(r"^\s*languages:[ \t]*\n((?:[ \t]*-[ \t]*\S+[^\n]*\n?)+)", re.MULTILINE)
BLOCK_ITEM = re.compile(r"^[ \t]*-[ \t]*([^\s#]+)", re.MULTILINE)
TOP_LEVEL_RULES = re.compile(r"^rules:", re.MULTILINE)
BLOCKING_SEVERITY = "ERROR"
SUMMARY_LIMIT = 50
DOWNLOAD_TIMEOUT_SECONDS = 120


@dataclass(frozen=True, slots=True)
class RuleFile:
    """A rule file and the languages it declares (empty when none could be read)."""

    path: Path
    languages: frozenset[str]


def fail(category: str, message: str) -> None:
    """Print a categorised error and exit with code 1."""
    print(f"::error::[{category}] {message}")
    sys.exit(1)


def home_dir() -> str:
    return os.environ.get("OPENGREP_HOME", ".opengrep")


def binary_path() -> str:
    return os.path.join(home_dir(), "opengrep")


def rules_dir() -> str:
    return os.path.join(home_dir(), "rules")


def selected_rules_dir() -> str:
    return os.path.join(home_dir(), "selected-rules")


def opengrep_command() -> str:
    return os.environ.get("OPENGREP_BIN") or binary_path()


def report_path() -> str:
    return os.environ.get("OPENGREP_REPORT", "opengrep-report.json")


def check_platform() -> None:
    """Only Linux x86_64 has a recorded checksum; anything else is a configuration error."""
    system, machine = platform.system(), platform.machine()
    if system != "Linux" or machine not in ("x86_64", "AMD64"):
        fail("configuration", f"OpenGrep {OPENGREP_VERSION} is supported on Linux x86_64 only, not {system} {machine}.")


def download(url: str, target: str) -> None:
    """Fetch ``url`` into the file ``target``; a network failure is a tool error."""
    try:
        with urllib.request.urlopen(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:  # noqa: S310 - fixed https URL
            data = response.read()
        with open(target, "wb") as handle:
            handle.write(data)
    except OSError as error:
        fail("tool", f"{url} cannot be downloaded: {error}")


def sha256_of(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def install_binary() -> None:
    """Download the pinned binary, verify its checksum and make it executable."""
    os.makedirs(home_dir(), exist_ok=True)
    target = binary_path()
    download(OPENGREP_URL, target)
    actual = sha256_of(target)
    if actual != OPENGREP_SHA256:
        os.remove(target)
        fail("tool", f"The OpenGrep download has sha256 {actual}, expected {OPENGREP_SHA256}; the binary is removed.")
    os.chmod(target, os.stat(target).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def fetch_rules() -> None:
    """Fetch only the pinned commit of the rules repository, without its history."""
    target = rules_dir()
    os.makedirs(target, exist_ok=True)
    for command in (
        ["git", "init", "--quiet", target],
        ["git", "-C", target, "fetch", "--quiet", "--depth", "1", RULES_REPOSITORY, RULES_COMMIT],
        ["git", "-C", target, "checkout", "--quiet", "FETCH_HEAD"],
    ):
        # The command is a list of constants and values of this script; no shell runs it.
        if subprocess.run(command, check=False).returncode != 0:  # nosemgrep
            fail("tool", f"'{' '.join(command[:4])}' failed; the OpenGrep rules {RULES_COMMIT} are not fetched.")


def install() -> None:
    """Install the pinned OpenGrep binary and the pinned rules."""
    check_platform()
    install_binary()
    fetch_rules()


def tracked_files(root: Path) -> list[str] | None:
    """Return the files git tracks under ``root``, or None when git cannot list them."""
    command = ["git", "-C", str(root), "ls-files", "-z"]
    try:
        # The command is a list of constants and values of this script; no shell runs it.
        completed = subprocess.run(command, check=False, capture_output=True, text=True)  # nosemgrep
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    return [name for name in completed.stdout.split("\0") if name]


def walked_files(root: Path) -> list[str]:
    """Return every file under ``root`` except the contents of .git directories."""
    names = []
    for current, directories, files in os.walk(root):
        directories[:] = [name for name in directories if name != ".git"]
        names += [str(Path(current, name).relative_to(root)) for name in files]
    return names


def repository_files(root: Path) -> list[str]:
    """Return the files of the repository: the tracked ones, else a walk of the tree."""
    tracked = tracked_files(root)
    return tracked if tracked is not None else walked_files(root)


def languages_in(text: str) -> set[str]:
    """Return the ``languages:`` values of one rule file, lower case."""
    names: list[str] = []
    for match in INLINE_LANGUAGES.finditer(text):
        names += [item.strip().strip("'\"") for item in match.group(1).split(",")]
    for match in BLOCK_LANGUAGES.finditer(text):
        names += [item.strip("'\"") for item in BLOCK_ITEM.findall(match.group(1))]
    return {name.lower() for name in names if name}


def read_rule_file(path: Path) -> RuleFile | None:
    """Return the rule file at ``path``, or None when it is not one (no top-level ``rules:``).

    A file that cannot be read is returned with no languages, so it is kept (fail safe).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return RuleFile(path, frozenset())
    if not TOP_LEVEL_RULES.search(text):
        return None
    return RuleFile(path, frozenset(languages_in(text)))


def rule_files_in(directory: Path) -> list[RuleFile]:
    """Return the rule files under ``directory``; other YAML (fixtures, metadata) is left out."""
    paths = sorted([*directory.rglob("*.yaml"), *directory.rglob("*.yml")])
    return [rule for rule in map(read_rule_file, paths) if rule is not None]


def has_file_of(file_names: list[str], languages: frozenset[str]) -> bool:
    endings = tuple(ending for language in languages for ending in LANGUAGE_EXTENSIONS[language])
    return any(name.endswith(endings) for name in file_names)


def is_needed(file_names: list[str], rule: RuleFile) -> bool:
    """A rule is needed unless all its languages are known and the repository has no file of them."""
    if not rule.languages or not rule.languages <= LANGUAGE_EXTENSIONS.keys():
        return True
    return has_file_of(file_names, rule.languages)


def copy_rules(rules: list[RuleFile], source: Path, target: Path) -> None:
    """Copy the rule files into ``target``, keeping their paths relative to ``source``."""
    for rule in rules:
        destination = target / rule.path.relative_to(source)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rule.path, destination)
        except OSError as error:
            fail("tool", f"The rule file {rule.path} cannot be copied: {error}")


def select_rules(files: list[str], rules_root: Path, work_dir: Path) -> tuple[list[Path], list[str]]:
    """Return the --config directories and one line per rule directory saying what was kept.

    ``work_dir`` receives a filtered copy of each directory that has rule files to skip.
    The generic directory, and a directory without readable rule files, are used whole.
    """
    file_names = [name.lower() for name in files]
    shutil.rmtree(work_dir, ignore_errors=True)
    configs: list[Path] = []
    lines: list[str] = []
    for directory in RULE_DIRECTORIES:
        source = rules_root / directory
        rules = [] if directory == ALWAYS_SCANNED_DIRECTORY else rule_files_in(source)
        if not rules:
            configs.append(source)
            lines.append(f"Rule directory {directory}: used whole")
            continue
        kept = [rule for rule in rules if is_needed(file_names, rule)]
        lines.append(f"Rule directory {directory}: {len(kept)} rule files kept, {len(rules) - len(kept)} skipped")
        if kept:
            copy_rules(kept, source, work_dir / directory)
            configs.append(work_dir / directory)
    return configs, lines


def home_exclude() -> list[str]:
    """Return the --exclude option that keeps the scan out of the home directory when it is in the repository.

    The filtered rule files are YAML files copied there; scanned as source, they give findings of their own.
    """
    try:
        inside = Path(home_dir()).resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        return []
    return ["--exclude", inside.as_posix()] if inside.parts else []


def scan_command(configs: list[Path]) -> list[str]:
    command = [opengrep_command(), "scan"]
    for config in configs:
        command += ["--config", str(config)]
    command += home_exclude()
    command += ["--json", "--output", report_path(), "--quiet", "--disable-version-check"]
    return command


def load_report(path: str) -> dict:
    """Return the decoded report, or fail as a tool error when it is unreadable."""
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        fail("tool", f"The OpenGrep report {path} cannot be read: {error}")
    return {}


def annotation(severity: str) -> str:
    return {"ERROR": "error", "WARNING": "warning"}.get(severity, "notice")


def print_finding(finding: dict) -> None:
    extra = finding.get("extra", {})
    severity = extra.get("severity", "INFO")
    line = finding.get("start", {}).get("line", 1)
    message = " ".join(extra.get("message", "").split())
    print(f"::{annotation(severity)} file={finding['path']},line={line}::[finding] {finding['check_id']}: {message}")


def write_summary(findings: list, blocking: list, selection: list[str]) -> None:
    """Append a short table to the job summary when the runner provides one."""
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if not target:
        return
    lines = [
        "## OpenGrep",
        "",
        f"{len(findings)} findings, {len(blocking)} of severity {BLOCKING_SEVERITY} (they fail the run).",
        "",
        "| Severity | Rule | File |",
        "| --- | --- | --- |",
    ]
    for finding in findings[:SUMMARY_LIMIT]:
        extra = finding.get("extra", {})
        location = f"{finding['path']}:{finding.get('start', {}).get('line', 1)}"
        lines.append(f"| {extra.get('severity', 'INFO')} | `{finding['check_id']}` | {location} |")
    if len(findings) > SUMMARY_LIMIT:
        lines.append(f"| | {len(findings) - SUMMARY_LIMIT} more in the log | |")
    lines += ["", *(f"- {line}" for line in selection)]
    with open(target, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def run() -> None:
    """Scan, print every finding and fail when one has the blocking severity."""
    configs, selection = select_rules(repository_files(Path.cwd()), Path(rules_dir()), Path(selected_rules_dir()))
    print("\n".join(selection))
    command = scan_command(configs)
    try:
        # The command is a list of constants and values of this script; no shell runs it.
        completed = subprocess.run(command, check=False)  # nosemgrep
    except OSError as error:
        fail("tool", f"OpenGrep cannot be started: {error}")
    if completed.returncode != 0:
        fail("tool", f"OpenGrep exited with code {completed.returncode}.")
    report = load_report(report_path())
    scanned = report.get("paths", {}).get("scanned", [])
    if not scanned:
        print("No file that OpenGrep scans in this repository; nothing to scan.")
        return
    findings = report.get("results", [])
    for finding in findings:
        print_finding(finding)
    blocking = [item for item in findings if item.get("extra", {}).get("severity") == BLOCKING_SEVERITY]
    write_summary(findings, blocking, selection)
    print(f"OpenGrep {report.get('version', OPENGREP_VERSION)} scanned {len(scanned)} files: {len(findings)} findings, {len(blocking)} blocking.")
    if blocking:
        fail("finding", f"{len(blocking)} finding(s) of severity {BLOCKING_SEVERITY}; fix them or silence them with '# nosemgrep' or a .semgrepignore file.")


def main(argv: list) -> None:
    commands = {"install": install, "run": run}
    if len(argv) != 2 or argv[1] not in commands:
        fail("configuration", "usage: opengrep_scan.py install|run")
    commands[argv[1]]()


if __name__ == "__main__":
    main(sys.argv)
