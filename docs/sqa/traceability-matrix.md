# Traceability Matrix

## Metadata
| Key | Value |
| --- | --- |
| ID | TM-001 |
| CrossReference | [BC-001], [SA-001], [PP-001], [MIL-001], [MIL-002], [MIL-003], [MIL-004], [MIL-005], [MIL-006], [MIL-007], [RC-001], [RC-002], [RC-003], [RC-004], [RC-005], [RC-006], [RC-007], [RC-008], [RC-009], [RC-010], [RC-011], [RC-012], [RC-013], [RC-014], [RC-015], [RC-016], [RC-017], [RC-018], [RC-019], [RC-020], [RC-021], [RC-022], [RC-023], [RC-024], [RC-025], [RC-026], [RC-027], [RC-028], [RC-029], [RC-030], [RC-031], [RC-032], [RC-033], [RC-034], [RC-035], [RC-036], [RC-037], [RC-038], [RC-039], [RC-040], [RC-041], [RC-042], [RC-043], [RC-044], [RC-045], [RC-046], [RC-047], [RC-048], [RC-049], [RC-050], [RC-051], [RC-052], [RC-053], [ADR-0007], [UC-007], [UC-006], [ADR-0006], [UC-005], [ADR-0005], [UCD-001], [US-001], [UC-001], [UC-002], [UC-003], [UC-004], [ADR-0001], [ADR-0002], [ADR-0003], [ADR-0004] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-11 | Deprecated | Jens Tirsvad Nielsen | S01 | Added RC-051 (ADR-0005 tools-ref) | [670f0ac] |
| 2026-10-11 | Accepted | Jens Tirsvad Nielsen | S01 | Added MIL-007, RC-052 and RC-053 | [e3ad1fa] |

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
| [PP-001] | PP | [BC-001], [SA-001] | [MIL-001], [MIL-002], [MIL-003], [MIL-004], [MIL-005], [MIL-006], [MIL-007], [US-001] | [RC-002], [RC-009], [RC-015], [RC-017], [RC-025], [RC-032], [RC-053] |
| [MIL-001] | MIL | [BC-001], [PP-001] | [MIL-002] | [RC-003], [RC-026] |
| [MIL-002] | MIL | [BC-001], [PP-001], [MIL-001] | [MIL-003], [MIL-005] | [RC-005], [RC-027] |
| [MIL-003] | MIL | [BC-001], [PP-001], [MIL-002] | [MIL-004] | [RC-006], [RC-028], [RC-033], [RC-039] |
| [MIL-004] | MIL | [BC-001], [PP-001], [MIL-003] | - | [RC-007], [RC-029], [RC-034], [RC-048] |
| [RC-001] | RC | [BC-001] | - | - |
| [RC-002] | RC | [PP-001] | - | - |
| [RC-003] | RC | [MIL-001] | - | - |
| [RC-004] | RC | [SA-001] | - | - |
| [RC-005] | RC | [MIL-002] | - | - |
| [RC-006] | RC | [MIL-003] | - | - |
| [MIL-005] | MIL | [BC-001], [PP-001], [MIL-002] | [MIL-006] | [RC-010], [RC-011], [RC-030], [RC-050] |
| [MIL-006] | MIL | [BC-001], [PP-001], [MIL-002], [MIL-005] | - | [RC-016], [RC-031], [RC-049] |
| [MIL-007] | MIL | [BC-001], [PP-001], [MIL-003], [MIL-004] | - | [RC-052] |
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
| [UCD-001] | UCD | [SA-001], [BC-001] | [US-001], [UC-001], [UC-002], [UC-003], [UC-004], [UC-005], [UC-006], [UC-007] | [RC-019], [RC-035], [RC-040], [RC-045] |
| [US-001] | US | [UCD-001], [BC-001], [MIL-001], [MIL-002], [MIL-003], [MIL-004] | [UC-001], [UC-002], [UC-003], [UC-004], [UC-005], [UC-006], [UC-007] | [RC-020], [RC-036], [RC-041], [RC-046] |
| [UC-001] | UC | [UCD-001], [US-001], [SA-001] | - | [RC-021] |
| [UC-002] | UC | [UCD-001], [US-001], [SA-001] | - | [RC-022] |
| [UC-003] | UC | [UCD-001], [US-001], [SA-001] | - | [RC-023] |
| [UC-004] | UC | [UCD-001], [US-001], [SA-001] | - | [RC-024] |
| [UC-005] | UC | [UCD-001], [US-001], [SA-001] | [ADR-0005] | [RC-037] |
| [ADR-0005] | ADR | [MIL-003], [UC-005], [US-001], [ADR-0004] | - | [RC-038], [RC-051] |
| [UC-006] | UC | [UCD-001], [US-001], [SA-001] | [ADR-0006] | [RC-042] |
| [ADR-0006] | ADR | [MIL-004], [UC-006], [US-001], [ADR-0004], [ADR-0005] | - | [RC-043] |
| [ADR-0007] | ADR | [MIL-004], [UC-006], [ADR-0006] | - | [RC-047] |
| [UC-007] | UC | [UCD-001], [US-001], [SA-001] | - | [RC-044] |
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
| [RC-040] | RC | [UCD-001] | - | - |
| [RC-041] | RC | [US-001] | - | - |
| [RC-042] | RC | [UC-006] | - | - |
| [RC-043] | RC | [ADR-0006] | - | - |
| [RC-044] | RC | [UC-007] | - | - |
| [RC-045] | RC | [UCD-001] | - | - |
| [RC-046] | RC | [US-001] | - | - |
| [RC-047] | RC | [ADR-0007] | - | - |
| [RC-048] | RC | [MIL-004] | - | - |
| [RC-049] | RC | [MIL-006] | - | - |
| [RC-050] | RC | [MIL-005] | - | - |
| [RC-051] | RC | [ADR-0005] | - | - |
| [RC-052] | RC | [MIL-007] | - | - |
| [RC-053] | RC | [PP-001] | - | - |

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
[MIL-007]: ../milestones/mil-007-cpp-csharp-quality-checks.md
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
[RC-040]: ./reviews/rc-040-ucd-001-release.md
[RC-041]: ./reviews/rc-041-us-001-release.md
[RC-042]: ./reviews/rc-042-uc-006.md
[RC-043]: ./reviews/rc-043-adr-0006.md
[RC-044]: ./reviews/rc-044-uc-007.md
[RC-045]: ./reviews/rc-045-ucd-001-consume.md
[RC-046]: ./reviews/rc-046-us-001-consume.md
[RC-047]: ./reviews/rc-047-adr-0007.md
[RC-048]: ./reviews/rc-048-mil-004-outcome.md
[RC-049]: ./reviews/rc-049-mil-006-outcome.md
[RC-050]: ./reviews/rc-050-mil-005-outcome.md
[RC-051]: ./reviews/rc-051-adr-0005-tools-ref.md
[RC-052]: ./reviews/rc-052-mil-007.md
[RC-053]: ./reviews/rc-053-pp-001-mil-007.md
[ADR-0007]: ../adr/adr-0007-release-publish-destination.md
[UC-007]: ../uc-007/uc.md
[UC-006]: ../uc-006/uc.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
[UC-005]: ../uc-005/uc.md
[ADR-0005]: ../adr/adr-0005-quality-check-contract.md
[670f0ac]: https://git.tirsystem.com/TirSystem/github-action/commit/670f0ac469043bb166c84290c0dbf62b4908e3cc
[e3ad1fa]: https://git.tirsystem.com/TirSystem/github-action/commit/e3ad1fa7e7eef57a6793a479edb41ac6fd2db688
