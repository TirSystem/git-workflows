# MIL-020: Release when the changelog changes

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-020 |
| CrossReference | [BC-001], [MIL-018], [US-001], [ADR-0017], [RC-105] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-06 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; reviewed (RC-105), accepted by the author in chat on 2026-11-06 as stand-in for S01, not independent | pending |

---

## Purpose

Decide that a release is no longer started by hand. When `CHANGELOG.md` changes
on the default branch of a repository, the scoped `release.yml` reads the newest
numbered entry, and if that version has no tag yet it creates the tag, the
release page and, from 1.0.0, moves the major tag. Today MIL-018 requires a
person to open the Actions page, fill in a version and run the workflow twice
(a dry run, then the real run); the release of `git-workflows` 3.1.0 and of the
framework 0.19.1 both needed that. The changelog pull request check already
keeps the file releasable, so the changelog is the one place that says a version
exists. This amends ADR-0017, which chose "started by hand" and a dry run.

## Deliverable

`.gitea/scoped_workflows/release.yml` with the triggers `pull_request` (the
changelog check, as now) and `push` to the default branch with `paths:
CHANGELOG.md`, and no inputs; `tools/release.py` that reads the version from the
changelog, waits for the green `Validate / validate (push)` of the same commit
(it runs at the same time on a push), and ends green without writing when the
tag of the newest entry already exists; an amendment of ADR-0017 (or a new ADR
that supersedes the part about starting by hand and the dry run); the guides, the
adoption rules, the README, the wiki pages in three languages and the changelog;
the user stories US-001.21 to US-001.23; offline tests; and the first release
made by merging a changelog, with nothing run by hand.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | A push to the default branch that changes `CHANGELOG.md` releases the newest numbered entry when its tag does not exist | A merged changelog in a test repository shows the tag, the release page and, from 1.0.0, the major tag, with no run started by hand | A person has to start the run |
| 2 | A push that changes the changelog without a new numbered entry (an edit under `Unreleased`, a typo) releases nothing and the run is green | A test and a run show a green run, no new tag, no new page | The run fails or a tag is made |
| 3 | The release waits for `Validate / validate (push)` of the same commit and refuses when it ends red or does not appear within the limit | One test per outcome (green, red, timeout) passes with the message of the category | The release runs on an unchecked commit, or fails on the race |
| 4 | An exact tag is never moved and the version of the newest entry already tagged is a green no-op | A re-run of a merged release changes nothing | A tag or a page is overwritten |
| 5 | The secret `TOKEN_FOR_GITEA_RELEASE` is required with no fallback, no token or secret value reaches a log or an argument, and the workflow has `permissions: contents: read` | The file and the log are read and show it | A fallback is used or a value is printed |
| 6 | The manual start without a form still works, so a failed release can be run again | A manual run releases the newest entry or is a green no-op | There is no way to retry |
| 7 | The documents say so: ADR-0017 is amended, and the guides, the adoption rules, the README and the wiki pages in three languages describe the new start and no longer the dry run | A search for `dry_run` and `started by hand` finds only history | A document still sends the reader to the old form |
| 8 | The offline tests pass, `python tools/build_wiki.py --check` is clean and `validate.yml` is green | All succeed | A test fails or a page is stale |
| 9 | The first release is made by merging a changelog, in this repository and in `sqa-qc-framework`, and the page is read back through the API | Both releases exist with no run started by hand | A release is made by hand |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-018 | The scoped release workflow and `release.py` that this milestone changes |
| MIL-017 | The status `Validate / validate (push)` that the release waits for |
| ADR-0017 | The decision to start by hand that this milestone amends |
| Business Case objective O4 | Shared quality-check and release workflows; S01 asked for the release to follow the changelog |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O4 (shared quality-check and release workflows, versioned) | [BC-001] |
| A release is made when the changelog changes | [US-001] (US-001.21) |
| The release waits for the validation of the same commit | [US-001] (US-001.22) |
| A version that is already released is not released again | [US-001] (US-001.23) |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-11-13 — proposed by the author; the Business Case sets no deadline. It is
urgent work that moves ahead of MIL-007 and later phases because every release
until it is done needs two manual runs; S01 confirms or moves the date.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Write the user stories | US-001.21 to US-001.23 in `docs/user-stories.md`, with their review record. | No | [US-001] |
| 2 | Amend the decision (ADR) | Amend ADR-0017: the release starts on a push that changes the changelog, with no inputs; the dry run is replaced by the pull request check; the wait for the validation of the same commit; a version already tagged is a no-op. | No | [ADR-0017] |
| 3 | Wait for the validation and make "tag exists" a no-op | `tools/release.py`: poll `Validate / validate (push)` of the commit up to a limit (a setting, default 10 minutes); in push mode an existing tag of the newest entry ends green without writing; tests for green, red, timeout and the no-op. The uncommitted edit that reads the version from the changelog is part of this task. | No | |
| 4 | Add the push trigger | `release.yml`: `push` to the default branch with `paths: CHANGELOG.md`, no inputs, the concurrency group kept, the manual start kept as a retry. | No | |
| 5 | Describe the new start | `guides/release-process.md`, `guides/adoption-rules.md`, the README, the wiki pages in three languages and the changelog entry under Changed. | No | |
| 6 | Release by merging | Merge the changelog of this milestone and read the tag, the page and the major tag back; then do the same in `sqa-qc-framework` (its next release). | No | |

---

[BC-001]: ../business-case.md
[US-001]: ../user-stories.md
[MIL-018]: ./mil-018-scoped-release-workflow.md
[ADR-0017]: ../adr/adr-0017-scoped-release-workflow.md
[RC-105]: ../sqa/reviews/rc-105-mil-020-pp-001.md
