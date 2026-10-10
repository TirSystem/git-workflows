# Traceability Matrix

## Metadata
| Key | Value |
| --- | --- |
| ID | TM-001 |
| CrossReference | [BC-001], [SA-001], [PP-001], [MIL-001], [MIL-002], [MIL-003], [MIL-004], [MIL-005], [MIL-006], [RC-001], [RC-002], [RC-003], [RC-004], [RC-005], [RC-006], [RC-007], [RC-008], [RC-009], [RC-010], [RC-011], [RC-012], [RC-013], [RC-014], [RC-015], [RC-016], [RC-017], [RC-018], [RC-019], [RC-020], [RC-021], [RC-022], [RC-023], [RC-024], [RC-025], [RC-026], [RC-027], [RC-028], [RC-029], [RC-030], [RC-031], [RC-032], [RC-033], [RC-034], [RC-035], [RC-036], [RC-037], [RC-038], [RC-039], [UC-005], [ADR-0005], [UCD-001], [US-001], [UC-001], [UC-002], [UC-003], [UC-004], [ADR-0001], [ADR-0002], [ADR-0003], [ADR-0004] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Deprecated | Jens Tirsvad Nielsen | S01 | Added UC-005, ADR-0005 and RC-035 to RC-038 | [385d2fb] |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Added RC-039 for MIL-003 | [3b8681d] |

---

## Purpose

Tracks backward/forward links between artifact instances so that the Business Case's
cross-artifact traceability success criterion is measurable. A row is added or
updated whenever an artifact instance is created or reviewed.

## Traceability Table

| Artifact Instance | Type | Upstream (Backward Link) | Downstream (Forward Link) | Last Reviewed (RC-ID) |
| --- | --- | --- | --- | --- |
| [SA-001] | SA | - | [BC-001], [UCD-001] | [RC-004] |
| [BC-001] | BC | [SA-001] | [PP-001], [MIL-001], [MIL-002], [MIL-003], [MIL-004], [MIL-005], [MIL-006] | [RC-001], [RC-008] |
| [PP-001] | PP | [BC-001], [SA-001] | [MIL-001], [MIL-002], [MIL-003], [MIL-004], [MIL-005], [MIL-006], [US-001] | [RC-002], [RC-009], [RC-015], [RC-017], [RC-025], [RC-032] |
| [MIL-001] | MIL | [BC-001], [PP-001] | [MIL-002] | [RC-003], [RC-026] |
| [MIL-002] | MIL | [BC-001], [PP-001], [MIL-001] | [MIL-003], [MIL-005] | [RC-005], [RC-027] |
| [MIL-003] | MIL | [BC-001], [PP-001], [MIL-002] | [MIL-004] | [RC-006], [RC-028], [RC-033], [RC-039] |
| [MIL-004] | MIL | [BC-001], [PP-001], [MIL-003] | - | [RC-007], [RC-029], [RC-034] |
| [RC-001] | RC | [BC-001] | - | - |
| [RC-002] | RC | [PP-001] | - | - |
| [RC-003] | RC | [MIL-001] | - | - |
| [RC-004] | RC | [SA-001] | - | - |
| [RC-005] | RC | [MIL-002] | - | - |
| [RC-006] | RC | [MIL-003] | - | - |
| [MIL-005] | MIL | [BC-001], [PP-001], [MIL-002] | [MIL-006] | [RC-010], [RC-011], [RC-030] |
| [MIL-006] | MIL | [BC-001], [PP-001], [MIL-002], [MIL-005] | - | [RC-016], [RC-031] |
| [RC-007] | RC | [MIL-004] | - | - |
| [RC-008] | RC | [BC-001] | - | - |
| [RC-009] | RC | [PP-001] | - | - |
| [RC-010] | RC | [MIL-005] | - | - |
| [ADR-0001] | ADR | [BC-001], [MIL-005] | [ADR-0003] | [RC-012] |
| [ADR-0002] | ADR | [SA-001], [RC-001] | - | [RC-013] |
| [ADR-0003] | ADR | [MIL-005], [ADR-0001], [RC-011] | [ADR-0004] | [RC-014] |
| [ADR-0004] | ADR | [MIL-006], [ADR-0003], [ADR-0002] | - | [RC-018] |
| [RC-011] | RC | [MIL-005] | - | - |
| [RC-012] | RC | [ADR-0001] | - | - |
| [RC-013] | RC | [ADR-0002] | - | - |
| [RC-014] | RC | [ADR-0003] | - | - |
| [RC-015] | RC | [PP-001] | - | - |
| [RC-016] | RC | [MIL-006] | - | - |
| [RC-017] | RC | [PP-001] | - | - |
| [RC-018] | RC | [ADR-0004] | - | - |
| [UCD-001] | UCD | [SA-001], [BC-001] | [US-001], [UC-001], [UC-002], [UC-003], [UC-004], [UC-005] | [RC-019], [RC-035] |
| [US-001] | US | [UCD-001], [BC-001], [MIL-001], [MIL-002], [MIL-003] | [UC-001], [UC-002], [UC-003], [UC-004], [UC-005] | [RC-020], [RC-036] |
| [UC-001] | UC | [UCD-001], [US-001], [SA-001] | - | [RC-021] |
| [UC-002] | UC | [UCD-001], [US-001], [SA-001] | - | [RC-022] |
| [UC-003] | UC | [UCD-001], [US-001], [SA-001] | - | [RC-023] |
| [UC-004] | UC | [UCD-001], [US-001], [SA-001] | - | [RC-024] |
| [UC-005] | UC | [UCD-001], [US-001], [SA-001] | [ADR-0005] | [RC-037] |
| [ADR-0005] | ADR | [MIL-003], [UC-005], [US-001], [ADR-0004] | - | [RC-038] |
| [RC-019] | RC | [UCD-001] | - | - |
| [RC-020] | RC | [US-001] | - | - |
| [RC-021] | RC | [UC-001] | - | - |
| [RC-022] | RC | [UC-002] | - | - |
| [RC-023] | RC | [UC-003] | - | - |
| [RC-024] | RC | [UC-004] | - | - |
| [RC-025] | RC | [PP-001] | - | - |
| [RC-026] | RC | [MIL-001] | - | - |
| [RC-027] | RC | [MIL-002] | - | - |
| [RC-028] | RC | [MIL-003] | - | - |
| [RC-029] | RC | [MIL-004] | - | - |
| [RC-030] | RC | [MIL-005] | - | - |
| [RC-031] | RC | [MIL-006] | - | - |
| [RC-032] | RC | [PP-001] | - | - |
| [RC-033] | RC | [MIL-003] | - | - |
| [RC-034] | RC | [MIL-004] | - | - |
| [RC-035] | RC | [UCD-001] | - | - |
| [RC-036] | RC | [US-001] | - | - |
| [RC-037] | RC | [UC-005] | - | - |
| [RC-038] | RC | [ADR-0005] | - | - |
| [RC-039] | RC | [MIL-003] | - | - |

