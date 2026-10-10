# Review Record: MIL-004 (scripts as files)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-034 |
| CrossReference | [MIL-004], [QC-MIL-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | [616c5d2] |

---

## Artifact Under Review

- Instance reviewed: [MIL-004]
- Checklist used: [QC-MIL-001]

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | The deliverable now also names scripts as files fetched at a pinnable reference. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | New criterion 5 is checkable: the count of embedded scripts is 0 and a run in another organization passes. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged (MIL-003); task 6 needs no other milestone, because the checkout of a script repository was verified on 2026-10-10. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | Finding fixed during this review: task 6 serves O2 (one canonical copy and a defined way to reach consuming repositories) and the Traceability table listed only O4. It now lists O2 and O4. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Unchanged: owner S05, approving reviewer S01. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | 2026-11-28, confirmed (RC-029). |

## Overall Verdict

Go - all six criteria pass; the one finding (criterion 4) was fixed during the review. S01 gave the Go in chat on 2026-10-10, standing in for the other reviewers as ADR-0002 records; there is no independent reader. Accepting the amendment unlocks task 6 under the plan-first gate; the issue is still to be created with `sync-project.sh --apply`.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Decide whether consumers pin a tag or follow `main` for the shared scripts (task 1 of this milestone) | S01 | 2026-11-16 |

---

[MIL-004]: ../../milestones/mil-004-versioned-release.md
[QC-MIL-001]: ../../../framework/qc/qc-milestones-gateways.md
[616c5d2]: https://git.tirsystem.com/TirSystem/github-action/commit/616c5d2e48f0d76399a6f78923891fc7f50c8e22
