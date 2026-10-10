# UC-002: Configure Workflow Credentials

## Metadata
| Key | Value |
| --- | --- |
| ID | UC-002 |
| CrossReference | [UCD-001], [US-001], [SA-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | [a2bf2d4] |

---

**Format:** Brief

**Title:** Configure Workflow Credentials
**Scope:** Reusable Workflow Collection
**Level:** user-goal
**Primary Actor:** DevOps Professional
**Stakeholders:** S05, S03, S02 (interests below)
**Stories:** US-001.03, US-001.04

## Brief

The DevOps Professional creates a Gitea token and a GitHub fine-grained token with the minimum permissions in the credentials guide, and the Platform Operator stores them once as secrets of the organization, each holding only the token. A run of the workflow checks that each token is accepted and, for GitHub, that it can administer the mirror, and reports `Preflight passed` without printing any secret value.

**Stakeholder interests**

- S05 — credentials are least-privilege and checked before use
- S03 — tokens are scoped, stored as secrets and never printed
- S02 — a failed credential check says which secret to fix

**Preconditions:** The actor has access to the Gitea and GitHub settings and can store secrets for the organization.

**Postconditions (success guarantee):** Both secrets hold only a token, a run passes the credential check with the documented minimum permissions, and no secret value appeared in a log.

---

[UCD-001]: ../use-case-diagram.md
[US-001]: ../user-stories.md
[SA-001]: ../stakeholder-analysis.md
[a2bf2d4]: https://git.tirsystem.com/TirSystem/github-action/commit/a2bf2d420416f7aff2badc6fe32a7690e2e523fd
