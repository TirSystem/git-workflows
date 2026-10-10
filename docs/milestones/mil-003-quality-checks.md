# MIL-003: Shared quality checks

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-003 |
| CrossReference | [BC-001], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-03 | Deprecated | Jens Tirsvad Nielsen | S01 | Owner is S05 (security authority); S01 remains approving reviewer | [4de5438] |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Target date 2026-11-14 confirmed on 2026-10-10 by S01 (stand-in for S05) | [ea06eaa] |

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

2026-11-14 — confirmed on 2026-10-10 by S01, standing in for S05 (ADR-0002); the Business Case sets no deadline.

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
[4de5438]: https://git.tirsystem.com/TirSystem/github-action/commit/4de5438a88b4bbf18b165f52f797d1a52af89f6d
[ADR-0002]: ../adr/adr-0002-s01-approves-as-stand-in.md
[ea06eaa]: https://git.tirsystem.com/TirSystem/github-action/commit/ea06eaaa698247d20e4a8e2694d7acbb1de58b63
