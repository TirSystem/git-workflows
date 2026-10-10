# UC-007: Consume a Workflow Update

## Metadata
| Key | Value |
| --- | --- |
| ID | UC-007 |
| CrossReference | [UCD-001], [US-001], [SA-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | [4cf52af] |

---

**Format:** Brief

**Title:** Consume a Workflow Update
**Scope:** Reusable Workflow Collection
**Level:** user-goal
**Primary Actor:** Software Engineer
**Stakeholders:** S02, S05 (interests below)
**Stories:** US-001.13, US-001.14, US-001.15

## Brief

When a new release of the shared workflows is announced, the Software Engineer reads its changelog entry to see whether it is breaking, changes the pinned version in one repository on a branch, opens a pull request and reads the run, and, when it is green, makes the same change in the other repositories.

**Stakeholder interests**

- S02 — an update is adopted deliberately, in one place first, and can be undone
- S05 — consumers move to supported versions without a support request

**Preconditions:** Releases are versioned with a changelog (the release process), and the repository calls the shared workflow at a version tag.

**Postconditions (success guarantee):** The repository calls the new version, its pipeline still passes, and the previous version remains the way back.

---

[UCD-001]: ../use-case-diagram.md
[US-001]: ../user-stories.md
[SA-001]: ../stakeholder-analysis.md
[4cf52af]: https://git.tirsystem.com/TirSystem/github-action/commit/4cf52afe00f546c6b20424fb8dfc12796ffd9296
