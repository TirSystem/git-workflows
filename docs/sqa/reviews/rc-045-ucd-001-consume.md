# Review Record: UCD-001 (consume an update)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-045 |
| CrossReference | [UCD-001], [QC-UCD-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | pending |

---

## Artifact Under Review

- Instance reviewed: [UCD-001]
- Checklist used: [QC-UCD-001]

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | Actors are defined with correct UML stereotypes (e.g. `<<System>>`, `<<Actor>>`) | Pass | Unchanged actors. |
| 2 | System boundary is clearly drawn and labeled | Pass | Unchanged. |
| 3 | Include/extend relationships are used correctly per UML 2.5.1, not as generic "uses" arrows | Pass | The new use case has none; its dependency on UC-006 is a precondition. |
| 4 | Every actor participates in at least one use case (no orphan actors) | Pass | Software Engineer now reaches two use cases. |
| 5 | Diagram is traceable to a documented stakeholder need | Pass | S02 in the Actor Table. |
| 6 | Use case names are verb phrases describing actor goals, not internal system operations | Pass | "Consume a Workflow Update". |
| 7 | Diagram is free of implementation detail (e.g. UI widgets, database tables) | Pass | No tool or file named. |
| 8 | Actor and use case naming is consistent with corresponding Use Case and User Story documents | Pass | UC-007's title and the story roles match. |

## Overall Verdict

Go - all eight criteria pass for the amendment (the use case of UC-007). S01 gave the Go in chat on 2026-10-10, standing in for the other reviewers as ADR-0002 records; there is no independent reader.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| None | - | - |

---

[UCD-001]: ../../use-case-diagram.md
[QC-UCD-001]: ../../../framework/qc/qc-use-case-diagram.md
