<!-- Generated from guides/credentials.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`guides/credentials.md`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/guides/credentials.md). Changes made here are overwritten the next time the wiki is published.

English | [Dansk](Credentials.da) | [Bahasa Melayu](Credentials.ms)

# Workflow credentials

The sync workflow uses two secrets. Give each the least privilege that works,
store it only as a Gitea secret, and rotate it when a person with access
leaves.

| Secret | Content | Used for |
| --- | --- | --- |
| `TOKEN_FOR_GITEA` | The Gitea token, nothing else | Reading the repository (description, topics) and its push mirrors |
| `PAT_FOR_GITHUB` | The GitHub token, nothing else | Changing the description and topics of the GitHub mirror |

## Minimum permissions

These come from the Gitea and GitHub documentation and the API calls the
workflow makes. They have **not been confirmed with a minimal token on this
instance yet**; S05 should confirm them when the tokens are created.

**Gitea token** (a personal access token of a user, not a deploy key; deploy
keys do not work for the REST API):

- scope `read:repository`
- the user must be allowed to read the repository's push mirrors, which
  Gitea limits to repository administrators

Calls made: `GET /repos/{owner}/{repo}` and `GET /repos/{owner}/{repo}/push_mirrors`.

**GitHub token** (fine-grained personal access token):

- Resource owner: the owner of the mirror repository
- Repository access: only the mirror repository
- Repository permission: **Administration: Read and write** (no other permission)
- Set an expiry date

Calls made: `GET /repos/{owner}/{repo}`, `PATCH /repos/{owner}/{repo}` (description)
and `PUT /repos/{owner}/{repo}/topics`.

Format of `PAT_FOR_GITHUB`: only the token string (for example
`github_pat_...`), as clear text. The workflow only checks that it is not empty;
GitHub rejects a wrong value (HTTP 401).

## What the workflow checks before it changes anything

The workflow runs a preflight and writes nothing to GitHub unless it passes:

1. Both secrets exist and have the expected shape.
2. Gitea accepts the token and the repository is visible with it.
3. At most one GitHub push mirror is configured. With none, the run ends
   successfully without syncing and the GitHub secret is not read.
4. GitHub accepts the token for the mirror repository **and** the token
   reports administration access to it.

On success the log says `Preflight passed: Gitea and GitHub accepted the
credentials.` Failures start with a category such as `[credentials]` or
`[permissions]`; see [troubleshooting.md](Troubleshooting). No secret value
is ever printed.

## Wiki publishing secret

The workflow **Publish wiki** copies `wiki/` to the Gitea wiki of a repository
that has opted in with `wiki/.publish` (see [onboarding.md](Onboarding)). It
uses its own secret, so the metadata sync token stays read-only.

| Secret | Content | Used for |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_WIKI` | The Gitea token, nothing else | Writing the wiki pages of the repositories of an organization that opt in |

- Store it as a secret of the organization of each repository that publishes.
  There is no fallback to `TOKEN_FOR_GITEA`: a repository that opted in and has
  no such secret fails with a configuration error, and a repository that did
  not opt in does not need it.
- The token needs scope `write:repository`, and its user needs write access to
  the repositories. Gitea has no wiki-only scope, so create the token for a
  dedicated user. S05 approves the scope and S03 stores the secret.
- Calls made: `GET /repos/{owner}/{repo}`, `GET /repos/{owner}/{repo}/wiki/pages`,
  `GET`, `POST` and `PATCH /repos/{owner}/{repo}/wiki/...` and, for a page that
  no longer exists in `wiki/`, `DELETE /repos/{owner}/{repo}/wiki/page/{name}`.
- The wiki must be enabled in the repository settings. The workflow refuses to
  run when it is not.
- Pages that are in `wiki/` are always overwritten from it, so a change made
  in the Gitea web UI is lost on the next publish. Pages that are only in the
  wiki are removed only when `wiki/.publish` contains the word `prune`.

## Rotating a token

1. Create the new token with the permissions above.
2. Replace the secret value in the repository or organization settings.
3. Run the workflow manually and wait for `Preflight passed`.
4. Revoke the old token.
