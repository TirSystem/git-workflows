# Workflow credentials

The sync workflow uses two secrets. Give each the least privilege that works,
store it only as a Gitea secret, and rotate it when a person with access
leaves.

| Secret | Content | Used for |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_REPO` | The Gitea token, nothing else | Reading the repository (description, topics) and its push mirrors |
| `PAT_FOR_GITHUB` | The GitHub token, nothing else | Changing the description and topics of the GitHub mirror |

## Minimum permissions

These were checked on 2026-10-10 against the Gitea source (the route
definitions in `routers/api/v1/api.go`, `main` branch) and the GitHub page
"Permissions required for fine-grained personal access tokens", for every API
call the workflows make. S01, standing in for S05 (ADR-0002), approved them on
2026-10-10. They have **not been tested on this instance with a token that
holds only these permissions**; the checks at the end of this section are the
way to do that.

**Gitea token** (a personal access token of a user, not a deploy key; deploy
keys do not work for the REST API):

- scope `read:repository`: every `/repos/...` route needs the repository
  scope, and the calls below only read
- the user must be an administrator of the repository: the `push_mirrors`
  routes require repository administration in addition to the token scope

Calls made: `GET /repos/{owner}/{repo}` and `GET /repos/{owner}/{repo}/push_mirrors`.

**GitHub token** (fine-grained personal access token):

- Resource owner: the owner of the mirror repository
- Repository access: only the mirror repository
- Repository permission: **Administration: Read and write** (no other
  permission); it is needed for `PATCH /repos/{owner}/{repo}` and
  `PUT /repos/{owner}/{repo}/topics`. `Metadata: Read` is added automatically
  and covers `GET /repos/{owner}/{repo}`.
- Set an expiry date

Calls made: `GET /repos/{owner}/{repo}`, `PATCH /repos/{owner}/{repo}` (description)
and `PUT /repos/{owner}/{repo}/topics`.

**Gitea token for the wiki** (see "Wiki publishing secret" below): scope
`write:repository`, because writing a page (`POST`, `PATCH`, `DELETE` under
`/repos/{owner}/{repo}/wiki`) needs the repository scope with write access, and
the user needs write access to the repository's wiki. Listing and reading
pages needs only the read scope.

**Testing the permissions on the instance (optional)**

1. In the Gitea settings of the user, the token stored as `TOKEN_FOR_GITEA_REPO`
   lists only `read:repository`, the user is an administrator of the
   repository, and a run still ends with `Preflight passed`.
2. The GitHub token lists only the mirror repository and
   `Administration: Read and write` (plus the automatic `Metadata: Read`), and
   a run ends with `Preflight passed` and `Synced description and topics`.
3. A throwaway token that lacks one of these permissions makes the run fail
   with `[permissions]` (or HTTP 403 for Gitea) and names the category,
   without printing the token.

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
`[permissions]`; see [troubleshooting.md](troubleshooting.md). No secret value
is ever printed.

## Wiki publishing secret

The workflow **Publish wiki pages** copies `docs/wiki/` to the Gitea wiki of a
repository that has a `docs/wiki/` folder (see [onboarding.md](onboarding.md)).
It uses its own secret, so the metadata sync token stays read-only.

| Secret | Content | Used for |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_WIKI` | The Gitea token, nothing else | Writing the wiki pages of the repositories of an organization that have a `docs/wiki/` folder |

- Store it as a secret of the organization of each repository that publishes.
  There is no fallback to `TOKEN_FOR_GITEA_REPO`: a repository with a
  `docs/wiki/` folder and no such secret fails with a configuration error, and a
  repository without the folder does not need it.
- The token needs scope `write:repository`, and its user needs write access to
  the repositories. Gitea has no wiki-only scope, so create the token for a
  dedicated user. S05 approves the scope and S03 stores the secret.
- Calls made: `GET /repos/{owner}/{repo}`, `GET /repos/{owner}/{repo}/wiki/pages`,
  `GET`, `POST` and `PATCH /repos/{owner}/{repo}/wiki/...` and, for a page that
  no longer exists in `docs/wiki/`, `DELETE /repos/{owner}/{repo}/wiki/page/{name}` (only when pruning is switched on, which the scoped workflow does not do).
