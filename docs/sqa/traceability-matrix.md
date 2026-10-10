# Traceability Matrix

## Metadata
| Key | Value |
| --- | --- |
| ID | TM-001 |
| CrossReference | [BC-001], [SA-001], [PP-001], [MIL-001], [MIL-002], [MIL-003], [MIL-004], [MIL-005], [MIL-006], [RC-001], [RC-002], [RC-003], [RC-004], [RC-005], [RC-006], [RC-007], [RC-008], [RC-009], [RC-010], [RC-011], [RC-012], [RC-013], [RC-014], [RC-015], [RC-016], [RC-017], [ADR-0001], [ADR-0002], [ADR-0003] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Deprecated | Jens Tirsvad Nielsen | S01 | Added MIL-006 and RC-016 | pending |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Added RC-017 for PP-001 | pending |

---

## Purpose

Tracks backward/forward links between artifact instances so that the Business Case's
cross-artifact traceability success criterion is measurable. A row is added or
updated whenever an artifact instance is created or reviewed.

## Traceability Table

| Artifact Instance | Type | Upstream (Backward Link) | Downstream (Forward Link) | Last Reviewed (RC-ID) |
| --- | --- | --- | --- | --- |
| [SA-001] | SA | - | [BC-001] | [RC-004] |
| [BC-001] | BC | [SA-001] | [PP-001], [MIL-001], [MIL-002], [MIL-003], [MIL-004], [MIL-005], [MIL-006] | [RC-001], [RC-008] |
| [PP-001] | PP | [BC-001], [SA-001] | [MIL-001], [MIL-002], [MIL-003], [MIL-004], [MIL-005], [MIL-006] | [RC-002], [RC-009], [RC-015], [RC-017] |
| [MIL-001] | MIL | [BC-001], [PP-001] | [MIL-002] | [RC-003] |
| [MIL-002] | MIL | [BC-001], [PP-001], [MIL-001] | [MIL-003], [MIL-005] | [RC-005] |
| [MIL-003] | MIL | [BC-001], [PP-001], [MIL-002] | [MIL-004] | [RC-006] |
| [MIL-004] | MIL | [BC-001], [PP-001], [MIL-003] | - | [RC-007] |
| [RC-001] | RC | [BC-001] | - | - |
| [RC-002] | RC | [PP-001] | - | - |
| [RC-003] | RC | [MIL-001] | - | - |
| [RC-004] | RC | [SA-001] | - | - |
| [RC-005] | RC | [MIL-002] | - | - |
| [RC-006] | RC | [MIL-003] | - | - |
| [MIL-005] | MIL | [BC-001], [PP-001], [MIL-002] | [MIL-006] | [RC-010], [RC-011] |
| [MIL-006] | MIL | [BC-001], [PP-001], [MIL-002], [MIL-005] | - | [RC-016] |
| [RC-007] | RC | [MIL-004] | - | - |
| [RC-008] | RC | [BC-001] | - | - |
| [RC-009] | RC | [PP-001] | - | - |
| [RC-010] | RC | [MIL-005] | - | - |
| [ADR-0001] | ADR | [BC-001], [MIL-005] | [ADR-0003] | [RC-012] |
| [ADR-0002] | ADR | [SA-001], [RC-001] | - | [RC-013] |
| [ADR-0003] | ADR | [MIL-005], [ADR-0001], [RC-011] | - | [RC-014] |
| [RC-011] | RC | [MIL-005] | - | - |
| [RC-012] | RC | [ADR-0001] | - | - |
| [RC-013] | RC | [ADR-0002] | - | - |
| [RC-014] | RC | [ADR-0003] | - | - |
| [RC-015] | RC | [PP-001] | - | - |
| [RC-016] | RC | [MIL-006] | - | - |
| [RC-017] | RC | [PP-001] | - | - |

## Coverage Notes

- `-` in Upstream means foundational (SA-001 has no prerequisite). In Downstream it means nothing is built on the instance yet. In Last Reviewed it means no `RC-*` exists (review records are not themselves reviewed).
- Types with no instance yet: KPI, BMC, BPMN, UCD, US, UC, SSD, DM, OC, SD, DCD, ERD, GOV, DICT. The Project Plan lists use case candidates, but the formal use cases wait for a use case diagram and user stories.
- PP-001 and TM-001 have no QC checklist; RC-002 validated PP-001 against its Business Case constraints and the milestone Go / No-Go criteria. TM-001 has no review record.
- All review records are `Accepted` after S01 stood in for S05 on 2026-10-10. The author and S01 are the same person, so an independent review by S05 is still open (see RC-001).

---

[BC-001]: ../business-case.md
[SA-001]: ../stakeholder-analysis.md
[PP-001]: ../project-plan.md
[MIL-001]: ../milestones/mil-001-stabilise-metadata-sync.md
[MIL-002]: ../milestones/mil-002-onboarding-and-operations.md
[MIL-003]: ../milestones/mil-003-quality-checks.md
[MIL-004]: ../milestones/mil-004-versioned-release.md
[MIL-005]: ../milestones/mil-005-wiki-and-translations.md
[MIL-006]: ../milestones/mil-006-shared-wiki-publishing.md
[RC-001]: ./reviews/rc-001-business-case.md
[RC-002]: ./reviews/rc-002-project-plan.md
[RC-003]: ./reviews/rc-003-mil-001.md
[RC-004]: ./reviews/rc-004-stakeholder-analysis.md
[RC-005]: ./reviews/rc-005-mil-002.md
[RC-006]: ./reviews/rc-006-mil-003.md
[RC-007]: ./reviews/rc-007-mil-004.md
[RC-008]: ./reviews/rc-008-business-case-wiki-scope.md
[RC-009]: ./reviews/rc-009-project-plan-mil-005.md
[RC-010]: ./reviews/rc-010-mil-005.md
[RC-011]: ./reviews/rc-011-mil-005-wiki-publishing.md
[RC-012]: ./reviews/rc-012-adr-0001.md
[ADR-0001]: ../adr/adr-0001-wiki-structure-and-languages.md
[ADR-0002]: ../adr/adr-0002-s01-approves-as-stand-in.md
[ADR-0003]: ../adr/adr-0003-wiki-publish-token.md
[RC-013]: ./reviews/rc-013-adr-0002.md
[RC-014]: ./reviews/rc-014-adr-0003.md
[RC-015]: ./reviews/rc-015-project-plan-pat.md
[RC-016]: ./reviews/rc-016-mil-006.md
[RC-017]: ./reviews/rc-017-project-plan-mil-006.md
