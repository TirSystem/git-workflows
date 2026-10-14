# UC-008: Show Code Metrics and Coverage Badges

## Metadata
| Key | Value |
| --- | --- |
| ID | UC-008 |
| CrossReference | [UCD-001], [US-001], [SA-001], [MIL-010] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | Accepted | Jens Tirsvad Nielsen | AI as stand-in for S01 | Initial version; reviewed (RC-069) | pending |

---

**Format:** Brief

**Title:** Show Code Metrics and Coverage Badges
**Scope:** Reusable Workflow Collection
**Level:** user-goal
**Primary Actor:** Software Engineer
**Stakeholders:** S02, S05 (interests below)
**Stories:** US-001.18, US-001.19, US-001.20

## Brief

A Software Engineer pushes a change to a repository that calls the shared code-metrics workflow. The workflow counts the code files and the lines of code (without comment and blank lines), reads the coverage report the repository supplies, and publishes three badges: the number of code files, the number of lines of code and the coverage. The repository's README shows the badges, and they show the numbers of the latest push.

**Stakeholder interests**

- S02 — the size and the coverage of the code are visible at a glance, without a service outside the instance, and a wrong or missing report is reported instead of shown as a number
- S05 — the counting rules and the badge contract are defined once and change through a reviewed release

**Preconditions:** The repository is onboarded and the shared workflow is available through reusable workflow delivery; a coverage badge needs a coverage report that the repository's own tests have produced.

**Postconditions (success guarantee):** The three badges show the numbers of the pushed revision, nothing but the badges is changed in the repository, and a run whose numbers are unchanged changes nothing.

---

[UCD-001]: ../use-case-diagram.md
[US-001]: ../user-stories.md
[SA-001]: ../stakeholder-analysis.md
[MIL-010]: ../milestones/mil-010-code-metrics-badges.md
