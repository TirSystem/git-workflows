"""Publish the pages in ``wiki/`` to the Gitea wiki of this repository.

The pages are written through the Gitea wiki REST API. A page that is missing
in ``wiki/`` is removed from the wiki, so the wiki always equals the reviewed
source; edits made in the web UI are overwritten (MIL-005).

Environment:
    GITEA_API_URL        Gitea API base, for example https://host/api/v1
    SOURCE_REPOSITORY    owner/repo of the repository whose wiki is written
    WIKI_CREDENTIALS     bare token, JSON string, or JSON with GITEA_TOKEN
    WIKI_DIR             directory with the pages (default: wiki)

Exit codes: 0 published or nothing to do, 1 failed (message names a category).
"""

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

PAGE_LIMIT = 50
REQUEST_TIMEOUT_SECONDS = 30
COMMIT_MESSAGE = "Publish wiki from the repository"

JsonRequest = Callable[..., Any]


class WorkflowError(RuntimeError):
    """A failure with a category.

    configuration: a secret, a setting or the wiki source is missing or malformed.
    credentials:   Gitea rejected the token (HTTP 401).
    permissions:   the token is valid but not allowed (HTTP 403).
    api:           any other API or network failure.
    """

    def __init__(self, category: str, message: str) -> None:
        super().__init__(f"[{category}] {message}")
        self.category = category
        self.detail = message


def request_json(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
) -> Any:
    """Send one JSON request to Gitea and return the decoded response."""
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
        detail = f"Gitea API request failed with HTTP {error.code} ({error.reason})"
        if error.code == 401:
            raise WorkflowError("credentials", f"{detail}. The token was rejected.") from None
        if error.code == 403:
            raise WorkflowError(
                "permissions", f"{detail}. The token lacks a required permission."
            ) from None
        if error.code == 404:
            raise WorkflowError(
                "configuration",
                f"{detail}. The repository or page was not found, or the token "
                "cannot see it.",
            ) from None
        raise WorkflowError("api", detail) from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise WorkflowError("api", f"Gitea API is unreachable ({error}).") from None


def parse_gitea_token(raw_credentials: str | None) -> str:
    """Return the token from a bare value, a JSON string or JSON with GITEA_TOKEN."""
    raw_credentials = (raw_credentials or "").strip()
    if not raw_credentials:
        raise WorkflowError(
            "configuration",
            "No token for the wiki: set TOKEN_FOR_GITEA_WIKI, or TOKEN_FOR_GITEA.",
        )

    token: Any
    try:
        credentials = json.loads(raw_credentials)
    except json.JSONDecodeError:
        token = raw_credentials
    else:
        if isinstance(credentials, dict):
            token = credentials.get("GITEA_TOKEN")
        elif isinstance(credentials, str):
            token = credentials
        else:
            token = None

    if not isinstance(token, str) or not token.strip():
        raise WorkflowError(
            "configuration", "The wiki token must contain a non-empty GITEA_TOKEN."
        )
    return token.strip()


def describe_token(token: str) -> str:
    """Describe the shape of a token without revealing any of its characters.

    Used when Gitea rejects the token, so a wrongly stored secret (the masked
    text, ``NAME=value``, quotes) can be recognised from the log.
    """
    facts = [f"{len(token)} characters"]
    if re.fullmatch(r"[0-9a-f]{40}", token):
        facts.append("looks like a Gitea token (40 hexadecimal characters)")
        return ", ".join(facts)
    facts.append("a Gitea token has 40 hexadecimal characters")
    if set(token) <= {"*", "x", "X", "•"}:
        facts.append("only mask characters: the masked text was stored")
    if "=" in token:
        facts.append("contains '=': the secret name may be part of the value")
    if re.search(r"[\"'`]", token):
        facts.append("contains a quote character")
    if re.search(r"\s", token):
        facts.append("contains whitespace")
    return ", ".join(facts)


def split_repository(full_name: str | None) -> tuple[str, str]:
    """Split ``owner/repo`` into its two parts."""
    owner, separator, repo = (full_name or "").partition("/")
    if not separator or not owner or not repo:
        raise WorkflowError("configuration", "Could not determine the Gitea repository.")
    return owner, repo


