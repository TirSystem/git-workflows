# Review Record: ADR-0017 amendment (RC-107)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-107 |
| CrossReference | [ADR-0017], [MIL-020], [QC-ADR-001], [RC-101] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-06 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted by the author in chat on 2026-11-06 as stand-in for S01 | pending |

---

## Artifact Under Review

- Instance reviewed: [ADR-0017]
- Checklist used: [QC-ADR-001]
- Scope: delta review of the amendment "the release starts when the changelog changes" (MIL-020 task 2) and of the lines of the Decision and the Consequences it changes; the earlier record is [RC-101]
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, asked in chat on 2026-11-06 to build MIL-020 and stands in for S01; the AI prepared the evidence)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | The ID matches the filename number and is unique and sequential | Pass | Unchanged: `ADR-0017`. |
| 2 | Context states the problem, the forces and the options evaluated | Pass | The amendment names the problem (two manual runs per release, failures on the form and on a status name) and the force (the changelog already says which version exists and is reviewed in its pull request). |
| 3 | At least two options were considered | Pass | Three: keep starting by hand, start on a changelog push, start on a schedule. |
| 4 | Decision is stated in one or two unhedged sentences and matches an evaluated option | Pass | "Decision: option 2", followed by the triggers and six rules. |
| 5 | Consequences list both Positive and Negative outcomes | Pass | One positive line and one negative line added: a merged changelog releases without a person starting it, and its safeguards. |
| 6 | Quality-attribute impacts are named where the decision affects them | Pass | Reliability (the wait, red stops at once, a skipped older push, a green no-op for a released version) and security (an unchanged secret, scope and permissions; the negative consequence names the safeguards). |
| 7 | Affected Artifacts are listed as links, and each is also in CrossReference | Pass | [MIL-020] is added to both; [RC-107] is in CrossReference and the links. |
| 8 | Status changes are recorded as new Version History rows | Pass | A new row; the earlier row becomes `Deprecated`; the two latest rows are kept. |
| 9 | A superseded or deprecated ADR names its successor, and the successor links back | Not applicable | The amendment replaces parts of one ADR, not another ADR; the open point of [RC-101] about [ADR-0006] and [ADR-0007] is unchanged. |
| 10 | Written in the language of the domain, with no unexplained abbreviations | Pass | |
| 11 | Status is one of the allowed values | Pass | `Accepted`. |

Facts the amendment rests on, each read on 2026-11-06:

| Claim | Evidence |
| --- | --- |
| The triggers are `pull_request`, `push` with `paths: CHANGELOG.md`, and `workflow_dispatch` with no inputs | `.gitea/scoped_workflows/release.yml` and the test of the triggers |
| The version is the newest numbered entry, and an existing tag is a green no-op | `main` of `tools/release.py` and the test `test_newest_entry_that_is_already_tagged_is_a_green_no_op` |
| The wait is 600 seconds by default, a red status stops at once, pending or missing stops after the wait | `wait_for_validation` and five tests (pending then green, not reported yet, stays pending, never appears, red) |
| A push that is no longer the tip is skipped, a start by hand is refused | `test_a_push_that_is_no_longer_the_tip_is_skipped_without_error` and `test_a_run_by_hand_from_a_commit_that_is_not_the_tip_is_refused` |
| Only the default branch releases on a push | the `if:` of the release step and its test |
| Whether the step condition `gitea.event.repository.default_branch` is filled on the instance | Not verified here; MIL-020 task 6 (the first release made by merging a changelog) verifies it |

## Overall Verdict

Go. All applicable criteria pass; criterion 9 does not apply. One claim is not yet verified on the instance (the default branch in the event), and task 6 of [MIL-020] verifies it. The AI records the decision as stand-in for S01 on the author's request in chat; there is no independent reader and the decision stays open to challenge.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Verify on the instance that `gitea.event.repository.default_branch` is set on a push, and fix the condition if not (MIL-020 task 6) | S05 | 2026-11-13 |

---

[ADR-0017]: ../../adr/adr-0017-scoped-release-workflow.md
[MIL-020]: ../../milestones/mil-020-release-on-changelog-change.md
[RC-101]: ./rc-101-adr-0017.md
[QC-ADR-001]: ../../../framework/qc/artifacts/qc-adr.md
