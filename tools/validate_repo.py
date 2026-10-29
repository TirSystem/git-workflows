"""Steps of the scoped workflow .gitea/scoped_workflows/validate.yml (ADR-0016).

The workflow checks out the repository, fetches this file into shared-scripts/
and runs one command per step:

  validate_repo.py install   create a virtual environment with the pinned tools
  validate_repo.py run       check the workflow files and the shell scripts

The checks are the criteria of QC-WF-001 that a script can decide (WF-2, WF-3,
WF-5, WF-7, WF-8, WF-9, WF-10, WF-14 and WF-20), and shellcheck and shfmt on the
tracked shell scripts. Every finding is printed as
::error file=...,line=...::[WF-8] message (::warning for WF-5), and the run fails
when there is an error. A finding is silenced where it is:

  # validate-ignore: WF-8        on the line of the finding
  # validate-ignore-file: WF-5   anywhere in the file, for the whole file

Settings come from the environment:
  VALIDATE_VENV   virtual environment to install into (default .validate-venv)
  SHELLCHECK, SHFMT   the commands to run (default: from the virtual environment)
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

PYYAML_VERSION = "6.0.3"
SHELLCHECK_VERSION = "0.10.0.1"
SHFMT_VERSION = "3.11.0.2"
WORKFLOW_DIRECTORIES = (".gitea/workflows", ".gitea/scoped_workflows", ".github/workflows")
RUN_BLOCK_LIMIT = 5
TRUSTED_ORGANISATION = "TirSystem"
WARNING_CRITERIA = {"WF-5"}

_SHA = re.compile(r"^[0-9a-f]{40}$")
_EXACT_TAG = re.compile(r"^v?\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?$")
_MAJOR_TAG = re.compile(r"^v\d+$")
_UNTRUSTED = re.compile(r"\$\{\{\s*(inputs\.|(github|gitea)\.event\.|steps\.[\w-]+\.outputs\.)")
_SECRET_ON_LINE = re.compile(r"\$\{\{\s*secrets\.")
_RESERVED_SECRET = re.compile(r"secrets\.((?:GITEA|GITHUB)_\w+)")
_IGNORE_LINE = re.compile(r"#\s*validate-ignore:\s*(WF-\d+(?:\s*,\s*WF-\d+)*)")
_IGNORE_FILE = re.compile(r"#\s*validate-ignore-file:\s*(WF-\d+(?:\s*,\s*WF-\d+)*)")


class Finding(NamedTuple):
    path: str
    line: int
    criterion: str
    message: str


def fail(category: str, message: str) -> None:
    """Print a categorised error and exit with code 1."""
    print(f"::error::[{category}] {message}")
    sys.exit(1)


def venv_dir() -> str:
    return os.environ.get("VALIDATE_VENV", ".validate-venv")


def tool_command(name: str) -> str:
    return os.environ.get(name.upper()) or os.path.join(venv_dir(), "bin", name)


def install() -> None:
    """Create the virtual environment and install the pinned tools."""
    venv = venv_dir()
    for command in (
        [sys.executable, "-m", "venv", venv],
        [
            os.path.join(venv, "bin", "pip"),
            "install",
            "--quiet",
            f"PyYAML=={PYYAML_VERSION}",
            f"shellcheck-py=={SHELLCHECK_VERSION}",
            f"shfmt-py=={SHFMT_VERSION}",
        ],
    ):
        if subprocess.run(command, check=False).returncode != 0:
            fail("tool", f"'{' '.join(command[:3])}' failed; the validation tools are not installed.")


def tracked_files(root: Path) -> list[str]:
    """Return the git-tracked files of the repository, or every file when it is not one."""
    try:
        completed = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=False)
    except OSError:
        completed = None
    if completed is not None and completed.returncode == 0:
        return sorted(name for name in completed.stdout.decode("utf-8").split("\0") if name)
    return sorted(str(path.relative_to(root)).replace(os.sep, "/") for path in root.rglob("*") if path.is_file())


def workflow_files(files: list[str]) -> list[str]:
    return [
        name
        for name in files
        if name.endswith((".yml", ".yaml"))
        and any(name.startswith(directory + "/") and "/" not in name[len(directory) + 1 :] for directory in WORKFLOW_DIRECTORIES)
    ]


def shell_scripts(files: list[str]) -> list[str]:
    return [name for name in files if name.endswith(".sh")]


def pair(node, key: str):
    """Return the (key node, value node) of ``key`` in a YAML mapping node, or None."""
    for key_node, value_node in getattr(node, "value", []) if hasattr(node, "value") and isinstance(node.value, list) else []:
        if getattr(key_node, "value", None) == key:
            return key_node, value_node
    return None


def mapping_items(node):
    if node is not None and isinstance(getattr(node, "value", None), list):
        return [item for item in node.value if isinstance(item, tuple)]
    return []


def line_of(node) -> int:
    return node.start_mark.line + 1


def check_uses(path: str, value: str, line: int, found: list) -> None:
    """WF-8: an action is pinned to a full commit, an exact release tag, or a major tag of this organisation."""
    if value.startswith("./") or value.startswith("docker://"):
        return
    name, _, ref = value.partition("@")
    if not ref:
        found.append(Finding(path, line, "WF-8", f"'{value}' has no version after @."))
    elif _SHA.match(ref) or _EXACT_TAG.match(ref):
        return
    elif _MAJOR_TAG.match(ref):
        if name.split("/")[0] != TRUSTED_ORGANISATION:
            found.append(Finding(path, line, "WF-8", f"'{value}' uses a moving major tag of another organisation; pin an exact tag or a commit."))
    else:
        found.append(Finding(path, line, "WF-8", f"'{value}' is pinned to a branch or an unknown reference; pin an exact tag or a commit."))


def check_run(path: str, node, found: list) -> None:
    """WF-20, WF-10 and WF-9 on the text of a run: block."""
    text = node.value
    line = line_of(node)
    lines = text.rstrip("\n").split("\n")
    if len(lines) > RUN_BLOCK_LIMIT:
        found.append(Finding(path, line, "WF-20", f"run: holds {len(lines)} lines; the limit is {RUN_BLOCK_LIMIT}. Make it a script file."))
    if _UNTRUSTED.search(text):
        found.append(Finding(path, line, "WF-10", "run: interpolates untrusted text; pass it through env: and use a quoted variable."))
    if _SECRET_ON_LINE.search(text):
        found.append(Finding(path, line, "WF-9", "run: reads a secret in the command; pass it through env:."))


def check_steps(path: str, job_name: str, steps, found: list) -> None:
    seen: set[str] = set()
    entries = getattr(steps, "value", [])
    if not isinstance(entries, list):  # "steps: text" is a scalar; there is nothing to walk
        return
    for step in entries:
        line = line_of(step)
        name = pair(step, "name")
        if name is None:
            found.append(Finding(path, line, "WF-5", f"A step of job '{job_name}' has no name."))
        elif name[1].value in seen:
            found.append(Finding(path, line_of(name[1]), "WF-5", f"Step name '{name[1].value}' is used twice in job '{job_name}'."))
        else:
            seen.add(name[1].value)
        uses = pair(step, "uses")
        if uses is not None:
            check_uses(path, uses[1].value, line_of(uses[1]), found)
        run = pair(step, "run")
        if run is not None:
            check_run(path, run[1], found)


def check_workflow(path: str, text: str, yaml_module) -> list:
    """Return the findings of one workflow file."""
    found: list[Finding] = []
    try:
        root = yaml_module.compose(text)
    except yaml_module.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        return [Finding(path, (mark.line + 1) if mark else 1, "WF-1", f"Not valid YAML: {getattr(error, 'problem', error)}")]
    if root is None or not isinstance(root.value, list):
        return [Finding(path, 1, "WF-3", "The file is empty or is not a mapping.")]
    for key in ("name", "on", "jobs"):
        if pair(root, key) is None:
            found.append(Finding(path, 1, "WF-3", f"The file declares no '{key}'."))
    for text_value in _RESERVED_SECRET.findall(text):
        if text_value != "GITHUB_TOKEN":
            found.append(Finding(path, 1, "WF-9", f"secrets.{text_value} starts with GITEA_ or GITHUB_, which the host does not accept."))
    workflow_permissions = pair(root, "permissions")
    jobs = pair(root, "jobs")
    for key_node, job in mapping_items(jobs[1] if jobs else None):
        name = key_node.value
        line = line_of(key_node)
        calls_workflow = pair(job, "uses")
        if workflow_permissions is None and pair(job, "permissions") is None:
            found.append(Finding(path, line, "WF-7", f"Job '{name}' declares no permissions."))
        if calls_workflow is not None:
            check_uses(path, calls_workflow[1].value, line_of(calls_workflow[1]), found)
            continue
        if pair(job, "name") is None:
            found.append(Finding(path, line, "WF-5", f"Job '{name}' has no name."))
        if pair(job, "runs-on") is None:
            found.append(Finding(path, line, "WF-14", f"Job '{name}' has no runs-on."))
        if pair(job, "timeout-minutes") is None:
            found.append(Finding(path, line, "WF-14", f"Job '{name}' has no timeout-minutes."))
        steps = pair(job, "steps")
        if steps is not None:
            check_steps(path, name, steps[1], found)
    return found


def ignored(finding: Finding, lines: list[str], file_ignores: set[str]) -> bool:
    if finding.criterion in file_ignores:
        return True
    if 0 < finding.line <= len(lines):
        match = _IGNORE_LINE.search(lines[finding.line - 1])
        return bool(match) and finding.criterion in {item.strip() for item in match.group(1).split(",")}
    return False


def check_duplicates(files: list[str]) -> list:
    """WF-2: the same workflow must not exist in both .gitea/workflows and .github/workflows."""
    gitea = {Path(name).name for name in files if name.startswith(".gitea/workflows/")}
    return [
        Finding(name, 1, "WF-2", f"'{Path(name).name}' exists in both .gitea/workflows and .github/workflows.")
        for name in files
        if name.startswith(".github/workflows/") and Path(name).name in gitea
    ]


def check_shell(scripts: list[str]) -> bool:
    """Run shellcheck and shfmt on the scripts; return True when both are clean."""
    clean = True
    for tool, arguments in (("shellcheck", []), ("shfmt", ["-d"])):
        try:
            completed = subprocess.run([tool_command(tool), *arguments, *scripts], check=False)
        except OSError as error:
            fail("tool", f"{tool} cannot be started: {error}")
        if completed.returncode != 0:
            print(f"::error::[shell] {tool} found problems in the shell scripts above.")
            clean = False
    return clean


def report(finding: Finding) -> bool:
    """Print a finding as an annotation and return True when it is an error."""
    level = "warning" if finding.criterion in WARNING_CRITERIA else "error"
    print(f"::{level} file={finding.path},line={finding.line}::[{finding.criterion}] {finding.message}")
    return level == "error"


def run() -> None:
    """Check the repository in the current directory."""
    try:
        import yaml
    except ImportError:
        fail("tool", "PyYAML is not installed; run the install step first.")
    root = Path.cwd()
    files = tracked_files(root)
    workflows = workflow_files(files)
    scripts = shell_scripts(files)
    if not workflows and not scripts:
        print("No workflow file and no shell script in this repository; nothing to validate.")
        return
    findings = check_duplicates(workflows)
    workflows = [path for path in workflows if (root / path).is_file()]
    scripts = [path for path in scripts if (root / path).is_file()]
    for path in workflows:
        text = (root / path).read_text(encoding="utf-8")
        lines = text.split("\n")
        file_ignores = {item.strip() for match in _IGNORE_FILE.findall(text) for item in match.split(",")}
        findings += [item for item in check_workflow(path, text, yaml) if not ignored(item, lines, file_ignores)]
    errors = sum(report(finding) for finding in sorted(findings))
    shell_clean = check_shell(scripts) if scripts else True
    print(f"Checked {len(workflows)} workflow file(s) and {len(scripts)} shell script(s): {len(findings)} finding(s), {errors} error(s).")
    if errors or not shell_clean:
        fail("finding", "The validation found errors; fix them or silence them with '# validate-ignore: <criterion>'.")


def main(argv: list[str]) -> None:
    commands = {"install": install, "run": run}
    if len(argv) != 2 or argv[1] not in commands:
        fail("configuration", "usage: validate_repo.py install|run")
    commands[argv[1]]()


if __name__ == "__main__":
    main(sys.argv)