def read_pages(wiki_dir: Path) -> dict[str, bytes]:
    """Return ``{page title: content}`` for every Markdown file in ``wiki_dir``."""
    if not wiki_dir.is_dir():
        raise WorkflowError("configuration", f"The wiki source directory {wiki_dir} is missing.")
    pages = {path.stem: path.read_bytes() for path in sorted(wiki_dir.glob("*.md"))}
    if not pages:
        # Publishing an empty directory would delete the whole wiki.
        raise WorkflowError(
            "configuration", f"The wiki source directory {wiki_dir} has no Markdown pages."
        )
    return pages


def list_wiki_titles(wiki_url: str, headers: dict[str, str], send: JsonRequest) -> set[str]:
    """Return the titles of the pages that exist in the wiki.

    Gitea answers 404 for a wiki that has never been written to; that is an
    empty wiki, not a failure.
    """
    titles: set[str] = set()
    page = 1
    while True:
        url = f"{wiki_url}/pages?page={page}&limit={PAGE_LIMIT}"
        try:
            batch = send(url, headers=headers)
        except WorkflowError as error:
            if error.category == "configuration" and page == 1:
                return titles
            raise
        if not isinstance(batch, list):
            raise WorkflowError("api", "Gitea returned an invalid wiki page list.")
        titles.update(str(item.get("title", "")) for item in batch)
        if len(batch) < PAGE_LIMIT:
            return titles
        page += 1


def read_wiki_page(
    wiki_url: str, title: str, headers: dict[str, str], send: JsonRequest
) -> bytes:
    """Return the current content of one wiki page."""
    quoted = urllib.parse.quote(title, safe="")
    page = send(f"{wiki_url}/page/{quoted}", headers=headers)
    encoded = (page or {}).get("content_base64", "")
    return base64.b64decode(encoded)


def publish(
    pages: dict[str, bytes],
    wiki_url: str,
    headers: dict[str, str],
    send: JsonRequest,
) -> dict[str, list[str]]:
    """Make the wiki equal ``pages``; return the titles created, updated, deleted."""
    existing = list_wiki_titles(wiki_url, headers, send)
    current = {
        title: read_wiki_page(wiki_url, title, headers, send)
        for title in sorted(existing & pages.keys())
    }

    result: dict[str, list[str]] = {"created": [], "updated": [], "deleted": []}
    for title, content in pages.items():
        body = {
            "title": title,
            "content_base64": base64.b64encode(content).decode("ascii"),
            "message": COMMIT_MESSAGE,
        }
        if title not in existing:
            send(f"{wiki_url}/new", method="POST", headers=headers, body=body)
            result["created"].append(title)
        elif current[title] != content:
            quoted = urllib.parse.quote(title, safe="")
            send(f"{wiki_url}/page/{quoted}", method="PATCH", headers=headers, body=body)
            result["updated"].append(title)

    for title in sorted(existing - pages.keys()):
        quoted = urllib.parse.quote(title, safe="")
        send(f"{wiki_url}/page/{quoted}", method="DELETE", headers=headers)
        result["deleted"].append(title)
    return result


def main() -> int:
    """Run the publish; return the process exit code."""
    wiki_dir = Path(os.environ.get("WIKI_DIR", "wiki"))
    pages = read_pages(wiki_dir)
    token = parse_gitea_token(os.environ.get("WIKI_CREDENTIALS"))
    owner, repo = split_repository(os.environ.get("SOURCE_REPOSITORY"))

    api_url = os.environ["GITEA_API_URL"].rstrip("/")
    repository_url = (
        f"{api_url}/repos/{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repo, safe='')}"
    )
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        repository = request_json(repository_url, headers=headers)
        if isinstance(repository, dict) and repository.get("has_wiki") is False:
            raise WorkflowError(
                "configuration",
                f"The wiki is not enabled on {owner}/{repo}. Enable it in the repository settings.",
            )
        print("Preflight passed: Gitea accepted the token and the wiki is enabled.")

        result = publish(pages, f"{repository_url}/wiki", headers, request_json)
    except WorkflowError as error:
        if error.category == "credentials":
            raise WorkflowError(
                "credentials", f"{error.detail} Token shape: {describe_token(token)}."
            ) from None
        raise
    print(
        f"Published {len(pages)} page(s) to the wiki of {owner}/{repo}: "
        f"{len(result['created'])} created, {len(result['updated'])} updated, "
        f"{len(result['deleted'])} deleted."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except WorkflowError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
