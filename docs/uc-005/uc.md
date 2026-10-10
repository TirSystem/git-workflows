# UC-005: Run Project Quality Checks

## Metadata
| Key | Value |
| --- | --- |
| ID | UC-005 |
| CrossReference | [UCD-001], [US-001], [SA-001], [ADR-0005] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | pending |

---

**Format:** Brief

**Title:** Run Project Quality Checks
**Scope:** Reusable Workflow Collection
**Level:** user-goal
**Primary Actor:** Software Engineer
**Stakeholders:** S02, S05 (interests below)
**Stories:** US-001.09, US-001.10

## Brief

A Software Engineer opens a pull request in a repository that calls the shared quality-check workflow. The workflow installs the pinned tools, runs the checks for each selected language on the files of the repository (lint, format and types for Python; lint and format for shell), and reports one status for the pull request. When every selected tool passes, the status is green.

**Stakeholder interests**

- S02 — checks run the same way in every project without writing a pipeline, and a failure says what to fix
- S05 — the checks and their tool versions are defined once and change through a reviewed release

**Preconditions:** The repository is onboarded, the shared workflow is available through reusable workflow delivery, and the repository has files of at least one supported language.

**Postconditions (success guarantee):** The pull request has a pass or fail status that comes from every selected tool, and no file of the repository was changed.

---

[UCD-001]: ../use-case-diagram.md
[US-001]: ../user-stories.md
[SA-001]: ../stakeholder-analysis.md
[ADR-0005]: ../adr/adr-0005-quality-check-contract.md
