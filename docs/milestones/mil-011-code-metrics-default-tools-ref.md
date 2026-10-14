# MIL-011: Fix the defaults of the code metrics workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-011 |
| CrossReference | [BC-001], [US-001], [MIL-010], [ADR-0010], [ADR-0006] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | Accepted | Jens Tirsvad Nielsen | S01 | Added the results of task 1 (reproduction and the defaults of the five workflows); reviewed (RC-077), accepted by the AI as stand-in for S01 in autonomous mode | [e11c43f] |
| 2026-10-14 | Proposed | Jens Tirsvad Nielsen | S01 | Added the results of tasks 2 to 5 (the fix, the test, the guides, the run on the instance); reviewed in RC-078, the release follows | [a6892c3] |

---

## Purpose

Decide whether the released code metrics workflow can be called with its documented defaults, and correct it if it cannot.

Release 2.1.0 ([MIL-010]) added `code-metrics.yml`. Its guide, its header comment and the default of its `tools-ref` input name `v1`, but the workflow and its scripts (`tools/code-metrics.sh`, `tools/count_loc.py`, `tools/badges.py`) exist only from `v2.1.0`. A caller who follows the guide (`@v1`) cannot resolve the workflow, and a caller at `@v2` that leaves `tools-ref` at its default fetches the scripts from `v1`, where they are absent, so the run fails. The offline tests of [MIL-010] did not see it, because they run the scripts from the checkout and never resolve a ref. The framework wiki page `Badges` works around it by telling callers to set `tools-ref: v2`.

The other four reusable workflows also default `tools-ref` to `v1`; their scripts exist at `v1`, but a default that follows an old major is the same kind of error, so this milestone checks them too.

## Deliverable

A patch release (`2.1.1`, [ADR-0006]) in which: the default `tools-ref` of every reusable workflow names a tag that holds the scripts it runs; the guide, the header comment of `code-metrics.yml`, the upgrading guide, the README and the wiki pages in English, Danish and Bahasa Malaysia call the workflow at `@v2`; a test fails when a default `tools-ref` names a tag without the script; and the changelog has a `Fixed` entry. In `TirSystem/sqa-qc-framework`: the `Badges` wiki page without the `tools-ref` workaround.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The defect is reproduced before the fix: a call at the major tag with the defaults fails, and the failure names the missing script, recorded in this milestone | Reproduced and recorded | Not reproduced, or not recorded |
| 2 | Every reusable workflow's default `tools-ref` names a tag that contains the script file the workflow runs, listed per workflow in this milestone | All five checked and listed | A default names a tag without its script |
| 3 | The default is derived, not copied: one place gives the current major, and a test fails when a workflow default differs from it or names a tag without the script | Test fails on a seeded wrong default and passes on the fix | No such test |
| 4 | No guide, comment, README or wiki page tells a caller to use `@v1` for `code-metrics.yml`; a search of `guides/`, `README.md`, `docs/wiki/` and `.gitea/workflows/` finds none | Count is 0 | A page still says `@v1` for it |
| 5 | A call with the documented defaults runs on the instance and commits the badges to a `badges` branch, verified on a throwaway branch and recorded | Run succeeds | Fails or is not run |
| 6 | The release is a patch (`2.1.1`): the changelog has a `Fixed` entry, the major tag `v2` moves to it, and `v1` is not touched | Released | Released as another level, or `v1` moved |
| 7 | The framework `Badges` page no longer tells a caller to set `tools-ref`, in all three languages, and still calls the workflow at `@v2` | Page merged | The workaround remains |
| 8 | Reviewed | A review record (`RC-*`) for this milestone and the changed workflow, tests and guides, each with a verdict of Go | An instance without a record |

## Dependencies

