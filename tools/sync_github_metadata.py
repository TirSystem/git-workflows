"""Copy the description and topics of a Gitea repository to its GitHub push mirror.

Run by the scoped workflow sync-github-metadata.yml, which checks out this
repository and runs this file (MIL-004 task 6). It reads its settings from the
environment:

    GITEA_API_URL        Gitea API base, for example https://host/api/v1
    GITEA_CREDENTIALS    the Gitea token, as clear text (TOKEN_FOR_GITEA)
    SOURCE_REPOSITORY    owner/repo of the repository whose metadata is synced
    PAT_FOR_GITHUB       the GitHub token, as clear text

Every failure is printed as ``ERROR: [category] message`` with the categories
configuration, credentials, permissions and api; no secret value is printed.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


class WorkflowError(RuntimeError):
    """A failure with a category.

    configuration: a secret or repository setting is missing or malformed.
    credentials:   a service rejected the token (HTTP 401).
    permissions:   the token is valid but not allowed (HTTP 403).
    api:           any other API or network failure.
    """

    def __init__(self, category, message):
        super().__init__(f"[{category}] {message}")
        self.category = category


def service_name(url):
    hostname = urllib.parse.urlsplit(url).hostname
    return "GitHub" if hostname == "api.github.com" else "Gitea"


def request_json(url, method="GET", headers=None, body=None):
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers=headers or {},
        method=method,
    )
    service = service_name(url)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
            return json.loads(content) if content else None
    except urllib.error.HTTPError as error:
        detail = (
            f"{service} API request failed with HTTP "
            f"{error.code} ({error.reason})"
        )
        if error.code == 401:
            raise WorkflowError(
                "credentials", f"{detail}. The token was rejected."
            ) from None
        if error.code == 403:
            raise WorkflowError(
                "permissions",
                f"{detail}. The token lacks a required permission.",
            ) from None
        if error.code == 404:
            raise WorkflowError(
                "configuration",
                f"{detail}. The repository was not found or the "
                "token cannot see it.",
            ) from None
        raise WorkflowError("api", detail) from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise WorkflowError(
            "api", f"{service} API is unreachable ({error})."
        ) from None


def parse_github_token(raw_token):
    token = (raw_token or "").strip()
    if not token:
        raise WorkflowError(
            "configuration", "PAT_FOR_GITHUB is missing or empty."
        )
    return token


def parse_gitea_token(raw_token):
    token = (raw_token or "").strip()
    if not token:
        raise WorkflowError(
            "configuration", "TOKEN_FOR_GITEA is missing or empty."
        )
    return token


def split_repository(full_name):
    owner, separator, repo = (full_name or "").partition("/")
    if not separator or not owner or not repo:
        raise WorkflowError(
            "configuration",
            "Could not determine the Gitea source repository.",
        )
    return owner, repo


def find_github_targets(mirrors):
    targets = []
    for mirror in mirrors:
        remote_address = mirror.get("remote_address", "")
        if remote_address.startswith("git@github.com:"):
            mirror_path = remote_address.split(":", 1)[1]
        else:
            parsed_remote = urllib.parse.urlsplit(remote_address)
            if parsed_remote.hostname != "github.com":
                continue
            mirror_path = parsed_remote.path.lstrip("/")

        mirror_path = mirror_path.removesuffix(".git").strip("/")
        path_parts = mirror_path.split("/")
        if len(path_parts) != 2 or not all(path_parts):
            raise WorkflowError(
                "configuration",
                "Could not determine the GitHub owner and repository "
                "from a configured push mirror.",
            )
        targets.append(tuple(path_parts))

    if not targets:
        return None
    if len(targets) != 1:
        raise WorkflowError(
            "configuration",
            "Expected at most one GitHub push mirror for this repository; "
            f"found {len(targets)}.",
        )
    return targets[0]


def main():
    gitea_token = parse_gitea_token(os.environ.get("GITEA_CREDENTIALS"))
    source_owner, source_repo = split_repository(
        os.environ.get("SOURCE_REPOSITORY")
    )

    gitea_api_url = os.environ["GITEA_API_URL"].rstrip("/")
    source_url = f"{gitea_api_url}/repos/{source_owner}/{source_repo}"
    gitea_headers = {
        "Authorization": f"token {gitea_token}",
        "Accept": "application/json",
    }
    source = request_json(source_url, headers=gitea_headers)
    mirrors = request_json(
        f"{source_url}/push_mirrors",
        headers=gitea_headers,
    )
    if not isinstance(mirrors, list):
        print(
            "WARNING: Gitea returned an invalid push mirror list; "
            "GitHub metadata was not synced."
        )
        return 0

    target = find_github_targets(mirrors)
    if target is None:
        print(
            "No GitHub push mirror configured for "
            f"{source_owner}/{source_repo}; nothing to sync."
        )
        print("Skipped")
        return 0

    github_token = parse_github_token(os.environ.get("PAT_FOR_GITHUB"))
    github_owner, github_repo = target
    github_api_url = (
        "https://api.github.com/repos/"
        f"{urllib.parse.quote(github_owner, safe='')}/"
        f"{urllib.parse.quote(github_repo, safe='')}"
    )
    github_headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }

    github_repository = request_json(github_api_url, headers=github_headers)
    permissions = (github_repository or {}).get("permissions")
    if isinstance(permissions, dict) and not permissions.get("admin"):
        raise WorkflowError(
            "permissions",
            f"The GitHub token cannot administer {github_owner}/{github_repo}; "
            "editing the description and topics needs administration access.",
        )
    print("Preflight passed: Gitea and GitHub accepted the credentials.")

    request_json(
        github_api_url,
        method="PATCH",
        headers=github_headers,
        body={"description": source.get("description") or ""},
    )
    request_json(
        f"{github_api_url}/topics",
        method="PUT",
        headers=github_headers,
        body={"names": source.get("topics") or []},
    )

    print(f"Synced description and topics to {github_owner}/{github_repo}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
