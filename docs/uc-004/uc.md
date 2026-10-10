# UC-004: Diagnose a Failed Workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | UC-004 |
| CrossReference | [UCD-001], [US-001], [SA-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | pending |

---

**Format:** Brief

**Title:** Diagnose a Failed Workflow
**Scope:** Reusable Workflow Collection
**Level:** user-goal
**Primary Actor:** DevOps Professional
**Stakeholders:** S05, S03 (interests below)
**Stories:** US-001.07, US-001.08

## Brief

The DevOps Professional or the Platform Operator opens the failed run, reads the last lines of the failing step and takes the category from the message. The troubleshooting guide maps that category and message to a cause and a fix, which is applied, and the workflow is run again.

**Stakeholder interests**

- S05 — the cause of a failure is found quickly and fixed once
- S03 — a runner or secret problem is recognised as such and not blamed on the workflow

**Preconditions:** A run failed or did not start, and the actor can read the run log.

**Postconditions (success guarantee):** The cause is placed in one category (configuration, credentials, permissions, API response or runner) and the fix from the guide is applied or a defect is raised.

---

[UCD-001]: ../use-case-diagram.md
[US-001]: ../user-stories.md
[SA-001]: ../stakeholder-analysis.md
