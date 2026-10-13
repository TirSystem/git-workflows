"""Publish the pages in wiki/ to the Gitea wiki of the repository.

Run by the scoped workflow publish-wiki.yml, which checks out the repository
that owns the wiki and this repository, and runs this file (MIL-004 task 6).
A repository publishes only when it has opted in with wiki/.publish
(ADR-0004); the word prune in that file lets the run delete wiki pages that
are not in wiki/. It reads its settings from the environment:

    GITEA_API_URL        Gitea API base, for example https://host/api/v1
    SOURCE_REPOSITORY    owner/repo of the repository whose wiki is written
    WIKI_CREDENTIALS     the Gitea token, as clear text (TOKEN_FOR_GITEA_WIKI)
    WIKI_DIR             directory with the pages (default: wiki)

Every failure is printed as ``ERROR: [category] message`` with the categories
configuration, credentials, permissions and api; no secret value is printed.
"""

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PAGE_LIMIT = 50
REQUEST_TIMEOUT_SECONDS = 30
COMMIT_MESSAGE = "Publish wiki from the repository"
MARKER_NAME = ".publish"
PRUNE_WORD = "prune"


class WorkflowError(RuntimeError):
    """A failure with a category.

    configuration: a secret, a setting or the wiki source is missing or malformed.
    credentials:   Gitea rejected the token (HTTP 401).
    permissions:   the token is valid but not allowed (HTTP 403).
    api:           any other API or network failure.
    """

    def __init__(self, category, message):
        super().__init__(f"[{category}] {message}")
        self.category = category
        self.detail = message


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


def parse_marker(text):
    """Return True when the marker asks for pruning, False when it is empty."""
    word = (text or "").strip()
    if not word:
        return False
    if word == PRUNE_WORD:
        return True
    raise WorkflowError(
        "configuration",
        f"wiki/{MARKER_NAME} may only be empty or contain the word '{PRUNE_WORD}'.",
    )


def parse_gitea_token(raw_token):
    token = (raw_token or "").strip()
    if not token:
        raise WorkflowError(
            "configuration",
            "TOKEN_FOR_GITEA_WIKI is missing or empty. Store it as a secret of "
            "the organization of this repository.",
        )
    return token


def describe_token(token):
    """Describe the shape of a token without revealing any of its characters."""
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


def split_repository(full_name):
    owner, separator, repo = (full_name or "").partition("/")
    if not separator or not owner or not repo:
        raise WorkflowError("configuration", "Could not determine the Gitea repository.")
    return owner, repo


def page_key(title):
    """Return the identity of a page: Gitea stores a space as a hyphen.

    The page "Home da" is the file Home-da.md and its address is Home-da, so
    both spellings must name the same page.
    """
    return str(title).replace(" ", "-")


def page_title(key):
    """Return the title to send to Gitea for a page key.

    A hyphen in a title is a literal hyphen to Gitea, which then stores the page
    as Home-da.-.md and addresses it as Home%2Dda, so a link to Home-da finds
    nothing. A space is stored as a hyphen (Home-da.md) and addressed as Home-da.
    """
    return key.replace("-", " ")


def read_pages(wiki_dir):
    """Return {page key: content} for every Markdown file in wiki_dir."""
    pages = {}
    for path in sorted(wiki_dir.glob("*.md")):
        key = page_key(path.stem)
        if key in pages:
            raise WorkflowError(
                "configuration",
                f"Two files in {wiki_dir} name the wiki page {key}; a space and "
                "a hyphen are the same in a page name.",
            )
        pages[key] = path.read_bytes()
    if not pages:
        # Publishing an empty directory would delete the whole wiki.
        raise WorkflowError(
            "configuration", f"The wiki source directory {wiki_dir} has no Markdown pages."
        )
    return pages


def list_wiki_titles(wiki_url, headers, send):
    """Return the keys of the pages that exist in the wiki.

    The key is the address Gitea reports (sub_url), or the title with its
    spaces replaced by hyphens.

    Gitea answers 404 for a wiki that has never been written to; that is an
    empty wiki, not a failure.
    """
    titles = set()
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
        titles.update(
            urllib.parse.unquote(str(item.get("sub_url") or ""))
            or page_key(item.get("title", ""))
            for item in batch
        )
        if len(batch) < PAGE_LIMIT:
            return titles
        page += 1


def read_wiki_page(wiki_url, title, headers, send):
    quoted = urllib.parse.quote(title, safe="")
    page = send(f"{wiki_url}/page/{quoted}", headers=headers)
    return base64.b64decode((page or {}).get("content_base64", ""))


def publish(pages, wiki_url, headers, send, prune):
    """Create and update the pages; delete the others only when prune is set.

    Returns the titles created, updated and deleted, and the titles that were
    left in the wiki because pruning is off.
    """
    existing = list_wiki_titles(wiki_url, headers, send)
    current = {
        title: read_wiki_page(wiki_url, title, headers, send)
        for title in sorted(existing & pages.keys())
    }

    result = {"created": [], "updated": [], "deleted": [], "kept": []}
    for title, content in pages.items():
        body = {
            "title": page_title(title),
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
        if not prune:
            result["kept"].append(title)
            continue
        quoted = urllib.parse.quote(title, safe="")
        send(f"{wiki_url}/page/{quoted}", method="DELETE", headers=headers)
        result["deleted"].append(title)
    return result


def main():
    wiki_dir = Path(os.environ.get("WIKI_DIR", "wiki"))
    owner, repo = split_repository(os.environ.get("SOURCE_REPOSITORY"))

    marker = wiki_dir / MARKER_NAME
    if not marker.is_file():
        print(
            f"No {wiki_dir}/{MARKER_NAME} marker in {owner}/{repo}; "
            "wiki publishing is not enabled for this repository."
        )
        return 0
    prune = parse_marker(marker.read_text(encoding="utf-8"))

    pages = read_pages(wiki_dir)
    token = parse_gitea_token(os.environ.get("WIKI_CREDENTIALS"))

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
                f"The wiki is not enabled on {owner}/{repo}. Enable it in the "
                "repository settings.",
            )
        print("Preflight passed: Gitea accepted the token and the wiki is enabled.")

        result = publish(pages, f"{repository_url}/wiki", headers, request_json, prune)
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
    if result["kept"]:
        print(
            f"{len(result['kept'])} page(s) are in the wiki but not in "
            f"{wiki_dir}/ and were kept; put the word '{PRUNE_WORD}' in "
            f"{wiki_dir}/{MARKER_NAME} to delete them."
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except WorkflowError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
