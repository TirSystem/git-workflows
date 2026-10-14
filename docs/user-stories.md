# User Story

## Metadata
| Key | Value |
| --- | --- |
| ID | US-001 |
| CrossReference | [UCD-001], [BC-001], [MIL-001], [MIL-002], [MIL-003], [MIL-004], [UC-001], [UC-002], [UC-003], [UC-004], [UC-005], [UC-006], [UC-007], [MIL-007], [UC-008], [MIL-010] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-11 | Deprecated | Jens Tirsvad Nielsen | S01 | US-001.16 and US-001.17 reviewed (RC-057) and accepted; the Purpose and Scope names the later stories | [1bc56f8] |
| 2026-10-14 | Accepted | Jens Tirsvad Nielsen | AI as stand-in for S01 | Added US-001.18 to US-001.20 (code metrics and coverage badges, MIL-010 task 1); reviewed (RC-070) | [9ca9673] |

---

## Purpose and Scope

These stories cover the P1 use cases of the Project Plan that MIL-002 delivers
(O1 to O3 of [BC-001]): keeping the mirror metadata correct, configuring
credentials, onboarding a repository and diagnosing a failed run. Roles are the
actors of [UCD-001]. Later stories cover quality checks (US-001.09, US-001.10 and, for
C++ and C#, US-001.16 and US-001.17), releases and updates (US-001.11 to
US-001.15) and the code metrics and coverage badges (US-001.18 to
US-001.20). Stories for the wiki (MIL-005, MIL-006) are not written yet.

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

### US-001.09 — Same checks on every change

**As a** Software Engineer, **I want** every pull request to run the same quality checks for the languages of my repository, **so that** a defect is found before review without me writing a pipeline.

**Acceptance Criteria**

- Given a repository that calls the shared workflow and has Python files, when a pull request is opened, then lint, format and type checks run and the status is pass or fail.
- Given a repository that has shell scripts, when a pull request is opened, then lint and format checks run for them and the status is pass or fail.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-005], [MIL-003] | fits one iteration | none |

### US-001.10 — A failure says what to fix

**As a** Software Engineer, **I want** a failed check to show the tool, the file, the line and the message, **so that** I can fix it without reading the workflow.

**Acceptance Criteria**

- Given a file with a finding, when the check runs, then the job fails and the log shows the tool name with `path:line` and the tool's message.
- Given a language that has no files in the repository, when the check runs, then it passes and the log says that nothing was checked.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-005], [MIL-003] | fits one iteration | none |

### US-001.11 — Only validated commits are released

**As a** DevOps Professional, **I want** a release to be created only from a commit whose validation run is green, **so that** consumers never receive an unchecked version.

**Acceptance Criteria**

- Given a commit whose validation run failed, when a release is attempted, then no version tag is created.
- Given a green commit and a changelog entry for the version, when the release is created, then the version tag, the major tag and the release page exist.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-006], [MIL-004] | fits one iteration | none |

### US-001.12 — A release says whether it is breaking

**As a** DevOps Professional, **I want** every release to say whether it is breaking, **so that** consumers know whether they must act.

**Acceptance Criteria**

- Given a change that renames a workflow, an input or a secret, or can turn a passing consumer red, when it is released, then the changelog marks it as breaking and a new major version is created.
- Given a compatible change, when it is released, then the major tag moves to it and consumers pinned to that major version receive it.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-006], [MIL-004] | fits one iteration | none |

### US-001.13 — A pin that does not move

**As a** Software Engineer, **I want** to pin the shared workflows to a version that does not change under me, **so that** a release cannot break my pipeline by surprise.

**Acceptance Criteria**

- Given a repository that calls a shared workflow at an exact version tag, when a new release is made, then its runs use the same code as before.
- Given a repository that calls a shared workflow at a major tag, when a compatible release is made, then it receives the release and a breaking release is not delivered to it.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-007], [MIL-004] | fits one iteration | none |

### US-001.14 — A changelog says whether to act

**As a** Software Engineer, **I want** to see in a changelog entry whether a release is breaking, **so that** I know whether I must change my pipeline.

**Acceptance Criteria**

- Given a release page or a changelog entry, when it is read, then the groups Breaking, Added, Changed and Fixed are visible and a breaking change is the first group.
- Given a breaking release, when the entry is read, then it names what changed and what to do.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-007], [MIL-004] | fits one iteration | none |

### US-001.15 — Try an update in one place and go back

**As a** Software Engineer, **I want** to try a new version in one repository and return to the previous one, **so that** an update cannot harm all my pipelines at once.

