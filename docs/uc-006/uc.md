# UC-006: Release a Reusable Workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | UC-006 |
| CrossReference | [UCD-001], [US-001], [SA-001], [ADR-0006] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | [044d8ba] |

---

**Format:** Brief

**Title:** Release a Reusable Workflow
**Scope:** Reusable Workflow Collection
**Level:** user-goal
**Primary Actor:** DevOps Professional
**Stakeholders:** S05, S02, S03 (interests below)
**Stories:** US-001.11, US-001.12

## Brief

When a change to the workflows or their scripts is ready on the default branch, the DevOps Professional checks that the repository's validation run on that commit is green, adds the version to the changelog with each breaking change marked, and creates the version tag and moves the major tag of the same major version. The release page for the tag is created from the changelog entry and announces what changed and whether consumers need to act. Consumers pinned to the previous version are not affected.

**Stakeholder interests**

- S05 — a release is a deliberate, validated, reviewed step, and a faulty one can be undone
- S02 — a pinned pipeline never changes under them, and a changelog tells them whether to act
- S03 — a change to credentials, tokens or permissions is visible in the changelog before it reaches runners

**Preconditions:** The repository's validation run exists and is green on the commit to be released, and the version scheme of ADR-0006 is defined.

**Postconditions (success guarantee):** A version tag and a changelog entry exist for the commit, the major tag points to the latest compatible release, the release page announces it, and pipelines pinned to earlier versions run unchanged.

---

[UCD-001]: ../use-case-diagram.md
[US-001]: ../user-stories.md
[SA-001]: ../stakeholder-analysis.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
[044d8ba]: https://git.tirsystem.com/TirSystem/github-action/commit/044d8ba21f96f4aceb807d62addc35cdcbb56051
