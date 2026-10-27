# Diagnosing a failed run

Open the run in Gitea (Actions) and read the last lines of the failing step.
Every failure from the sync script is written as

```
ERROR: [<category>] <message>
```

The category tells you where to look. A failure outside the script (the job
never starts, or stops before the step) is a **runner** problem.

| Category | Meaning | First thing to check |
| --- | --- | --- |
| `configuration` | A secret or a repository setting is missing or malformed | Secret names and format, push mirror setup |
| `credentials` | A service rejected the token (HTTP 401) | Token expired, revoked or mistyped |
| `permissions` | The token is valid but not allowed (HTTP 403, or no GitHub administration access) | Token scopes and repository access |
| `api` | Another HTTP error, or the service was unreachable | Service status, runner network |
| runner | No `ERROR:` line; the run waits, or the job fails before the script | Runner online, label, tools |

## Messages and fixes

| Message (start) | Category | Cause and fix |
| --- | --- | --- |
| `PAT_FOR_GITHUB is missing or empty.` | configuration | Add the secret |
| `TOKEN_FOR_GITEA is missing or empty.` | configuration | Add the secret |
| `Could not determine the Gitea source repository.` | configuration | The run has no repository name; report as a defect |
| `Expected at most one GitHub push mirror ... found N` | configuration | Keep one GitHub push mirror |
| `TOKEN_FOR_GITEA_WIKI is missing or empty.` | configuration | Wiki publishing only: the repository has a `docs/wiki/` folder but its organization has no such secret; store it as an organization secret (see [credentials.md](credentials.md)) |
| `... HTTP 403 ...` while publishing the wiki | permissions | Wiki publishing only: the token needs `write:repository` and write access to this repository |
| `The wiki is not enabled on <repo>` | configuration | Wiki publishing only: enable the wiki in the repository settings |
| `The wiki source directory ... has no Markdown pages` | configuration | Wiki publishing only: the folder has no Markdown pages; nothing was changed |
| `Could not determine the GitHub owner and repository ...` | configuration | The mirror address must look like `https://github.com/<owner>/<repo>.git` |
| `Gitea API request failed with HTTP 401` | credentials | Create a new Gitea token and update `TOKEN_FOR_GITEA` |
| `GitHub API request failed with HTTP 401` | credentials | Create a new GitHub token and update `PAT_FOR_GITHUB`; the value must be the token only (no name, quotes or JSON) |
| `... HTTP 403 ...` (Gitea) | permissions | Token needs `read:repository`, and its user needs administrator access to the repository |
| `... HTTP 403 ...` (GitHub) | permissions | Token needs Administration read and write on the mirror repository |
| `The GitHub token cannot administer <repo>` | permissions | Same as above; the token can read the repository but not edit it |
| `... HTTP 404 ...` | configuration | Repository not found, or the token cannot see it; check the mirror address and token repository access |
| `... HTTP 5xx ...` | api | Service problem; re-run later |
| `... API is unreachable ...` | api | Network, DNS or proxy problem on the runner |

## Not an error

`No GitHub push mirror configured for <repo>; nothing to sync.` followed by
`Skipped`. The run succeeds. Not every Gitea repository has a GitHub mirror, so
this is expected for those. If the repository should have one, add it in the repository
settings.

`WARNING: Gitea returned an invalid push mirror list; GitHub metadata was not
synced.` The run succeeds but nothing was synced. Check that the Gitea
version supports the push mirror API and re-run.

`<n> page(s) are in the wiki but not in <folder>/ and were kept ...` The run
succeeds. Pages that exist only in the wiki are always left alone.

## Runner problems

See the [Runners](onboarding.md#runners) section. In short: if the run stays
`waiting`, no online runner has the label; if the job fails before the
script, the runner image is missing a tool.

## Re-running

Use **Run workflow** (`workflow_dispatch`) after fixing the cause. The sync is
safe to repeat: it overwrites the GitHub description and topics with the
Gitea values.
