# Stakeholder Analysis: TirSystem Reusable Workflows

## Metadata
| Key | Value |
| --- | --- |
| ID | SA-001 |
| CrossReference | [BC-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-03 | Rejected | Jens Tirsvad Nielsen | S01 | Initial version | pending |
| 2026-10-03 | Accepted | Jens Tirsvad Nielsen | S01 | Added S05 Michael Kragh (DevOps owner, maintainer, cyber security)<br>S01 stays Product Owner and maintainer | pending |

---

## Purpose

This analysis identifies who depends on, operates or is affected by the
TirSystem reusable workflow collection, so that scope, priorities and
communication follow real needs. It uses a power/interest grid and maps
each concern to a FURPS+ attribute.

## Stakeholder Summary Table

| ID | Name | Role/Title | Organization | Power Level | Interest Level | Quadrant | Primary Concern (Business Language) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | Jens Tirsvad Nielsen | Product Owner and maintainer | TirSystem | HIGH | HIGH | Manage Closely | TirSystem repositories get the same automation without per-repository copy and paste, and scope follows business needs. |
| S02 | Software engineers on TirSystem projects | Consumers of shared workflows (group) | TirSystem | MEDIUM | HIGH | Keep Informed | Quality checks, builds and releases work out of the box, and failures say what to fix. |
| S03 | Gitea instance and runner operator | Platform operator (group; holders to be confirmed) | TirSystem | HIGH | MEDIUM | Keep Satisfied | Workflows run only on supported runners, use least-privilege tokens and never leak secrets. |
| S04 | GitHub mirror audience | Visitors of the GitHub push mirrors (group) | Public | LOW | LOW | Monitor | The mirror shows the same description and topics as the primary Gitea repository. |
| S05 | Michael Kragh | DevOps owner, maintainer and cyber security | TirSystem | HIGH | HIGH | Manage Closely | Shared automation is maintainable, and credentials, tokens and workflow permissions meet security requirements. |

## Power/Interest Classification Rationale

- **Manage Closely (S01):** decides scope and priorities, accepts documents and co-maintains the workflows.
- **Manage Closely (S05):** owns and co-maintains the workflows and is the security
  authority; credential, token and permission design cannot be accepted
  without this role.
- **Keep Informed (S02):** does not decide scope, but adoption by these
  engineers is the success measure; a breaking workflow change hits them first.
- **Keep Satisfied (S03):** controls runners, secrets and Gitea features
  (Actions, scoped workflows) that the workflows rely on; an incompatible
  change can be blocked here.
- **Monitor (S04):** passive consumers of mirror metadata; no action needed
  beyond keeping the metadata correct.

## Primary Concerns and FURPS+ Mapping

| ID | Concern | FURPS+ attribute |
| --- | --- | --- |
| S01 | One reviewed source of truth for shared automation | Supportability |
| S01 | Documentation never claims behavior that is not implemented | Functionality |
| S05 | One maintainable, reviewed source of truth for shared automation | Supportability |
| S05 | Least-privilege tokens, no secret in logs, pinned and reviewed workflow code | Functionality (security) |
| S02 | Clear failure messages that name the cause | Usability |
| S02 | Pinned, versioned workflows with a changelog | Supportability |
| S03 | Least-privilege tokens and no secret in logs | Functionality (security) |
| S03 | Declared runner labels and prerequisites | Supportability |
| S04 | Correct, current mirror description and topics | Functionality |

## Communication Requirements

| ID | Channel | Frequency | Deliverable | Phase / Milestone |
| --- | --- | --- | --- | --- |
| S01 | Pull request review and chat | Per milestone | Accepted documents, issue list | All milestones |
| S02 | README and changelog in the repository | Per workflow release | Usage guide, upgrade notes | MIL-002 onward |
| S05 | Pull request review and issue tracker | Per change to workflows, credentials or runners | Security-reviewed changes, token scope list | All milestones |
| S03 | Issue tracker | Per change to credentials or runners | Prerequisites and token scope list | MIL-001, MIL-002 |
| S04 | None (mirror metadata only) | Daily sync | Updated description and topics | MIL-001 |

## Conflicting Interests and Mitigations

| Conflict | Stakeholders | Mitigation |
| --- | --- | --- |
| Fast adoption of new workflow behavior versus stable consuming repositories | S01, S02 | Version every shared workflow and document breaking changes before release (MIL-004). |
| Convenient broad tokens versus least privilege | S02, S03 | Document the minimum token scope per workflow and validate it before use (MIL-002). |
| Delivery speed versus security review | S01, S05 | S05 reviews every change to credentials, tokens, permissions and workflow code before the milestone is accepted by S01. |
| Operator role holder not yet identified | S03, S05 | Confirm who operates runners and the Gitea instance; until then S05 is the contact. |

## Traceability Analysis

### Business Goal Alignment

| Stakeholder | Concern | Business Case objective |
| --- | --- | --- |
| S01 | One source of truth for shared automation | O1, O2 |
| S02 | Clear failures, versioned updates | O3, O4 |
| S03 | Least privilege, runner compatibility | O3 |
| S05 | Maintainable shared automation, security | O1, O2, O3 |
| S04 | Correct mirror metadata | O1 |

Objectives are defined in [BC-001]. Use-case mapping: S05 and S03 are the
primary actors of the DevOps use cases, S02 of the software engineer use
cases; both are listed in the Project Plan appendix.

## Sign-Off

Pending review by S01 and S05.

---

[BC-001]: ./business-case.md
