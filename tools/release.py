"""Create a release of this repository: version tag, release page, major tag.

Run by .gitea/workflows/release.yml (MIL-004 task 5, ADR-0006, ADR-0007). It
publishes a release only when all of these hold, and stops before any write
when one does not:

    - the version is MAJOR.MINOR.PATCH and CHANGELOG.md has an entry for it;
    - the commit is the tip of the default branch;
    - the validation run of that commit is green;
    - the tag vMAJOR.MINOR.PATCH does not exist yet.

It then creates the release page (which creates the tag) from the changelog
entry and moves the major tag vMAJOR to the commit when the version is the
highest of its major version. It reads its settings from the environment:

    GITEA_API_URL        Gitea API base, for example https://host/api/v1
    SOURCE_REPOSITORY    owner/repo that is released
    RELEASE_CREDENTIALS  the token of the run, as clear text
    RELEASE_VERSION      the version, for example 1.0.0 (no leading v)
    RELEASE_SHA          the commit to release
    RELEASE_DRY_RUN      "true" (default) checks and prints, writes nothing
    RELEASE_BRANCH       the default branch (default: main)
    VALIDATION_CONTEXT   the status context that must be green
                         (default: Validate workflows / validate (push))
    CHANGELOG_FILE       default: CHANGELOG.md

Every failure is printed as ``ERROR: [category] message`` with the categories
configuration, validation, credentials, permissions and api; no secret value
is printed.
"""

import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_CONTEXT = "Validate workflows / validate (push)"
_VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_TAG = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class WorkflowError(RuntimeError):
    """A failure with a category.

    configuration: a setting or the changelog is missing or malformed.
    validation:    the release is not allowed (commit, run, tag or changelog).
    credentials:   Gitea rejected the token (HTTP 401).
    permissions:   the token is valid but not allowed (HTTP 403).
    api:           any other API or network failure.
    """

    def __init__(self, category, message):
        super().__init__(f"[{category}] {message}")
        self.category = category
        self.detail = message


