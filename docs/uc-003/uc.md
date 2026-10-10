# UC-003: Onboard a Repository

## Metadata
| Key | Value |
| --- | --- |
| ID | UC-003 |
| CrossReference | [UCD-001], [US-001], [SA-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | pending |

---

**Format:** Brief

**Title:** Onboard a Repository
**Scope:** Reusable Workflow Collection
**Level:** user-goal
**Primary Actor:** DevOps Professional
**Stakeholders:** S05, S02, S03 (interests below)
**Stories:** US-001.05, US-001.06

## Brief

The DevOps Professional follows the onboarding guide for a repository: checks that Actions and a runner are available, configures the GitHub push mirror, includes the credential configuration for the organization if it is not done yet, sets a description and topics, and triggers a first run. Scoped delivery runs the shared workflow in the repository without a copy, and the log ends with the synchronized repository.

**Stakeholder interests**

- S05 — a repository gets the standard automation without copying workflow files
- S02 — onboarding is quick and needs no undocumented step
- S03 — a repository uses only supported runners and its organization's secrets

**Preconditions:** Actions are enabled in the repository, a runner with the needed label is online, and the secrets can be stored for the repository's organization.

**Postconditions (success guarantee):** The first run in the repository passes using only the onboarding guide, and the repository needs no copy of the workflow.

---

[UCD-001]: ../use-case-diagram.md
[US-001]: ../user-stories.md
[SA-001]: ../stakeholder-analysis.md
