# MIL-003: Shared quality checks

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-003 |
| CrossReference | [BC-001], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Deprecated | Jens Tirsvad Nielsen | S01 | Task 1 verified: workflow_call and uses work from the same repository, the same organization and another organization (RC-033) | [b3f006f] |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Task 4 recorded: adoption in RepoFoundry, the shfmt .editorconfig gap and the other findings (RC-039) | pending |

---

## Purpose

Decide whether a software engineer can run the same quality checks on any
TirSystem project through a shared workflow.

## Deliverable

A reusable quality-check workflow for Python and shell, used by at least one
other repository, and a guide for reading its results.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The instance supports reusable workflows (`workflow_call`), verified and recorded | Verified | Unsupported (re-plan as a copied template) |
| 2 | One other repository runs the workflow and its status check appears on pull requests | Appears | Does not run |
| 3 | A failing check shows the tool, file and message in the log | Verified with a seeded failure | Cause not visible |
| 4 | Inputs and defaults are documented | Documented | Missing |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-002 | Uses the onboarding guide and runner list |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O4 | [BC-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-11-14 — confirmed on 2026-10-10 by S01, standing in for S05 (ADR-0002); the Business Case sets no deadline.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Verify reusable workflow support | Check whether this Gitea version supports `workflow_call` and cross-repository `uses`; if not, choose a copied template instead. Verified on 2026-10-10: supported, so no copied template is needed (see Verification results). | No | Verification results |
| 2 | Define the quality-check contract | Decide the inputs (language, tool versions, working directory) and what a pass and a fail mean. Start with Python and shell. This is something an engineer does, so it needs a use case first. | Yes | Use case candidate: run project quality checks |
| 3 | Implement the reusable quality workflow | Create the workflow in the canonical location with pinned tool versions and least-privilege permissions. | No | |
| 4 | Adopt it in one other repository | Onboard a real project and fix the gaps in the guide that appear. Adopted in `TirSystem-BashScript/RepoFoundry` (its PR 76, run passes); see Adoption in a real repository. | No | Adoption in a real repository |
| 5 | Write the guide for reading results | Explain status checks, logs and typical fixes so an engineer can make a failing check pass. | No | |

## Verification results

Task 1 was run on 2026-10-10 on the instance (Gitea 1.27.3) with a throwaway
branch, `verify-reusable-workflows`, in `TirSystem/github-action`. The called
workflow declared `on: workflow_call` with one input and printed it; the
callers used `jobs.<job_id>.uses`. All branches were deleted afterwards.

| Call | Caller | Result |
| --- | --- | --- |
| `uses: ./.gitea/workflows/reuse-callee.yml` | `TirSystem/github-action` (same repository) | Called job ran; input received |
| `uses: TirSystem/github-action/.gitea/workflows/reuse-callee.yml@<branch>` | `TirSystem/github-action` | Called job ran; input received |
| the same, from another repository of the organization | `TirSystem/sqa-qc-checklists` | Called job ran; `gitea.repository` was the caller |
| the same, from a repository of another organization | `TirSystem-BashScript/RepoFoundry` | Called job ran; `gitea.repository` was the caller |

What the test did not cover: a provider repository that is private (the
provider here is public), passing secrets to a called workflow
(`secrets:` or `secrets: inherit`), and a reference by tag instead of a
branch. The quality checks of this milestone need none of the secrets; a
private provider and tag references are for the release milestone (MIL-004).

## Adoption in a real repository (task 4)

On 2026-10-10 the workflow was run against `TirSystem-BashScript/RepoFoundry`
(another organization; 39 shell files, no Python), first on a throwaway
branch and then as a pull request, RepoFoundry PR 76.

| Run | `shellcheck` | `shfmt -d` | Python |
| --- | --- | --- | --- |
| Unchanged repository | PASS on all 39 files | FAIL on 10 files | skipped with a notice (no files) |
| With `switch_case_indent = true` under `[*.sh]` in `.editorconfig` | PASS | PASS | skipped |
| The pull request itself (`languages: shell`) | PASS | PASS | not selected |

What the run showed:

- **`shellcheck` needs no help** when the project has a `.shellcheckrc`: the
  workflow runs from the repository root, so the project's own settings
  (`external-sources`, `source-path=SCRIPTDIR`) applied and files that share
  variables across `src/lib/*.sh` produced no false positives.
- **`shfmt` follows the project's style only through `.editorconfig`.** All ten
  differences were the indentation of `case` patterns: the workflow uses shfmt
  defaults, the project's own check is `shfmt -i 2 -ci`. One `.editorconfig`
  line fixed it without changing a script. A shell project with its own shfmt
  flags should expect a first formatting failure and express the flags there.
- **Paths in the log are relative to `working-directory`**, and a caller must
  reference the workflow at `main` or a tag, not at a branch that is deleted
  when its pull request merges (the first trial lost its reference that way).

The task closes when RepoFoundry PR 76 is merged. The gaps above are for the
guide of task 5 (issue #19).

---

[BC-001]: ../business-case.md
[ADR-0002]: ../adr/adr-0002-s01-approves-as-stand-in.md
[b3f006f]: https://git.tirsystem.com/TirSystem/github-action/commit/b3f006f7a482392189a46c324ad4f28c4c3a2d2a
