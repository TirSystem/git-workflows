# ADR-0018: Publishing of accepted milestones as a scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0018 |
| CrossReference | [MIL-019], [ADR-0013], [ADR-0005], [MIL-015] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; reviewed (RC-102, Go-with-conditions), accepted by the author in chat as stand-in for S01 with the conditions of RC-102 still open, not independent | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

The workflow that publishes accepted milestones as Milestones and Issues
(`sync-milestones.yml`) is a copy in each project: this repository and
`sqa-and-qc` carry one, and the framework's template says how to install more.
Each copy has to be kept current; [MIL-015] task 9 and the framework template
showed a defect (the checkout and the token) that every copy then had to fix.
[ADR-0013] took the same step for the wiki: a scoped workflow where the folder
is the opt-in.

What the publishing needs, read from the files on 2026-10-29:

| Fact | Where it comes from |
| --- | --- |
| The publishing is `framework/scripts/ci-publish-milestones.sh publish`, which runs `sync-project.sh --accepted-only`, with `--apply` unless `DRY_RUN` is `true` | `framework/scripts/ci-publish-milestones.sh` |
| `sync-project.sh` finds the project as two directories above its own location, so the framework must sit at `<project>/framework`; it reads host, owner and repository from the `origin` remote | `framework/scripts/sync-project.sh` (the root line and the origin parsing) |
| The framework is a private submodule with `ssh://` URLs; the runner has no SSH key, so the submodules are fetched over HTTPS with `TOKEN_FOR_GITEA_REPO` | the copy in `.gitea/workflows/sync-milestones.yml` |
| The nested `framework/qc` submodule is fetched today (`--recursive`) | the same copy; whether the scripts need it is not known and [MIL-019] task 1 checks it |
| What a scoped run can read (the organization secrets, the private framework) | not known; [MIL-019] task 1 verifies it |

Options:

1. **Keep a copy per project.** Explicit, but a file to keep current in each
   project, which is the defect that started this.
2. **A scoped workflow that uses the project's own `framework/` submodule.**
   Nothing to copy, and the scripts are the release the project pinned; a project
   without the submodule cannot be published.
3. **A scoped workflow that fetches a pinned framework release** into
   `framework/` when the project has none, and uses the project's submodule
   when it has one. Every repository with `docs/milestones/` works.
4. **A scoped workflow that always fetches its own pinned release.** One source
   everywhere, but it overrides the pin a project chose and breaks a project whose
   documents need a different framework version.

## Decision

Accepted milestones are published by the scoped workflow
`.gitea/scoped_workflows/sync-milestones.yml`, which runs in every repository
and publishes when `docs/milestones/` exists; the copies are removed.

The rules that follow from it:

- **The opt-in is the folder** `docs/milestones/`. A repository without it ends
  green, prints that there is nothing to publish and makes no API call.
- **The scripts are a published release** (option 3): the project's own
  `framework/` submodule when `framework/scripts/ci-publish-milestones.sh`
  exists, otherwise the framework repository checked out into `framework/` at the
  pinned tag `FRAMEWORK_TAG` of `tools/sync_milestones.py` (moved only in a
  release of this repository). The log prints which source and which tag or
  commit it used. A branch is never used.
- **The secrets are organization secrets with no fallback:**
  `TOKEN_FOR_GITEA_REPO` reads the repositories (the project and the private
  framework, over HTTPS) and `TOKEN_FOR_GITEA_ISSUES` publishes (issues and
  milestones only). A run without either ends as `[configuration]` and names it;
  no older name (`GITEA_TOKEN`, `SYNC_TOKEN`) is read, and no token is printed or
  put on a command line.
- **A push publishes, a manual run is a dry run:** a push to the default branch
  that changes `docs/milestones/**` or `docs/sqa/reviews/**` runs with `--apply`;
  `workflow_dispatch` has the input `dry_run`, default `true`, which prints the
  plan and creates nothing.
- **Only accepted milestones:** `--accepted-only` is always passed, so a
  `Proposed` milestone, or one without a Go review, is never published.
- **Nothing is closed or deleted:** a milestone removed from the folder leaves
  its issues and Milestone untouched; the workflow has no option that closes or
  deletes.
- The workflow has `permissions: contents: read`, the group
  `publish-accepted-milestones` queues runs and never cancels one, and the logic
  is a file of this repository, `tools/sync_milestones.py`, fetched at the
  current major tag ([ADR-0005]).
- Installing the framework template in a repository is no longer needed; a copy
  there runs next to the scoped workflow and publishes twice, so each copy is
  removed in a pull request of its repository.

## Consequences

**Positive:**

- No project copies or updates the workflow; one fix reaches every repository.
- A repository without the submodule can publish its milestones.
- The source of the scripts is printed in every run.

**Negative:**

- A secret that publishes issues in every repository of an organization is
  reachable by every repository's workflows in that organization.
- The fetched release can differ from the one a project pinned only when it has
  no submodule; two sources of scripts to keep working.
- A run publishes on every push that changes the folders, in every repository
  that has them, and the host records each edit.
- The decision rests on facts [MIL-019] task 1 has not yet verified (the secrets
  and the private framework in a scoped run, and whether `framework/qc` is
  needed).

## Affected Artifacts

- [MIL-019] — the milestone this decision belongs to; tasks 3 to 6 follow it.
- [ADR-0013] — the same delivery: a scoped workflow where the folder is the opt-in.
- [ADR-0005] — the logic is a file, failures have categories.
- [MIL-015] — the secret names `TOKEN_FOR_<host>_<purpose>` and the checkout defect.

---

[MIL-019]: ../milestones/mil-019-scoped-milestone-sync.md
[ADR-0013]: ./adr-0013-wiki-publishing-scoped-workflow.md
[ADR-0005]: ./adr-0005-quality-check-contract.md
[MIL-015]: ../milestones/mil-015-rename-to-git-workflows.md
