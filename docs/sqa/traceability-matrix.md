# Traceability Matrix

## Metadata
| Key | Value |
| --- | --- |
| ID | TM-001 |
| CrossReference | [BC-001], [SA-001], [PP-001], [MIL-001], [MIL-002], [MIL-003], [MIL-004], [RC-001], [RC-002], [RC-003], [RC-004], [RC-005], [RC-006], [RC-007] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Deprecated | Jens Tirsvad Nielsen | S05 | Initial version | [aa3f088] |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S05 | S05 review approved (reported by S01)<br>Review records RC-001 to RC-007 are Accepted | pending |

---

## Purpose

Tracks backward/forward links between artifact instances so that the Business Case's
cross-artifact traceability success criterion is measurable. A row is added or
updated whenever an artifact instance is created or reviewed.

## Traceability Table

| Artifact Instance | Type | Upstream (Backward Link) | Downstream (Forward Link) | Last Reviewed (RC-ID) |
| --- | --- | --- | --- | --- |
| [SA-001] | SA | - | [BC-001] | [RC-004] |
| [BC-001] | BC | [SA-001] | [PP-001], [MIL-001], [MIL-002], [MIL-003], [MIL-004] | [RC-001] |
| [PP-001] | PP | [BC-001], [SA-001] | [MIL-001], [MIL-002], [MIL-003], [MIL-004] | [RC-002] |
| [MIL-001] | MIL | [BC-001], [PP-001] | [MIL-002] | [RC-003] |
| [MIL-002] | MIL | [BC-001], [PP-001], [MIL-001] | [MIL-003] | [RC-005] |
| [MIL-003] | MIL | [BC-001], [PP-001], [MIL-002] | [MIL-004] | [RC-006] |
| [MIL-004] | MIL | [BC-001], [PP-001], [MIL-003] | - | [RC-007] |
| [RC-001] | RC | [BC-001] | - | - |
| [RC-002] | RC | [PP-001] | - | - |
| [RC-003] | RC | [MIL-001] | - | - |
| [RC-004] | RC | [SA-001] | - | - |
| [RC-005] | RC | [MIL-002] | - | - |
| [RC-006] | RC | [MIL-003] | - | - |
| [RC-007] | RC | [MIL-004] | - | - |

## Coverage Notes

- `-` in Upstream means foundational (SA-001 has no prerequisite). In Downstream it means nothing is built on the instance yet. In Last Reviewed it means no `RC-*` exists (review records are not themselves reviewed).
- Types with no instance yet: KPI, BMC, BPMN, UCD, US, UC, SSD, DM, OC, SD, DCD, ERD, ADR, GOV, DICT. The Project Plan lists use case candidates, but the formal use cases wait for a use case diagram and user stories.
- PP-001 and TM-001 have no QC checklist; RC-002 validated PP-001 against its Business Case constraints and the milestone Go / No-Go criteria. TM-001 has no review record.
- All review records are `Accepted` after the S05 review (reported by S01 on 2026-10-10); the author and S01 are the same person, so S05 is the independent reviewer.

---

[BC-001]: ../business-case.md
[SA-001]: ../stakeholder-analysis.md
[PP-001]: ../project-plan.md
[MIL-001]: ../milestones/mil-001-stabilise-metadata-sync.md
[MIL-002]: ../milestones/mil-002-onboarding-and-operations.md
[MIL-003]: ../milestones/mil-003-quality-checks.md
[MIL-004]: ../milestones/mil-004-versioned-release.md
[RC-001]: ./reviews/rc-001-business-case.md
[RC-002]: ./reviews/rc-002-project-plan.md
[RC-003]: ./reviews/rc-003-mil-001.md
[RC-004]: ./reviews/rc-004-stakeholder-analysis.md
[RC-005]: ./reviews/rc-005-mil-002.md
[RC-006]: ./reviews/rc-006-mil-003.md
[RC-007]: ./reviews/rc-007-mil-004.md
[aa3f088]: https://git.tirsystem.com/TirSystem/github-action/commit/aa3f08876d55fa5f008e93f65176a496601c00ca