def load_changelog_module():
    """Import tools/changelog.py, which sits next to this file."""
    path = Path(__file__).resolve().parent / "changelog.py"
    spec = importlib.util.spec_from_file_location("changelog", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def request_json(url, method="GET", headers=None, body=None):
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers=headers or {},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            content = response.read()
            return json.loads(content) if content else None
    except urllib.error.HTTPError as error:
        target = url.split("?")[0]
        detail = f"Gitea API request failed with HTTP {error.code} ({error.reason}) for {method} {target}"
        if error.code == 401:
            raise WorkflowError("credentials", f"{detail}. The token was rejected.") from None
        if error.code == 403:
            raise WorkflowError(
                "permissions",
                f"{detail}. The token lacks write access to the contents of the repository.",
            ) from None
        raise WorkflowError("api", detail) from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise WorkflowError("api", f"Gitea API is unreachable ({error}).") from None


def parse_version(raw):
    """Return the version as a tuple, or raise a configuration error."""
    text = (raw or "").strip()
    match = _VERSION.match(text)
    if not match:
        raise WorkflowError(
            "configuration",
            f"'{text}' is not a version MAJOR.MINOR.PATCH (write 1.0.0, without a leading v).",
        )
    return tuple(int(part) for part in match.groups())


def split_repository(full_name):
    owner, separator, repo = (full_name or "").partition("/")
    if not separator or not owner or not repo:
        raise WorkflowError("configuration", "Could not determine the Gitea repository.")
    return owner, repo


def release_notes(changelog_text, version, changelog):
    """Return the release page text for a version, or fail as a validation error."""
    problems = changelog.validate(changelog_text)
    if problems:
        raise WorkflowError("validation", "CHANGELOG.md breaks its convention: " + "; ".join(problems))
    try:
        return changelog.notes(changelog_text, version)
    except LookupError as error:
        raise WorkflowError("validation", str(error)) from None


def list_tag_names(api, headers, request):
    """Return every tag name of the repository."""
    names = []
    page = 1
    while True:
        batch = request(f"{api}/tags?limit=50&page={page}", headers=headers)
        if not batch:
            return names
        names += [item["name"] for item in batch]
        if len(batch) < 50:
            return names
        page += 1


def check_commit(api, headers, request, sha, branch, context):
    """The commit is the tip of the branch and its validation run is green."""
    tip = request(f"{api}/branches/{urllib.parse.quote(branch, safe='')}", headers=headers)
    tip_sha = (tip or {}).get("commit", {}).get("id", "")
    if tip_sha != sha:
        raise WorkflowError(
            "validation",
            f"{sha[:7]} is not the tip of {branch} ({tip_sha[:7] or 'unknown'}); "
            "release from the latest commit of the default branch.",
        )
    status = request(f"{api}/commits/{sha}/status", headers=headers) or {}
    for item in status.get("statuses", []):
        if item.get("context") == context:
            if item.get("status") != "success":
                raise WorkflowError(
                    "validation",
                    f"The validation run '{context}' of {sha[:7]} is {item.get('status')}, not success.",
                )
            return
    raise WorkflowError(
        "validation",
        f"No validation run '{context}' was found for {sha[:7]}; wait for it or run it first.",
    )


def plan_tags(tags, version):
    """Return (exact tag, major tag, whether the major tag moves)."""
    exact = "v{}.{}.{}".format(*version)
    major = f"v{version[0]}"
    if exact in tags:
        raise WorkflowError("validation", f"The tag {exact} already exists; tags are never moved.")
    same_major = [
        tuple(int(p) for p in m.groups())
        for m in (_TAG.match(name) for name in tags)
        if m and int(m.group(1)) == version[0]
    ]
    moves = all(version > other for other in same_major)
    return exact, major, moves


def publish(api, headers, request, sha, exact, major, moves, notes, major_exists):
    """Create the release page (and with it the tag), then move the major tag."""
    request(
        f"{api}/releases",
        method="POST",
        headers=headers,
        body={
            "tag_name": exact,
            "target_commitish": sha,
            "name": exact,
            "body": notes,
            "draft": False,
            "prerelease": False,
        },
    )
    if not moves:
        return
    if major_exists:
        request(f"{api}/tags/{major}", method="DELETE", headers=headers)
    request(
        f"{api}/tags",
        method="POST",
        headers=headers,
        body={"tag_name": major, "target": sha, "message": f"{major} points to {exact}"},
    )


def main(request=request_json):
    version = parse_version(os.environ.get("RELEASE_VERSION"))
    owner, repo = split_repository(os.environ.get("SOURCE_REPOSITORY"))
    sha = (os.environ.get("RELEASE_SHA") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise WorkflowError("configuration", "RELEASE_SHA must be the 40-character commit to release.")
    token = (os.environ.get("RELEASE_CREDENTIALS") or "").strip()
    if not token:
        raise WorkflowError(
            "configuration",
            "No token for the release: the run has none and TOKEN_FOR_GITEA_RELEASE is not set.",
        )
    dry_run = (os.environ.get("RELEASE_DRY_RUN") or "true").strip().lower() != "false"
    branch = os.environ.get("RELEASE_BRANCH") or "main"
    context = os.environ.get("VALIDATION_CONTEXT") or DEFAULT_CONTEXT
    changelog_path = Path(os.environ.get("CHANGELOG_FILE") or "CHANGELOG.md")

    changelog = load_changelog_module()
    name = "{}.{}.{}".format(*version)
    try:
        text = changelog_path.read_text(encoding="utf-8")
    except OSError as error:
        raise WorkflowError("configuration", f"Cannot read {changelog_path}: {error}") from None
    notes = release_notes(text, name, changelog)

    api_url = os.environ["GITEA_API_URL"].rstrip("/")
    api = f"{api_url}/repos/{urllib.parse.quote(owner, safe='')}/{urllib.parse.quote(repo, safe='')}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    check_commit(api, headers, request, sha, branch, context)
    tags = list_tag_names(api, headers, request)
    exact, major, moves = plan_tags(tags, version)
    print(f"Checks passed for {exact} on {sha[:7]}: changelog entry, tip of {branch}, green run, new tag.")

    if dry_run:
        print(
            f"Dry run: would create the release page {exact}"
            + (f" and point {major} to it." if moves else f" and leave {major} where it is.")
        )
        return 0

    publish(api, headers, request, sha, exact, major, moves, notes, major in tags)
    print(f"Released {exact} at {sha[:7]}.")
    print(
        f"The major tag {major} now points to {exact}."
        if moves
        else f"The major tag {major} was not moved: a higher {version[0]}.x release exists."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except WorkflowError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
