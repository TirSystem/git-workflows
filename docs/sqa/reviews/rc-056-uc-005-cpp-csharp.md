# Review Record: UC-005 (C++ and C#)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-056 |
| CrossReference | [UC-005], [QC-UC-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-11 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | [1bc56f8] |

---

## Artifact Under Review

- Instance reviewed: [UC-005] after the extension of its Brief to C++ and C# (MIL-007 task 1)
- Checklist used: [QC-UC-001] (Brief format)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | Consists of a single, concise paragraph summarizing only the primary success scenario | Pass | Finding fixed during this review: the extension had added a sentence about a language that needs a build or a project file and says what is missing, which is a failure flow. It is removed from the Brief; the stories US-001.16 and .17 carry it as an acceptance criterion. |
| 2 | Written as an informal multi-paragraph narrative; may mention some alternate flows without formal structure | N-A | Format is Brief. |
| 3 | All standard sections are present: actors, preconditions, postconditions, main success scenario, alternative/exception flows | N-A | Format is Brief; actor, stakeholders, pre- and postconditions and the paragraph are present. |
| 4 | Preconditions and postconditions are explicitly defined | Pass | The precondition now lists the four languages (Python, shell, C++, C#); the postcondition is unchanged. |
| 5 | Primary actor is explicitly stated | Pass | Software Engineer. |
| 6 | Stakeholders and their interests are stated | Pass | S02 and S05, unchanged. |
| 7 | Main success scenario is written as clear, numbered steps | N-A | Format is Brief. |
| 8 | Alternative/exception flows correctly reference `<<include>>`/`<<extend>>` use cases where relevant, per UML 2.5.1 | N-A | None in a Brief. |
| 9 | Explicit business rules are captured per step where applicable, rather than embedded loosely in narrative text | N-A | No steps in a Brief. |
| 10 | Naming of actors and use case title is consistent with the corresponding Use Case Diagram and User Stories | Pass | Title and actor equal UCD-001; the Stories line lists US-001.09, .10, .16 and .17, which exist. |
| 11 | Scope/level (e.g. summary, user-goal, subfunction) is explicitly stated | Pass | Scope and user-goal level, unchanged. |
| 12 | Use case is written from the actor's goal perspective, free of UI or implementation detail | Pass | Goal wording; the tool names are not in the Brief for C++ and C#. |

## Overall Verdict

Go - all applicable criteria pass; the one finding (criterion 1) was fixed during the review. S01 gave the Go in chat on 2026-10-11, standing in for the other reviewers as ADR-0002 records; there is no independent reader.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Update the description of this use case in the Use Case Diagram table of UCD-001 ("Lint, format and type checks run on every change ...") to cover C++ and C# at its next review | S01 | next review of UCD-001 |

---

[UC-005]: ../../uc-005/uc.md
[QC-UC-001]: ../../../framework/qc/qc-use-case.md
[1bc56f8]: https://git.tirsystem.com/TirSystem/github-action/commit/1bc56f8b771531f221f218fc00b147ecc73c051e
