# MIL-002: Onboarding and operations guide

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-002 |
| CrossReference | [BC-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-03 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version | [4de5438] |
| 2026-10-03 | Proposed | Jens Tirsvad Nielsen | S01 | Owner is S05 (security authority); S01 remains approving reviewer | [4de5438] |

---

## Purpose

Decide whether a DevOps professional can onboard a repository, set up
credentials, choose runners and diagnose a failed run from the documentation
alone.

## Deliverable

An onboarding and operations guide verified against the real Gitea instance,
a credential validation step in the workflow, and categorized failure messages.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | Support for scoped workflows on the instance is verified and the Gitea version is recorded | Recorded | Unverified |
| 2 | A second repository is onboarded by following only the guide | Run succeeds | Needs undocumented steps |
| 3 | Minimum token permissions are documented for both secrets and checked by the workflow before use | Documented and checked | Missing |
| 4 | Every failure message names its category: configuration, credentials, permissions, API response or runner | Verified for all messages | Uncategorized message exists |
| 5 | Supported runner labels and prerequisites are listed | Listed | Missing |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-001 | The guide describes the stabilised workflow |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O2, O3 | [BC-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-10-31 — proposed; to be confirmed by S01 and S05.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Write brief use cases for the P1 candidates | Turn the DevOps use cases in the Project Plan appendix into use case documents under `docs/uc-NNN/`, after a use case diagram and user stories exist. | No | |
| 2 | Verify scoped workflow support on the instance | The Business Case lists this as an unverified assumption. Check the Gitea version and how a scoped workflow reaches a repository, then record the result. | No | |
| 3 | Write the repository onboarding steps | Describe how to consume the workflow (scoped or copied), which secrets to set and how to test the first run. | No | |
| 4 | Document least-privilege tokens | Determine the minimum Gitea token scope and GitHub fine-grained token permission that the sync needs, and document them. | No | |
| 5 | Add a credential preflight step | Before the sync, check that both tokens authenticate and have the needed access, and report the result without printing any secret. | No | |
| 6 | Categorize failure messages | Group the error messages and HTTP errors into configuration, credentials, permissions, API response and runner, and write the diagnosis table. | No | |
| 7 | Document runner labels and prerequisites | State the supported labels (`ubuntu-latest`), the required `python3`, and how to recognize an offline or incompatible runner. | No | |

---

[BC-001]: ../business-case.md
[4de5438]: https://git.tirsystem.com/TirSystem/github-action/commit/4de5438a88b4bbf18b165f52f797d1a52af89f6d