**Acceptance Criteria**

- Given a branch that changes the pinned version in one repository, when its pull request runs, then the result of the new version is visible before any other repository changes.
- Given a failing update, when the pin is set back to the previous exact tag, then the pipeline runs the previous code unchanged.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-007], [MIL-004] | fits one iteration | none |

### US-001.16 — A C++ project gets the same checks

**As a** Software Engineer, **I want** a pull request in a C++ repository to run format and static checks, **so that** a defect is found before review without me writing a pipeline.

**Acceptance Criteria**

- Given a repository that calls the shared C++ quality-check workflow and has C++ files, when a pull request is opened, then the format and static checks run and the status is pass or fail.
- Given a file with a finding, when the check runs, then the job fails and the log shows the tool name with `path:line` and the tool's message.
- Given a repository that lacks what a check needs, when the check runs, then it fails with a `[configuration]` message that names what is missing instead of passing.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-005], [MIL-007] | fits one iteration | none |

### US-001.17 — A C# project gets the same checks

**As a** Software Engineer, **I want** a pull request in a C# repository to run format and analyzer checks, **so that** a defect is found before review without me writing a pipeline.

**Acceptance Criteria**

- Given a repository that calls the shared C# quality-check workflow and has a project or solution, when a pull request is opened, then the format and analyzer checks run and the status is pass or fail.
- Given a file with a finding, when the check runs, then the job fails and the log shows the tool name with `path:line` and the tool's message.
- Given a repository without a project or solution, when the check runs, then it fails with a `[configuration]` message that names what is missing instead of passing.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-005], [MIL-007] | fits one iteration | none |

### US-001.18 — The size of the code is visible as badges

**As a** Software Engineer, **I want** badges that show the number of code files and the number of lines of code without comment and blank lines, **so that** the size of the project is visible in its README without a service outside the instance.

**Acceptance Criteria**

- Given a repository that calls the shared code-metrics workflow, when a change is pushed, then a badge for the code files and a badge for the lines of code show the numbers of that revision.
- Given a file with a comment line, a blank line and a code line, when the lines are counted, then only the code line is counted as a line of code.
- Given a repository without a file of a supported language, when the workflow runs, then it passes with a notice and the badges show zero.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-008], [MIL-010] | fits one iteration | none |

### US-001.19 — The coverage is visible as a badge

**As a** Software Engineer, **I want** a badge that shows how much of the code my tests cover, **so that** a drop in coverage is seen as soon as it is pushed.

**Acceptance Criteria**

- Given a repository that supplies a coverage report, when a change is pushed, then a coverage badge shows the percentage of the report, and its colour follows the thresholds of the contract.
- Given a coverage report that is missing or that cannot be read, when the workflow runs, then it fails with a `[configuration]` message that names the report file and no coverage badge is changed.
- Given a repository that supplies no coverage report, when the workflow runs, then it passes with a notice and publishes no coverage badge.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-008], [MIL-010] | fits one iteration | none |

### US-001.20 — A run with unchanged numbers changes nothing

**As a** Software Engineer, **I want** the workflow to commit nothing when the numbers did not change, **so that** the history of the repository is not filled with badge commits.

**Acceptance Criteria**

- Given a push after which none of the three badges would differ, when the workflow runs, then no commit is made.
- Given a push after which a number changed, when the workflow runs, then one commit changes only the badge files, and the workflow does not start again from that commit.

| Traces to | Size | INVEST exceptions |
| --- | --- | --- |
| [UC-008], [MIL-010] | fits one iteration | none |

## INVEST Check

All twenty stories are independent of each other except that US-001.05 and
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
[MIL-003]: ./milestones/mil-003-quality-checks.md
[MIL-004]: ./milestones/mil-004-versioned-release.md
[MIL-007]: ./milestones/mil-007-cpp-csharp-quality-checks.md
[UC-001]: ./uc-001/uc.md
[UC-002]: ./uc-002/uc.md
[UC-003]: ./uc-003/uc.md
[UC-004]: ./uc-004/uc.md
[UC-005]: ./uc-005/uc.md
[UC-006]: ./uc-006/uc.md
[UC-007]: ./uc-007/uc.md
[UC-008]: ./uc-008/uc.md
[MIL-010]: ./milestones/mil-010-code-metrics-badges.md
[1bc56f8]: https://git.tirsystem.com/TirSystem/github-action/commit/1bc56f8b771531f221f218fc00b147ecc73c051e
[9ca9673]: https://git.tirsystem.com/TirSystem/github-action/commit/9ca9673b00351cf913966f347c4da09890ed3f1f
