# User Story

## Metadata
| Key | Value |
| --- | --- |
| ID | US-001 |
| CrossReference | [UCD-001], [BC-001], [MIL-001], [MIL-002], [UC-001], [UC-002], [UC-003], [UC-004] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | pending |

---

## Purpose and Scope

These stories cover the P1 use cases of the Project Plan that MIL-002 delivers
(O1 to O3 of [BC-001]): keeping the mirror metadata correct, configuring
credentials, onboarding a repository and diagnosing a failed run. Roles are the
actors of [UCD-001]. Stories for quality checks and releases (MIL-003,
MIL-004) and for the wiki (MIL-005, MIL-006) are not written yet.

## Story List

### US-001.01 — Mirror shows the Gitea metadata

**As a** DevOps Professional, **I want** the GitHub mirror to show the description and topics of the Gitea repository, **so that** visitors of the mirror see the same repository metadata as on the primary repository.

**Acceptance Criteria**

- Given a repository with one GitHub push mirror, when the workflow runs, then the GitHub description and topics equal the Gitea ones.
- Given the description or the topics changed on Gitea, when the next run completes, then the GitHub mirror shows the new values.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-001], [MIL-002] | fits one iteration | none |

### US-001.02 — Repository without a mirror is skipped

**As a** DevOps Professional, **I want** a repository without a GitHub mirror to be skipped successfully, **so that** repositories that have no mirror do not show failed runs.

**Acceptance Criteria**

- Given a repository with no GitHub push mirror, when the workflow runs, then the run succeeds and the log says that there is nothing to sync.
- Given a repository with several GitHub push mirrors, when the workflow runs, then the run fails with a configuration message and changes nothing.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-001], [MIL-002] | fits one iteration | none |

### US-001.03 — Check the tokens before changing anything

**As a** DevOps Professional, **I want** both tokens to be checked before the workflow changes anything, **so that** a wrong or too weak token is found without any side effect.

**Acceptance Criteria**

- Given a token that GitHub rejects, when the workflow runs, then nothing is changed and the log names the credentials category.
- Given a GitHub token without administration access, when the workflow runs, then it stops with a permissions message before the first change.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-002], [MIL-002] | fits one iteration | none |

### US-001.04 — Store the secrets once per organization

**As a** Platform Operator, **I want** to store a workflow's secrets once for an organization, **so that** every repository of the organization can use the workflow without its own copy of the secrets.

**Acceptance Criteria**

- Given the secrets are stored for an organization, when a repository of that organization runs the workflow, then it passes the credential check.
- Given a repository of another organization, when it runs the workflow, then it does not see these secrets and the log names the missing secret.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-002], [MIL-002] | fits one iteration | none |

### US-001.05 — Use the workflow without a copy

**As a** DevOps Professional, **I want** a repository to use the shared workflow without copying it, **so that** a fix made once reaches every repository.

**Acceptance Criteria**

- Given a repository without its own workflow files, when a push is made to `main`, then the shared workflow runs in it.
- Given the shared workflow changes, when the next run starts in another repository, then it runs the changed version.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-003], [MIL-002] | fits one iteration | none |

### US-001.06 — Onboard from one guide

**As a** DevOps Professional, **I want** to onboard a repository by following one guide, **so that** the first run passes without undocumented steps.

**Acceptance Criteria**

- Given a repository with Actions enabled and a runner, when its owner follows only the onboarding guide, then the first run succeeds.
- Given a step of the guide is wrong or missing, when it is found during onboarding, then it is raised as a defect of the guide.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-003], [MIL-002] | fits one iteration | none |

### US-001.07 — Every failure names its category

**As a** DevOps Professional, **I want** every failure message to name its category, **so that** I know at once whether to look at configuration, credentials, permissions, the service or the runner.

**Acceptance Criteria**

- Given any failure of the workflow, when its log is read, then the message starts with one of the categories configuration, credentials, permissions or api.
- Given a message that has no category, when it is found, then it is raised as a defect.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-004], [MIL-002] | fits one iteration | none |

### US-001.08 — Recognise a runner problem

**As a** Platform Operator, **I want** to recognise a runner problem from its symptom, **so that** I fix the runner and not the workflow.

**Acceptance Criteria**

- Given a run that stays waiting, when the troubleshooting guide is read, then it names the missing runner label as the cause.
- Given a job that fails before the script, when the guide is read, then it names the tool missing from the runner image.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-004], [MIL-002] | fits one iteration | none |

## INVEST Check

All eight stories are independent of each other except that US-001.05 and
US-001.06 build on US-001.04 (the secrets must exist before a repository can
run the workflow). Each states one goal and can be negotiated, delivers value
to the named role, is small enough for one iteration, and has acceptance
criteria that are checked with a run or a read of the guide. Exception:
US-001.01 and US-001.02 are already implemented and are written so that their
behaviour is tested rather than built.

---

[UCD-001]: ./use-case-diagram.md
[BC-001]: ./business-case.md
[MIL-001]: ./milestones/mil-001-stabilise-metadata-sync.md
[MIL-002]: ./milestones/mil-002-onboarding-and-operations.md
[UC-001]: ./uc-001/uc.md
[UC-002]: ./uc-002/uc.md
[UC-003]: ./uc-003/uc.md
[UC-004]: ./uc-004/uc.md
