# UC-001: Synchronize Repository Metadata

## Metadata
| Key | Value |
| --- | --- |
| ID | UC-001 |
| CrossReference | [UCD-001], [US-001], [SA-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | pending |

---

**Format:** Brief

**Title:** Synchronize Repository Metadata
**Scope:** Reusable Workflow Collection
**Level:** user-goal
**Primary Actor:** DevOps Professional
**Stakeholders:** S05, S04 (interests below)
**Stories:** US-001.01, US-001.02

## Brief

A push to `main`, a manual run or the daily schedule starts the workflow. It checks that both tokens are accepted and that the GitHub token can administer the mirror, reads the description and topics from Gitea, finds the single GitHub push mirror, and sets the description and replaces the topics on GitHub. The run ends with a line that names the repository it synchronized.

**Stakeholder interests**

- S05 — the mirror shows what the primary repository shows, with no manual copying
- S04 — the description and topics on the mirror are correct and current

**Preconditions:** The repository has Actions enabled and a runner, both secrets are stored, and at most one GitHub push mirror is configured.

**Postconditions (success guarantee):** The description and topics of the GitHub mirror equal those of the Gitea repository, or the run ended without a change and said why.

---

[UCD-001]: ../use-case-diagram.md
[US-001]: ../user-stories.md
[SA-001]: ../stakeholder-analysis.md
