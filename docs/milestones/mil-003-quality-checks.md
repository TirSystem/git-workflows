# MIL-003: Shared quality checks

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-003 |
| CrossReference | [BC-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-03 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version | pending |
| 2026-10-03 | Proposed | Jens Tirsvad Nielsen | S01 | Owner is S05 (security authority); S01 remains approving reviewer | pending |

---

## Purpose

Decide whether a software engineer can run the same quality checks on any
TirSystem project through a shared workflow.

## Deliverable

A reusable quality-check workflow for Python and shell, used by at least one
other repository, and a guide for reading its results.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The instance supports reusable workflows (`workflow_call`), verified and recorded | Verified | Unsupported (re-plan as a copied template) |
| 2 | One other repository runs the workflow and its status check appears on pull requests | Appears | Does not run |
| 3 | A failing check shows the tool, file and message in the log | Verified with a seeded failure | Cause not visible |
| 4 | Inputs and defaults are documented | Documented | Missing |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-002 | Uses the onboarding guide and runner list |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O4 | [BC-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-11-14 — proposed; to be confirmed by S01 and S05.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Verify reusable workflow support | Check whether this Gitea version supports `workflow_call` and cross-repository `uses`; if not, choose a copied template instead. | No | |
| 2 | Define the quality-check contract | Decide the inputs (language, tool versions, working directory) and what a pass and a fail mean. Start with Python and shell. This is something an engineer does, so it needs a use case first. | Yes | Use case candidate: run project quality checks |
| 3 | Implement the reusable quality workflow | Create the workflow in the canonical location with pinned tool versions and least-privilege permissions. | No | |
| 4 | Adopt it in one other repository | Onboard a real project and fix the gaps in the guide that appear. | No | |
| 5 | Write the guide for reading results | Explain status checks, logs and typical fixes so an engineer can make a failing check pass. | No | |

---

[BC-001]: ../business-case.md