## Coverage Notes

- `-` in Upstream means foundational (SA-001 has no prerequisite). In Downstream it means nothing is built on the instance yet. In Last Reviewed it means no `RC-*` exists (review records are not themselves reviewed).
- Types with no instance yet: KPI, BMC, BPMN, SSD, DM, OC, SD, DCD, ERD, GOV, DICT. The four P1 use case candidates are written as brief use cases (UC-001 to UC-004); the P2 and P3 candidates have no use case document yet.
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
[ADR-0004]: ../adr/adr-0004-shared-wiki-publishing-opt-in.md
[RC-013]: ./reviews/rc-013-adr-0002.md
[RC-014]: ./reviews/rc-014-adr-0003.md
[RC-015]: ./reviews/rc-015-project-plan-pat.md
[RC-016]: ./reviews/rc-016-mil-006.md
[RC-017]: ./reviews/rc-017-project-plan-mil-006.md
[RC-018]: ./reviews/rc-018-adr-0004.md
[UCD-001]: ../use-case-diagram.md
[US-001]: ../user-stories.md
[UC-001]: ../uc-001/uc.md
[UC-002]: ../uc-002/uc.md
[UC-003]: ../uc-003/uc.md
[UC-004]: ../uc-004/uc.md
[RC-019]: ./reviews/rc-019-ucd-001.md
[RC-020]: ./reviews/rc-020-us-001.md
[RC-021]: ./reviews/rc-021-uc-001.md
[RC-022]: ./reviews/rc-022-uc-002.md
[RC-023]: ./reviews/rc-023-uc-003.md
[RC-024]: ./reviews/rc-024-uc-004.md
[RC-025]: ./reviews/rc-025-pp-001-use-cases.md
[RC-026]: ./reviews/rc-026-mil-001-date.md
[RC-027]: ./reviews/rc-027-mil-002-date.md
[RC-028]: ./reviews/rc-028-mil-003-date.md
[RC-029]: ./reviews/rc-029-mil-004-date.md
[RC-030]: ./reviews/rc-030-mil-005-date.md
[RC-031]: ./reviews/rc-031-mil-006-date.md
[RC-032]: ./reviews/rc-032-pp-001-dates.md
[RC-033]: ./reviews/rc-033-mil-003-reusable-workflows.md
[RC-034]: ./reviews/rc-034-mil-004-scripts.md
[RC-035]: ./reviews/rc-035-ucd-001.md
[RC-036]: ./reviews/rc-036-us-001.md
[RC-037]: ./reviews/rc-037-uc-005.md
[RC-038]: ./reviews/rc-038-adr-0005.md
[RC-039]: ./reviews/rc-039-mil-003-adoption.md
[UC-005]: ../uc-005/uc.md
[ADR-0005]: ../adr/adr-0005-quality-check-contract.md
[385d2fb]: https://git.tirsystem.com/TirSystem/github-action/commit/385d2fb7cb9be1fdc8fd3503d0af624fa38eafc7
[3b8681d]: https://git.tirsystem.com/TirSystem/github-action/commit/3b8681d0236c669b794ffbba725433fff600a2d2
