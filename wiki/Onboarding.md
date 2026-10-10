<!-- Generated from guides/onboarding.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`guides/onboarding.md`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/guides/onboarding.md). Changes made here are overwritten the next time the wiki is published.

English | [Dansk](Onboarding.da) | [Bahasa Melayu](Onboarding.ms)

# Onboarding a repository

How a DevOps professional makes a TirSystem repository use the shared
**Sync GitHub mirror metadata** workflow, and which runners it needs. Only
this workflow exists today; the quality-check and release workflows are
planned (see the [Project Plan](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/docs/project-plan.md)).

## What has been verified

| Item | Status |
| --- | --- |
| Gitea version | 1.27.3 |
| `.gitea/scoped_workflows/sync-github-metadata.yml` runs in this repository | Verified: run 16, `workflow_dispatch`, succeeded |
| The same workflow applies to other repositories automatically | **Not verified.** Confirm how scoped workflows are delivered on the instance (admin or organization settings) before relying on it. |

Until delivery is verified, onboard a repository by copying the workflow (below).

## Steps

1. **Check the prerequisites** in the repository: Actions are enabled, and a
   runner with the label `ubuntu-latest` and `python3` is online (see
   [Runners](#runners)).
2. **Configure one GitHub push mirror** in the repository settings
   (Settings, Repository, Mirror settings, Push mirror). The workflow fails
   when there are several GitHub mirrors. With none, it succeeds without
   syncing anything.
3. **Add the two secrets** in the repository (or organization) settings,
   using the scopes in [credentials.md](Credentials):
   - `TOKEN_FOR_GITEA`
   - `PAT_FOR_GITHUB` (the GitHub token only)
4. **Deliver the workflow:**
   - *If scoped workflows apply to the repository:* nothing to copy.
   - *Otherwise:* copy `.gitea/scoped_workflows/sync-github-metadata.yml`
     from this repository to `.gitea/workflows/` in the target repository.
     Pin the copy to a reviewed version of this repository and re-copy
     when it changes.
5. **Set a description and topics** on the Gitea repository, so there is
   something to sync.
6. **Run it once manually:** Actions, **Sync GitHub mirror metadata**,
   Run workflow. The log must end with `Synced description and topics to
   <owner>/<repo>.` and the GitHub repository must show the same description
   and topics.
7. If it fails, use [troubleshooting.md](Troubleshooting).

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