| Depends on | Reason |
| --- | --- |
| [MIL-010] | The workflow and its guide are its deliverables; the defect is in release 2.1.0 |
| [ADR-0006] | The release process: a fix is a patch release, and a moving major tag follows it |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| Business Case objective O5: a shared workflow that counts the code files and lines of code, reads the coverage report and publishes the three results as SVG badges; the workflow cannot be called as documented until this milestone is done | [BC-001] |
| User stories | [US-001] (no new story: the tasks below are technical, and the story of [MIL-010] for the badges stays as written) |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-10-23 (Friday), one week of work: the fix is small and a caller cannot use the workflow until it is released. This precedes the planned decision date of [MIL-010] (2027-01-30) because that milestone was released on 2026-10-14, ahead of its date; the schedule row of [MIL-010] is not changed here. The Business Case sets no deadline.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Reproduce the defect and list the defaults | On a throwaway branch, call `code-metrics.yml` at `@v2` with the defaults and at `@v1`, and record both failures and the message. List, for each of the five reusable workflows, the default `tools-ref` and whether the script it runs exists at that tag. Record the result in this milestone. | No | [MIL-010] |
| 2 | Fix the defaults | Give the repository one definition of the current major (a file the workflows' tests and the release workflow read), set the default `tools-ref` of every reusable workflow from it, and change the header comment of `code-metrics.yml` to `@v2`. A workflow whose script is at the previous major keeps that tag only with a comment that says why. | No | [ADR-0006] |
| 3 | Add the test | An offline test that reads every workflow in `.gitea/workflows/`, takes the default `tools-ref` and the script it runs, and fails when the default differs from the current major or the script is not in that tag (checked with `git cat-file` against the tags of the checkout). Show it fails on a seeded wrong default and passes on the fix. | No | [MIL-010] |
| 4 | Correct the guides, README and wiki | Change `@v1` to `@v2` for `code-metrics.yml` in `guides/code-metrics.md`, `guides/upgrading.md`, `README.md` and `docs/wiki/CodeMetrics.md`, `.da.md` and `.ms.md`; say in the guide that `tools-ref` defaults to the current major. Search the repository for the remaining `@v1`. | No | |
| 5 | Verify on the instance | On a throwaway branch of a repository, call the fixed workflow at the branch with the defaults, and check that the `badges` branch gets the SVG files. Record the run. | No | [MIL-010] |
| 6 | Release 2.1.1 | Add the `Fixed` entry to the changelog (ADR-0006: a patch), run the Release workflow, and check that `v2` points at `v2.1.1` and `v1` at `v1.2.2`. | No | [ADR-0006] |
| 7 | Remove the workaround from the framework page | In `TirSystem/sqa-qc-framework`, remove the `tools-ref: v2` line and the two bullets about it from `docs/wiki/Badges.md`, `Badges-da.md` and `Badges-ms.md`, and add a changelog line. This is a change in another repository, made after release 2.1.1 and in its own pull request. | No | |
| 8 | Add MIL-011 to the Project Plan | Add the schedule row, the Gantt bar, the scope entry and the dependency to [PP-001], and its review to the traceability matrix. | No | |
| 9 | Review | Record `RC-*` for this milestone, the workflow and tests, and the guides, each with a verdict. | No | |

## Verification results

Task 1 was run on 2026-10-14 with the throwaway branch `verify-code-metrics-defaults` of `TirSystem/github-action`. It calls `code-metrics.yml` at the two refs a caller could use, with every input at its default.

| Call | Result | Evidence |
| --- | --- | --- |
| `...code-metrics.yml@v2`, defaults | Fails in the step "Validate the inputs": `bash: shared-scripts/tools/code-metrics.sh: No such file or directory`, exit code 127. The input `tools-ref` is `v1`, so the scripts are fetched from `v1`. | run 1499, job 1638 |
| `...code-metrics.yml@v1`, defaults | No run is created at all, and no error is shown: two pushes of a workflow that calls it (once with the `@v2` job beside it, once alone) made no run in over a minute, while the push of the `@v2` call alone made one | commits `5654905` and `46e752d` (no run), `9a17868` (run 1499) |

The defaults of the five reusable workflows at `v2.1.0` (`v1` is `1.2.2`, `v2` is `2.1.0`):

| Workflow | Default `tools-ref` | Script it runs | At the default | At `v2` |
| --- | --- | --- | --- | --- |
| `code-metrics.yml` | `v1` | `tools/code-metrics.sh` | **absent** | present |
| `quality-checks.yml` | `v1` | `tools/quality-checks.sh` | present | present |
| `quality-checks-cpp.yml` | `v1` | `tools/quality-checks-cpp.sh` | present | present |
| `quality-checks-csharp.yml` | `v1` | `tools/quality-checks-csharp.sh` | present | present |
| `publish-wiki-pages.yml` | `v1` | `tools/publish_wiki.py` | present | present |

Only `code-metrics.yml` is broken. The other four resolve, but a caller at `@v2` runs their scripts from `1.2.2` and not from `2.1.0`; `tools/publish_wiki.py` changed in `2.0.0` (it requires `WIKI_PRUNE` and no longer reads a marker). Whether that is a defect is decided in task 2.


Tasks 2 to 5 were done on 2026-10-14 on the branch `mil-011-fix`:

- **Fix (task 2):** the file `MAJOR_TAG` holds the current major (`v2`); the default `tools-ref` of the five reusable workflows is `v2`, and the header comment of `code-metrics.yml` calls it at `@v2`. The four workflows other than `code-metrics.yml` followed the older major only by default and changed no behaviour for a caller at `@v1`; for a caller at `@v2` the scripts now come from the same major as the workflow.
- **Test (task 3):** `tests/test_tools_ref.py` ties `MAJOR_TAG` to the highest major of the changelog and checks every reusable workflow's default and script. With `default: "v1"` seeded in `code-metrics.yml` three tests failed; restored, they pass. The suite passes (540 tests).
- **Guides (task 4):** `guides/code-metrics.md`, `guides/upgrading.md`, the three quality-check guides, `README.md` and the wiki pages in English, Danish and Bahasa Malaysia; the amendments of ADR-0005, ADR-0008, ADR-0009 and ADR-0010. A search for `code-metrics.yml@v1` finds none.
- **Instance (task 5):** the workflow at `@mil-011-fix` with every input at its default except `badges-branch` ran as run 1509 (job 1649): `tools-ref` resolved to `v2`, the scripts were fetched, and the badges were committed to `badges-verify` (commit `041d991`).

---

[BC-001]: ../business-case.md
[US-001]: ../user-stories.md
[MIL-010]: ./mil-010-code-metrics-badges.md
[ADR-0010]: ../adr/adr-0010-code-metrics-badges-contract.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
[PP-001]: ../project-plan.md
[e11c43f]: https://git.tirsystem.com/TirSystem/github-action/commit/e11c43f0a41e7dd9647f7804947d6e464407a597
[a6892c3]: https://git.tirsystem.com/TirSystem/github-action/commit/a6892c372aca9f2e12826a4c3b260290a0656ecb
