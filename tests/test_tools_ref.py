"""The default `tools-ref` of every reusable workflow names the current major.

A reusable workflow fetches the script it runs from this repository at its
input `tools-ref`. A default that names a tag without the script makes a call
with the defaults fail (MIL-011; code-metrics.yml defaulted to `v1`, where
`tools/code-metrics.sh` does not exist). The current major is defined once, in
`MAJOR_TAG`, and these tests check the workflows against it.
"""

import re
import subprocess

import pytest
import yaml

from workflow_source import REPO_ROOT, WORKFLOW_DIRS

MAJOR_TAG_FILE = REPO_ROOT / "MAJOR_TAG"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
SCRIPT_PATTERN = re.compile(r"shared-scripts/(tools/[A-Za-z0-9_.-]+)")
VERSION_HEADING = re.compile(r"^## \[(\d+)\.(\d+)\.(\d+)\]", re.MULTILINE)


def reusable_workflows():
    """Return the workflow files of this repository that a caller can use."""
    path = WORKFLOW_DIRS[1]
    found = []
    for candidate in sorted(path.glob("*.yml")):
        document = yaml.safe_load(candidate.read_text(encoding="utf-8"))
        triggers = document.get("on") or document.get(True) or {}
        if isinstance(triggers, dict) and "workflow_call" in triggers:
            found.append(candidate)
    return found


def tools_ref_problems(text, major, script_exists):
    """Return the problems of one workflow's default `tools-ref`, or [].

    `text` is the workflow file, `major` the current major tag, and
    `script_exists(tag, path)` says whether the tag holds the script.
    """
    document = yaml.safe_load(text)
    triggers = document.get("on") or document.get(True) or {}
    inputs = (triggers.get("workflow_call") or {}).get("inputs") or {}
    if "tools-ref" not in inputs:
        return []
    problems = []
    default = inputs["tools-ref"].get("default")
    if default != major:
        problems.append(f"default tools-ref is {default!r}, the current major is {major!r}")
    for script in sorted(set(SCRIPT_PATTERN.findall(text))):
        if not script_exists(default, script):
            problems.append(f"{script} is not in tag {default!r}")
    return problems


def current_major():
    return MAJOR_TAG_FILE.read_text(encoding="utf-8").strip()


def released_in_any_tag(path):
    """True when some version tag holds the file; False for a script not released yet."""
    tags = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "tag", "--list", "v*"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.split()
    return any(
        subprocess.run(
            ["git", "-C", str(REPO_ROOT), "cat-file", "-e", f"{tag}:{path}"],
            capture_output=True,
            check=False,
        ).returncode
        == 0
        for tag in tags
    )


def script_in_tag(tag, path):
    """True when the tag holds the file; True when the tag is not in this checkout.

    A script that no tag holds yet is new in the unreleased version: the release
    moves the major tag to it, so it does not count as missing (MIL-013).
    """
    known = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}"],
        capture_output=True,
        check=False,
    )
    if known.returncode != 0:
        return True
    holds = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "cat-file", "-e", f"{tag}:{path}"],
        capture_output=True,
        check=False,
    )
    return holds.returncode == 0 or not released_in_any_tag(path)


def test_major_tag_file_names_the_highest_major_of_the_changelog():
    majors = [int(m.group(1)) for m in VERSION_HEADING.finditer(CHANGELOG.read_text(encoding="utf-8"))]
    assert majors, "the changelog has no released version"
    assert current_major() == f"v{max(majors)}"


@pytest.mark.parametrize("path", reusable_workflows(), ids=lambda p: p.name)
def test_default_tools_ref_is_the_current_major_and_holds_the_script(path):
    problems = tools_ref_problems(path.read_text(encoding="utf-8"), current_major(), script_in_tag)
    assert problems == []


@pytest.mark.parametrize("path", reusable_workflows(), ids=lambda p: p.name)
def test_every_script_a_workflow_runs_is_in_the_working_tree(path):
    for script in SCRIPT_PATTERN.findall(path.read_text(encoding="utf-8")):
        assert (REPO_ROOT / script).is_file(), f"{path.name} runs {script}, which does not exist"


def test_a_default_that_names_an_old_major_is_reported():
    text = (WORKFLOW_DIRS[1] / "code-metrics.yml").read_text(encoding="utf-8")
    seeded = re.sub(r'(tools-ref:\s*description:[^\n]*\n\s*type: string\n\s*default: )"[^"]*"', r'\1"v1"', text)
    assert seeded != text, "the seeded default was not applied"
    problems = tools_ref_problems(seeded, "v2", lambda tag, path: tag != "v1")
    assert any("current major" in p for p in problems)
    assert any("is not in tag 'v1'" in p for p in problems)


def test_the_fixed_default_has_no_problem():
    text = (WORKFLOW_DIRS[1] / "code-metrics.yml").read_text(encoding="utf-8")
    assert tools_ref_problems(text, current_major(), lambda tag, path: True) == []
