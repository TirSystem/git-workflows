# Review Record: ADR-0004 superseded by ADR-0009

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-065 |
| CrossReference | [ADR-0004], [ADR-0009], [QC-ADR-001], [MIL-009] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | Accepted | Jens Tirsvad Nielsen | AI as stand-in for S01 | Initial version | pending |

---

## Artifact Under Review

- Instance reviewed: [ADR-0004] after the status change to `Superseded by ADR-0009` on 2026-10-14
- Checklist used: [QC-ADR-001]
- Scope: delta re-review of the criteria the status change touches (7, 8, 9, 11); the earlier record is RC-018
- Language and domain: n/a (technical type)
- Mode: autonomous, not independent (the reviewer is `AI as stand-in for S01`; the user accepted the plan [MIL-009] in chat on 2026-10-14)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | The ID matches the filename number and is unique and sequential | Pass | Unchanged. |
| 2 | Context states the problem, the forces and the options evaluated | Pass | Unchanged. |
| 3 | At least two options were considered | Pass | Unchanged. |
| 4 | Decision is stated in one or two unhedged sentences and matches an evaluated option | Pass | Unchanged. |
| 5 | Consequences list both Positive and Negative outcomes | Pass | Unchanged. |
| 6 | Quality-attribute impacts are named where the decision affects them | Pass | Unchanged. |
| 7 | Affected Artifacts are listed as links, and each is also in CrossReference | Pass | ADR-0009 is added to both. |
| 8 | Status changes are recorded as new Version History rows with a Change summary and Commit link; retained rows are never rewritten | Pass | The change is a new row; the earlier `Accepted` row became `Deprecated` and its content is unchanged. |
| 9 | A superseded or deprecated ADR names its successor, and the successor links back | Pass | The status names ADR-0009; ADR-0009 lists ADR-0004 under Affected Artifacts and in CrossReference. This closes the N-A of RC-018. |
| 10 | Written in the language of the domain, with no unexplained abbreviations | Pass | Unchanged. |
| 11 | Status is one of the allowed values and every row uses only these | Pass | `Deprecated` and `Superseded by ADR-0009`. |

## Overall Verdict

Go - all criteria pass. The scoped delivery and the marker are replaced and removed (MIL-009 tasks 2 to 6); the token and empty-folder rules of this ADR stand and are carried by ADR-0009. The AI records the acceptance as stand-in for S01; there is no independent reader, and the decision stays open to challenge in the run summary.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| None open | - | - |

---

[ADR-0004]: ../../adr/adr-0004-shared-wiki-publishing-opt-in.md
[ADR-0009]: ../../adr/adr-0009-wiki-publishing-reusable-workflow.md
[QC-ADR-001]: ../../../framework/qc/artifacts/qc-adr.md
[MIL-009]: ../../milestones/mil-009-migrate-wiki-callers-and-remove-scoped-workflow.md
