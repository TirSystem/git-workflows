# UC-006: Release a Reusable Workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | UC-006 |
| CrossReference | [UCD-001], [US-001], [SA-001], [ADR-0006], [ADR-0017] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version | [044d8ba] |
| 2026-11-07 | Accepted | Jens Tirsvad Nielsen | S01 | The workflow makes the tag when the changelog entry is merged (MIL-020; action item of RC-106); accepted by the author in chat as stand-in for S01, not independent | [94e7e39] |

---

**Format:** Brief

**Title:** Release a Reusable Workflow
**Scope:** Reusable Workflow Collection
**Level:** user-goal
**Primary Actor:** DevOps Professional
**Stakeholders:** S05, S02, S03 (interests below)
**Stories:** US-001.11, US-001.12, US-001.21, US-001.22, US-001.23

## Brief

When a change to the workflows or their scripts is ready on the default branch, the DevOps Professional adds the version to the changelog with each breaking change marked and merges that change to the default branch. The release workflow starts on that merge, waits for the repository's validation run on the same commit to be green, creates the version tag and moves the major tag of the same major version. The release page for the tag is created from the changelog entry and announces what changed and whether consumers need to act. Consumers pinned to the previous version are not affected.

**Stakeholder interests**

- S05 — a release is a deliberate, validated, reviewed step (the merge of the changelog entry), needs no manual run, and a faulty one can be undone
- S02 — a pinned pipeline never changes under them, and a changelog tells them whether to act
- S03 — a change to credentials, tokens or permissions is visible in the changelog before it reaches runners

**Preconditions:** The repository's validation run exists and is green on the commit to be released, and the version scheme of ADR-0006 is defined.

**Postconditions (success guarantee):** The workflow has made a version tag and a changelog entry exist for the commit, the major tag points to the latest compatible release, the release page announces it, and pipelines pinned to earlier versions run unchanged.

---

[UCD-001]: ../../use-case-diagram.md
[US-001]: ../../user-stories.md
[SA-001]: ../../stakeholder-analysis.md
[ADR-0006]: ../../adr/adr-0006-release-process-and-version-pinning.md
[ADR-0017]: ../../adr/adr-0017-scoped-release-workflow.md
[044d8ba]: https://git.tirsystem.com/TirSystem/github-action/commit/044d8ba21f96f4aceb807d62addc35cdcbb56051
[94e7e39]: https://git.tirsystem.com/TirSystem/git-workflows/commit/94e7e39e0a1dcb6f0b72476ca51ae8ffd959a211
