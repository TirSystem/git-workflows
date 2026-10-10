# Onboarding a repository

How a DevOps professional makes a TirSystem repository use the shared
**Sync GitHub mirror metadata** workflow, and which runners it needs. Only
this workflow exists today; the quality-check and release workflows are
planned (see the [Project Plan](../docs/project-plan.md)).

## What has been verified

| Item | Status |
| --- | --- |
| Gitea version | 1.27.3 |
| `.gitea/scoped_workflows/sync-github-metadata.yml` runs in this repository | Verified: run 16, `workflow_dispatch`, succeeded |
| The same workflow applies to other repositories automatically | Verified on 2026-10-10: it ran, with no copy in the repository, in repositories of `TirSystem`, `TirSystem-BashScript`, `vl-staal` and `Tirsvad-Udemy-100-days-of-code` (for example `TirSystem/sqa-qc-checklists` and `TirSystem-BashScript/RepoFoundry`). The script it ran changed when this repository's changed. |

Delivery is automatic, so a repository needs no copy of the workflow. Secrets are not shared between organisations: each organisation needs its own (step 3).

## Steps

1. **Check the prerequisites** in the repository: Actions are enabled, and a
   runner with the label `ubuntu-latest` and `python3` is online (see
   [Runners](#runners)).
2. **Configure one GitHub push mirror** in the repository settings
   (Settings, Repository, Mirror settings, Push mirror). The workflow fails
   when there are several GitHub mirrors. With none, it succeeds without
   syncing anything.
3. **Add the two secrets** in the repository (or organization) settings,
   using the scopes in [credentials.md](credentials.md). The workflow runs in
   every repository of an organization, so store the secrets once per
   organization; a repository in another organization does not see them:
   - `TOKEN_FOR_GITEA`
   - `PAT_FOR_GITHUB` (the GitHub token only)
4. **Deliver the workflow:** scoped workflows apply to every repository on
   this instance, so there is nothing to copy. Only where scoped delivery is
   not set up, copy `.gitea/scoped_workflows/sync-github-metadata.yml` from
   this repository to `.gitea/workflows/` in the target repository, pin the
   copy to a reviewed version and re-copy when it changes.
5. **Set a description and topics** on the Gitea repository, so there is
   something to sync.
6. **Run it once manually:** Actions, **Sync GitHub mirror metadata**,
   Run workflow. The log must end with `Synced description and topics to
   <owner>/<repo>.` and the GitHub repository must show the same description
   and topics.
7. If it fails, use [troubleshooting.md](troubleshooting.md).

## Runners

| Item | Value |
| --- | --- |
| Label the workflow uses | `ubuntu-latest` |
| Labels offered by the runner on this instance | `ubuntu-latest`, `ubuntu-24.04`, `ubuntu-22.04` |
| Tools the workflow needs | `python3` (standard library only), outbound HTTPS to the Gitea API and `api.github.com` |
| Needed for `actions/checkout` (used by the validation workflow) | `git` and Node.js, normally in the runner image |

**Check that a suitable runner is online** (needs permission to view runners):

```bash
curl -s -H "Authorization: token $GITEA_TOKEN" \
  https://git.tirsystem.com/api/v1/repos/<owner>/<repo>/actions/runners
```

For runners shared by the whole instance, an administrator uses
`/api/v1/admin/actions/runners`. At the time of writing the repository and
organization lists are empty and one instance-level runner (`36cd20104923`)
is `online`.

**Offline or incompatible runner**

| Symptom | Likely cause | Action |
| --- | --- | --- |
| Run stays `waiting` | No online runner has the label in `runs-on` | Start the runner, or register one with the label |
| Job fails at the start with a missing command | Runner image lacks `python3`, `git` or Node.js | Use an image that has them |
| Job cannot reach the API | Runner has no outbound HTTPS | Fix runner network or proxy settings |
