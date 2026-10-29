"""Clean up old data of a Gitea repository. Run by a person, never by an agent.

Dry run by default: it prints what it would delete and deletes nothing. Add
--apply to delete. Each part is chosen by an option, so nothing is touched that
was not asked for.

  --wiki-renamed     delete wiki pages named <Page>.<code> (for example Home.da)
                     whose renamed page <Page>-<code> exists
  --releases         delete release pages except the newest --keep-latest N and
                     the tags in --keep; the tags themselves are not touched
  --branch NAME      force-delete a local branch of --clone (repeatable)

Examples:
  python gitea_cleanup.py --repo git-workflows --wiki-renamed
  python gitea_cleanup.py --repo sqa-qc-framework --releases --keep-latest 3
  python gitea_cleanup.py --repo sqa-qc-framework --releases --keep v0.19.0 --branch old-branch \\
      --clone E:/repos/TirSystem/sqa-qc-framework --apply

Tokens come from the .env file (default: ./.env), by name: --wiki-token-name
(default TOKEN_FOR_GITEA_WIKI) for the wiki and --repo-token-name (default
TOKEN_FOR_GITEA_REPO) for releases. They are never printed.
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


def read_token(env_file: str, name: str) -> str:
    """Return the value of ``name`` in the env file, or exit when it is missing."""
    with open(env_file, encoding="utf-8") as handle:
        match = re.search(rf"^{re.escape(name)}=(.+)$", handle.read(), re.M)
    if not match:
        sys.exit(f"{name} is missing in {env_file}")
    return match.group(1).strip().strip('"').strip("'")


def call(method: str, url: str, token: str):
    """Call the API and return the decoded JSON body, or exit on an HTTP error."""
    request = urllib.request.Request(url, method=method, headers={"Authorization": "token " + token})
    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        sys.exit(f"{method} {url} failed: HTTP {error.code}")


def renamed_wiki_pages(titles: list[str]) -> list[str]:
    """Return the pages named <Page>.<code> whose <Page>-<code> page exists."""
    return sorted(
        title for title in titles
        if re.fullmatch(r"[A-Za-z0-9]+\.[a-z]{2,3}", title) and title.replace(".", "-") in titles
    )


def old_releases(releases: list[dict], keep_latest: int, keep: set[str]) -> list[dict]:
    """Return the releases that are neither among the newest nor in ``keep``."""
    newest = [r["tag_name"] for r in releases[:keep_latest]]
    return [r for r in releases if r["tag_name"] not in keep and r["tag_name"] not in newest]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--api", default="https://git.tirsystem.com/api/v1")
    parser.add_argument("--owner", default="TirSystem")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--wiki-token-name", default="TOKEN_FOR_GITEA_WIKI")
    parser.add_argument("--repo-token-name", default="TOKEN_FOR_GITEA_REPO")
    parser.add_argument("--wiki-renamed", action="store_true")
    parser.add_argument("--releases", action="store_true")
    parser.add_argument("--keep-latest", type=int, default=1)
    parser.add_argument("--keep", action="append", default=[], metavar="TAG")
    parser.add_argument("--branch", action="append", default=[], metavar="NAME")
    parser.add_argument("--clone", help="the local clone for --branch")
    parser.add_argument("--apply", action="store_true", help="delete (default: dry run)")
    args = parser.parse_args(argv)
    if not (args.wiki_renamed or args.releases or args.branch):
        parser.error("choose --wiki-renamed, --releases or --branch")
    if args.branch and not args.clone:
        parser.error("--branch needs --clone")

    base = f"{args.api}/repos/{args.owner}/{args.repo}"
    print("APPLY" if args.apply else "DRY RUN (nothing is deleted; add --apply)")

    if args.wiki_renamed:
        token = read_token(args.env_file, args.wiki_token_name)
        titles = [p["title"] for p in call("GET", f"{base}/wiki/pages?limit=200", token)]
        found = renamed_wiki_pages(titles)
        print(f"\nWiki pages to delete ({len(found)}):")
        for title in found:
            print("  ", title)
            if args.apply:
                call("DELETE", f"{base}/wiki/page/{urllib.parse.quote(title, safe='')}", token)

    if args.releases:
        token = read_token(args.env_file, args.repo_token_name)
        releases = call("GET", f"{base}/releases?limit=100", token)
        found = old_releases(releases, args.keep_latest, set(args.keep))
        print(f"\nRelease pages to delete ({len(found)}; tags stay):")
        for release in found:
            print("  ", release["tag_name"])
            if args.apply:
                call("DELETE", f"{base}/releases/{release['id']}", token)

    for branch in args.branch:
        print(f"\nLocal branch to delete in {args.clone}: {branch}")
        if args.apply:
            subprocess.run(["git", "-C", args.clone, "branch", "-D", branch], check=False)

    print("\nDone." if args.apply else "\nDry run done. Run again with --apply to delete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
