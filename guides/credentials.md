# Workflow credentials

The sync workflow uses two secrets. Give each the least privilege that works,
store it only as a Gitea secret, and rotate it when a person with access
leaves.

| Secret | Content | Used for |
| --- | --- | --- |
| `TOKEN_FOR_GITEA` | A bare token, a JSON string, or JSON with `GITEA_TOKEN` | Reading the repository (description, topics) and its push mirrors |
| `CREDENTIALS_FOR_GITHUB` | JSON object with a non-empty `GITHUB_PAT` | Changing the description and topics of the GitHub mirror |

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

Format of `CREDENTIALS_FOR_GITHUB`:

```json
{"GITHUB_PAT": "<token>"}
```

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

## Rotating a token

1. Create the new token with the permissions above.
2. Replace the secret value in the repository or organization settings.
3. Run the workflow manually and wait for `Preflight passed`.
4. Revoke the old token.
