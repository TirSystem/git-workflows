"""Tell the author of a pull request which comments are not in English (MIL-013).

Run by .gitea/workflows/english-comments.yml after the check. It reads the
findings file of tools/english_comments.py and keeps ONE comment on the pull
request:

    - findings: the comment mentions the author and lists each finding; an
      existing comment of this check is updated, never a second one added;
    - no findings: an existing comment of this check is marked resolved (and no
      longer mentions the author); with none nothing is written.

Settings come from the environment:

    GITEA_API_URL      Gitea API base, for example https://host/api/v1
    SOURCE_REPOSITORY  owner/repo of the pull request
    PR_NUMBER          the number of the pull request
    PR_AUTHOR          the login of the author, mentioned in the comment
    REPORT_TOKEN       a token that may comment on pull requests (a CI secret);
                       without it nothing is written and the step ends with a
                       warning (the check run itself still fails)
    FINDINGS_FILE      the JSON file written by english_comments.py --output
    RUN_URL            optional, linked in the comment

Every failure is printed as ``::error::[category] message`` with the categories
configuration, credentials, permissions and api; the token is never printed.
"""

import json
import os
import sys
import urllib.error
import urllib.request

MARKER = "<!-- english-comments-check -->"
REQUEST_TIMEOUT_SECONDS = 30
PAGE_SIZE = 50
MAX_ROWS = 30


class ReportError(RuntimeError):
    """A failure with a category: configuration, credentials, permissions or api."""

    def __init__(self, category: str, message: str) -> None:
        super().__init__(f"[{category}] {message}")


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
            raise ReportError("credentials", f"{detail}. The token was rejected.") from None
        if error.code == 403:
            raise ReportError(
                "permissions", f"{detail}. The token may not comment on pull requests."
            ) from None
        raise ReportError("api", detail) from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise ReportError("api", f"Gitea API is unreachable ({error}).") from None


def _cell(text: str, limit: int = 100) -> str:
    """Text safe for a table cell: no pipes, line breaks, mentions or backticks."""
    text = " ".join(text.split()).replace("|", "\\|").replace("`", "'").replace("@", "@​")
    return text if len(text) <= limit else text[: limit - 3] + "..."


def failing_body(author: str, findings: list[dict], run_url: str = "") -> str:
    rows = [
        f"| `{_cell(f['path'], 80)}` | {f['line']} | {_cell(str(f['language']))} {f['probability']} | {_cell(f['text'])} |"
        for f in findings[:MAX_ROWS]
    ]
    more = len(findings) - MAX_ROWS
    lines = [
        MARKER,
        f"@{author}, the **English comments** check found {len(findings)} comment(s) that do not look "
        "like English. Source code comments are written in English only.",
        "",
        "| File | Line | Looks like | Comment |",
        "| --- | --- | --- | --- |",
        *rows,
    ]
    if more > 0:
        lines.append(f"\n...and {more} more; see the run.")
    lines += [
        "",
        "Rewrite the comment in English. For a quotation or a name, add `english-comments: ignore` "
        "to the comment, or add the word to the allowed-words file.",
    ]
    if run_url:
        lines.append(f"\n[The run]({run_url})")
    return "\n".join(lines)


def resolved_body() -> str:
    return f"{MARKER}\nThe **English comments** check passes: every checked comment is in English."


def find_comment(api, headers, request, repository, number):
    """Return the newest comment of this check on the pull request, or None."""
    found = None
    page = 1
    while True:
        url = f"{api}/repos/{repository}/issues/{number}/comments?limit={PAGE_SIZE}&page={page}"
        comments = request(url, "GET", headers, None) or []
        for comment in comments:
            if MARKER in (comment.get("body") or ""):
                found = comment
        if len(comments) < PAGE_SIZE:
            return found
        page += 1


def main(request=request_json) -> int:
    env = os.environ
    token = env.get("REPORT_TOKEN", "")
    try:
        missing = [
            name
            for name in ("GITEA_API_URL", "SOURCE_REPOSITORY", "PR_NUMBER", "PR_AUTHOR", "FINDINGS_FILE")
            if not env.get(name)
        ]
        if missing:
            raise ReportError("configuration", f"{', '.join(missing)} not set.")
        if not os.path.exists(env["FINDINGS_FILE"]):
            print("::warning::The check wrote no findings file (it did not run); nothing to report.")
            return 0
        try:
            with open(env["FINDINGS_FILE"], encoding="utf-8") as handle:
                findings = json.load(handle)
        except (OSError, ValueError):
            raise ReportError("configuration", f"findings file '{env['FINDINGS_FILE']}' cannot be read.") from None
        if not token:
            print("::warning::No REPORT_TOKEN: the pull request is not commented. The check itself still decides.")
            return 0
        api = env["GITEA_API_URL"].rstrip("/")
        repository = env["SOURCE_REPOSITORY"]
        number = env["PR_NUMBER"]
        headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}
        existing = find_comment(api, headers, request, repository, number)
        if findings:
            body = failing_body(env["PR_AUTHOR"], findings, env.get("RUN_URL", ""))
        elif existing:
            body = resolved_body()
        else:
            print("No findings and no earlier comment: nothing to write.")
            return 0
        if existing:
            if existing.get("body") != body:
                request(f"{api}/repos/{repository}/issues/comments/{existing['id']}", "PATCH", headers, {"body": body})
            print("Updated the comment of the check.")
        else:
            request(f"{api}/repos/{repository}/issues/{number}/comments", "POST", headers, {"body": body})
            print("Wrote a comment on the pull request.")
        return 0
    except ReportError as error:
        print(f"::error::{error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