- The wiki must be enabled in the repository settings. The workflow refuses to
  run when it is not.
- Pages that are in `docs/wiki/` are always overwritten from it, so a change
  made in the Gitea web UI is lost on the next publish. Pages that are only in
  the wiki are kept.

## Release secret

The scoped workflow **Release** (ADR-0017) creates the version tag, the release
page and, from version 1.0.0, the major tag of any repository of an
organization. It is started by hand (see [release-process.md](release-process.md)).
It writes with its own secret, so no other token needs to write tags.

| Secret | Content | Used for |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_RELEASE` | The Gitea token, nothing else | Creating the tag and the release page, and moving the major tag, in the repository the workflow is started in |

- Store it as a secret of the organization of each repository that is released.
  There is no fallback to the token of the run, to `TOKEN_FOR_GITEA_REPO` or to
  any other secret: a run without it ends as `[configuration]` and names the
  secret, even as a dry run.
- The token needs scope `write:repository`, and its user needs write access to
  the repositories. Gitea has no tag-only scope, so create the token for a
  dedicated user. S05 approves the scope and S03 stores the secret.
- The workflow reads it in the environment of the one step that runs the script;
  it never appears on a command line or in the log. The workflow itself has
  `permissions: contents: read`.
- Calls made (a test compares this list with the script):
  - `GET /repos/{owner}/{repo}` (the default branch)
  - `GET /repos/{owner}/{repo}/branches/{branch}` (the tip of the default branch)
  - `GET /repos/{owner}/{repo}/commits/{sha}/status` (the status `Validate / validate (push)`)
  - `GET /repos/{owner}/{repo}/tags`
  - `POST /repos/{owner}/{repo}/releases` (the release page; Gitea creates the version tag with it)
  - `POST /repos/{owner}/{repo}/tags` (the major tag `vN`)
  - `DELETE /repos/{owner}/{repo}/tags/{tag}` (the major tag `vN`, before it is created again at the new commit)

  A dry run makes only the `GET` calls.
- A secret that can write tags and release pages in every repository of an
  organization is a high-value target (ADR-0017). It is limited by the dedicated
  user and by being stored per organization.
- **Not yet verified on the instance:** whether the token behaves as the
  decision assumes in a scoped run (it can create a tag and a page and move a
  tag) is the first task of MIL-018. Until that is recorded, treat the scope and
  the list of calls above as the decision, not as a tested result.

## Milestone publishing secrets

The scoped workflow **Publish accepted milestones** (ADR-0018, [guide](sync-milestones.md))
publishes the accepted milestones of a repository that has a `docs/milestones/`
folder as Gitea Milestones and Issues. It uses two organization secrets and
reads no other name.

| Secret | Content | Used for |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_REPO` | The Gitea token, nothing else | Reading the repositories: the project and the private framework, checked out over HTTPS |
| `TOKEN_FOR_GITEA_ISSUES` | The Gitea token, nothing else | Publishing: creating and updating issues and milestones, scope issues only |

- Store both as secrets of the organization of each repository that publishes.
  There is no fallback to an older name (`GITEA_TOKEN`, `SYNC_TOKEN`): a run
  without either ends as `[configuration]` and names it, and a repository without
  `docs/milestones/` needs neither.
- The workflow reads them in the environment of the steps that need them; they
  never appear on a command line or in the log. The workflow itself has
  `permissions: contents: read`.
- A copy of `sync-milestones.yml` in a repository's `.gitea/workflows/` is
  removed: it runs next to the scoped workflow and publishes twice.
- A token that publishes issues in every repository of an organization is
  reachable by every repository's workflows in that organization (ADR-0018).
- **Not yet verified on the instance:** that a scoped run can read both secrets
  and check out the private framework, and whether `framework/qc` is needed, is
  the first task of MIL-019. Until that is recorded, treat this as the decision,
  not as a tested result.

## Rotating a token

1. Create the new token with the permissions above.
2. Replace the secret value in the repository or organization settings.
3. Run the workflow manually and wait for `Preflight passed`.
4. Revoke the old token.
