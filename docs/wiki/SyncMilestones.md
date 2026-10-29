<!-- Generated from guides/sync-milestones.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`guides/sync-milestones.md`](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/sync-milestones.md). Changes made here are overwritten the next time the wiki is published.

**English** · [Dansk](SyncMilestones-da) · [Bahasa Melayu](SyncMilestones-ms)

# Publishing accepted milestones

How a project's accepted milestones become Milestones and Issues on Gitea with
the scoped workflow `sync-milestones.yml`. It replaces the copy of
`sync-milestones.yml` that a repository used to keep in `.gitea/workflows/`. Its
decision is ADR-0018 in this repository; when a repository uses it is set out in
the [adoption rules](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/adoption-rules.md#publish-accepted-milestones).

## What it does

For every milestone document in `docs/milestones/` it creates or updates the
Gitea Milestone and one Issue per task row, through
`framework/scripts/ci-publish-milestones.sh publish`, which runs
`sync-project.sh --accepted-only`. Only a milestone whose latest Version History
row is `Accepted` and whose latest review record is a Go is published. A
`Proposed` milestone, or one without a Go review, is skipped with the reason in
the log.

## The folder is the opt-in

The workflow is scoped: the instance runs it in every repository of the
organization, so a repository adds no file. A repository publishes when it has the
folder `docs/milestones/`. A repository without it ends green, prints that there
is nothing to publish and makes no API call.

## The secrets

Two organization secrets, stored in the organization of each repository that
publishes. There is no fallback: a run without either ends as `[configuration]`
and names it. No older name (`GITEA_TOKEN`, `SYNC_TOKEN`) is read, and no token
is printed or put on a command line.

| Secret | Used for |
| --- | --- |
| `TOKEN_FOR_GITEA_REPO` | Reading the repositories: the project and the private framework, over HTTPS |
| `TOKEN_FOR_GITEA_ISSUES` | Publishing: issues and milestones only |

Scopes, who stores them and how to rotate them are in
[credentials.md](Credentials).

## Where the framework scripts come from

The milestone scripts are those of the framework. The workflow takes them from
one of two sources and prints which one in the log:

- **The project's own submodule** when `framework/scripts/ci-publish-milestones.sh`
  exists in the repository. The scripts are the release the project pinned.
- **A pinned release** otherwise: the framework repository is checked out into
  `framework/` at the tag `FRAMEWORK_TAG` of `tools/sync_milestones.py`. The tag
  moves only in a release of this repository, and a branch is never used. A
  project without the submodule can therefore publish too.

The log line names the source and the tag or commit it used.

## A push publishes, a manual run is a dry run

| Start | What happens |
| --- | --- |
| Push to the default branch that changes `docs/milestones/**` or `docs/sqa/reviews/**` | Publishes (`--apply`) |
| Manual run (`workflow_dispatch`) with `dry_run` on (the default) | Prints the plan and creates nothing |
| Manual run with `dry_run` switched off | Publishes |

`--accepted-only` is always passed. Runs queue in the group
`publish-accepted-milestones` and a run never cancels another. The workflow has
`permissions: contents: read`.

## Nothing is closed or deleted

A milestone removed from `docs/milestones/` leaves its Milestone and issues on
Gitea as they are. The workflow has no option that closes or deletes. Each real
run edits the issues of every accepted milestone, and the host records each edit.

## Remove an old copy

A copy of `sync-milestones.yml` in `.gitea/workflows/` runs next to the scoped
workflow and publishes twice. Delete the copy in a pull request of its
repository; the scoped workflow needs no file in its place. Installing the
framework template `templates/ci/` for this workflow is no longer needed.

## Still to be verified on the instance

ADR-0018 rests on facts that MIL-019 task 1 has not yet verified in a scoped run:

- that the organization secrets `TOKEN_FOR_GITEA_REPO` and `TOKEN_FOR_GITEA_ISSUES`
  can be read;
- that the private framework can be checked out over HTTPS;
- whether the nested `framework/qc` submodule is needed by the scripts (the copy
  fetched it with `--recursive`).

Until that is recorded, treat this guide as the decision, not as a tested result.
