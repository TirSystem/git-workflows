# Project Plan: TirSystem Reusable Workflows

## Metadata
| Key | Value |
| --- | --- |
| ID | PP-001 |
| CrossReference | [BC-001], [SA-001], [MIL-001], [MIL-002], [MIL-003], [MIL-004] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-03 | Rejected | Jens Tirsvad Nielsen | S01 | Initial version<br>Added use case candidates and prioritisation appendix | pending |
| 2026-10-03 | Accepted | Jens Tirsvad Nielsen | S01 | Owner of every gateway is S05<br>Actors updated | pending |

---

## Purpose

This plan schedules four milestones that move the repository from one
workflow with known defects to a documented, versioned collection of shared
workflows. The Business Case sets no deadline, so the dates are proposals.

## Planning Assumptions

- Week 1 starts 2026-10-05; phases are two weeks long; the last decision is 2026-11-28.
- Work on a milestone starts only after its `MIL-*` document is `Accepted`.
- Dates are proposed by the author and need confirmation by S01 and S05.

## Gateway Schedule

| Gateway | Document | Window | Decision date | Owner | Stories | Main deliverable | Milestone |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Stabilise the metadata sync | [MIL-001] | 2026-10-05 to 2026-10-17 | 2026-10-17 | S05 | None yet | Single tested workflow, accurate README | [Milestone MIL-001] |
| Onboarding and operations guide | [MIL-002] | 2026-10-19 to 2026-10-31 | 2026-10-31 | S05 | None yet | Verified onboarding, credential and diagnosis guide | [Milestone MIL-002] |
| Shared quality checks | [MIL-003] | 2026-11-02 to 2026-11-14 | 2026-11-14 | S05 | None yet | Reusable quality-check workflow | [Milestone MIL-003] |
| Versioned release and publishing | [MIL-004] | 2026-11-16 to 2026-11-28 | 2026-11-28 | S05 | None yet | Release process and reusable release workflow | [Milestone MIL-004] |

```plantuml
@startgantt
Project starts 2026-10-05
[MIL-001 Stabilise] starts 2026-10-05 and ends 2026-10-17
[MIL-002 Onboarding] starts 2026-10-19 and ends 2026-10-31
[MIL-003 Quality checks] starts 2026-11-02 and ends 2026-11-14
[MIL-004 Release] starts 2026-11-16 and ends 2026-11-28
[MIL-001 Go/No-Go] happens 2026-10-17
[MIL-002 Go/No-Go] happens 2026-10-31
[MIL-003 Go/No-Go] happens 2026-11-14
[MIL-004 Go/No-Go] happens 2026-11-28
@endgantt
```

## Scope Coverage

| Business Case scope item | Gateway |
| --- | --- |
| Validation of workflow files and their documentation | [MIL-001] |
| Documentation for DevOps professionals | [MIL-002] |
| Gitea Actions workflows for software engineers (quality checks) | [MIL-003] |
| Gitea Actions workflows for software engineers (release and publishing) | [MIL-004] |

## Dependencies

```
MIL-001 → MIL-002 → MIL-003 → MIL-004
```

A No-Go moves every later window by the rework time of the failed milestone.

## Plan Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Reusable workflow support is missing on the instance | MIL-003 and MIL-004 change shape | Verify first in each milestone (MIL-002 task 2, MIL-003 task 1); fall back to copied templates. |
| Security review by S05 is a bottleneck | Milestone decisions slip | Keep milestones small and plan review time before each decision date. |

## Open Issues

- Confirm the proposed dates and the start week (S01 and S05).
- Decide the behavior for an invalid push mirror response (MIL-001 task 1).
- Decide the canonical location of the workflow source (MIL-001 task 3).
- No QC checklist exists for the Project Plan.
- Formal use cases need a use case diagram and user stories first; neither exists yet.

## Appendix: Use Case Candidates and Prioritisation

This appendix evaluates the candidate use cases against the repository as it
is today. It is analysis, not a use case document; formal use cases follow in
MIL-002 task 1. Priority: P1 do first, P2 next, P3 later.

**Recommended order:** (1) Synchronize repository metadata, because it is
the only implemented capability and has a defect, (2) Configure workflow
credentials, (3) Onboard a repository, (4) Diagnose a failed workflow, then
(5) Run project quality checks and (6) Release a reusable workflow. The first
four make the existing workflow dependable and adoptable; the others add new
workflows and only pay off once adoption works.

Current repository state used for the status column: one workflow
(`sync-github-metadata`), one manual probe script (`tests/test_.ps1`), no CI,
no tests, no release process.

| # | Use case | Actor | Priority | Status today |
| --- | --- | --- | --- | --- |
| 1 | Synchronize repository metadata | DevOps professional (S05) | P1 | Implemented in `.gitea/scoped_workflows/`; script has a syntax error |
| 2 | Configure workflow credentials | DevOps professional (S05, S03) | P1 | Partial: secrets are format-checked only |
| 3 | Onboard a repository to standard workflows | DevOps professional (S05) | P1 | Not documented; scoped workflow support unverified |
| 4 | Diagnose a failed workflow | DevOps professional (S05, S03) | P1 | Partial: errors are messages only, uncategorized |
| 5 | Run project quality checks | Software engineer (S02) | P2 | Planned |
| 6 | Release a reusable workflow | DevOps professional (S05) | P2 | Planned |
| 7 | Manage workflow runners | DevOps professional (S03, S05) | P2 | Partial: only `ubuntu-latest` with `python3` assumed |
| 8 | Consume a workflow update | Software engineer (S02) | P2 | Planned; needs versioning |
| 9 | Review workflow results | Software engineer (S02) | P3 | Gitea provides logs; guidance planned |
| 10 | Create a project workflow | Software engineer (S02) | P3 | Planned; needs MIL-003 |
| 11 | Build and publish an artifact | Software engineer (S02) | P3 | Planned; destination undecided |
| 12 | Publish a release | Software engineer (S02) | P3 | Planned; overlaps with use case 6 and 11 |

### UC candidate 1: Synchronize repository metadata (P1)

- **Actor:** DevOps professional. **Goal:** the GitHub mirror shows the Gitea description and topics.
- **Trigger:** push to `main`, manual dispatch, or daily at 03:17 UTC.
- **Preconditions:** both secrets set; exactly one GitHub push mirror configured; runner available.
- **Success:** description and topics on GitHub equal those on Gitea.
- **Main flow:** the workflow validates the secrets, reads description and topics from Gitea, finds the single GitHub mirror, updates the description, replaces the topics.
- **Alternatives and failures:** missing or invalid secret: fail with a message; zero or several GitHub mirrors: fail; non-list mirror response: behavior undecided (MIL-001 task 1); Gitea or GitHub API error: fail with the HTTP code.
- **Dependencies:** none.

### UC candidate 2: Configure workflow credentials (P1)

- **Actor:** DevOps professional. **Goal:** least-privilege tokens that a workflow accepts.
- **Trigger:** onboarding a repository or rotating a token.
- **Preconditions:** access to Gitea and GitHub settings.
- **Success:** a workflow run passes credential checks with the documented minimum permissions.
- **Main flow:** create the tokens, store `TOKEN_FOR_GITEA` and `CREDENTIALS_FOR_GITHUB`, run the workflow, read the validation result.
- **Alternatives and failures:** malformed JSON, empty value, expired token, missing permission: the check names the category without printing the secret.
- **Dependencies:** use case 1.

### UC candidate 3: Onboard a repository to standard workflows (P1)

- **Actor:** DevOps professional. **Goal:** a repository consumes the shared workflows.
- **Trigger:** a new or existing repository needs standard automation.
- **Preconditions:** Actions enabled; runner available; secrets possible to set.
- **Success:** the first run in the repository passes using only the guide.
- **Main flow:** choose scoped or copied delivery, set secrets, configure the push mirror, trigger a run.
- **Alternatives and failures:** scoped workflows unsupported: use a copied template; no runner: see use case 7.
- **Dependencies:** use cases 1 and 2; verification of scoped workflow support.

### UC candidate 4: Diagnose a failed workflow (P1)

- **Actor:** DevOps professional. **Goal:** find the cause of a failed run.
- **Trigger:** a failed or missing run.
- **Preconditions:** access to the run log.
- **Success:** the cause is placed in one category: configuration, credentials, permissions, API response or runner.
- **Main flow:** open the log, read the categorized message, look up the category in the guide, apply the fix, re-run.
- **Alternatives and failures:** no run starts: check runner and trigger; message uncategorized: raise as a defect.
- **Dependencies:** use cases 1 and 2.

### UC candidate 5: Run project quality checks (P2)

- **Actor:** software engineer. **Goal:** tests, lint, format and type checks run on every change.
- **Trigger:** pull request or push.
- **Preconditions:** shared workflow available; project onboarded.
- **Success:** a status check reports pass or fail.
- **Main flow:** the shared workflow detects inputs, runs the checks, reports the result.
- **Alternatives and failures:** a check fails: the log names tool, file and message; unsupported language: workflow fails with a clear message.
- **Dependencies:** use case 3; reusable workflow support.

### UC candidate 6: Release a reusable workflow (P2)

- **Actor:** DevOps professional. **Goal:** a validated, versioned workflow update that consumers can pin.
- **Trigger:** a workflow change is ready.
- **Preconditions:** validation checks exist; version scheme defined.
- **Success:** a tag and changelog entry exist and pinned consumers are unaffected.
- **Main flow:** run validation, update the changelog, tag, announce.
- **Alternatives and failures:** validation fails: no tag; breaking change: new major version.
- **Dependencies:** use case 1 (validation from MIL-001).

### UC candidate 7: Manage workflow runners (P2)

- **Actor:** DevOps professional (runner operator). **Goal:** workflows run on a supported runner.
- **Trigger:** a job waits, fails to start, or a new label is needed.
- **Preconditions:** access to the runner list.
- **Success:** a runner with the required label and tools is online.
- **Main flow:** compare the workflow's `runs-on` label with online runners, check prerequisites such as `python3`, fix or register a runner.
- **Alternatives and failures:** runner offline: restart or replace; label missing: add the label or change the workflow.
- **Dependencies:** use case 3.

### UC candidate 8: Consume a workflow update (P2)

- **Actor:** software engineer. **Goal:** adopt a new workflow version safely.
- **Trigger:** a new release or a changelog notice.
- **Preconditions:** releases are versioned and have a changelog.
- **Success:** the project uses the new version and its pipeline still passes.
- **Main flow:** read the changelog, change the pinned version in one branch, run, merge.
- **Alternatives and failures:** breaking change: follow upgrade notes; failure: roll back to the previous pin.
- **Dependencies:** use case 6.

### UC candidate 9: Review workflow results (P3)

- **Actor:** software engineer. **Goal:** understand a failed check and make it pass.
- **Trigger:** a failed status check on a pull request.
- **Preconditions:** a run exists.
- **Success:** the next run passes.
- **Main flow:** open the check, read the failing step, fix locally, push.
- **Alternatives and failures:** the cause is infrastructure, not code: hand over to use case 4.
- **Dependencies:** use case 5.

### UC candidate 10: Create a project workflow (P3)

- **Actor:** software engineer. **Goal:** compose shared workflows into a project pipeline.
- **Trigger:** a project needs build and delivery steps.
- **Preconditions:** shared workflows are documented with inputs.
- **Success:** the project workflow runs the chosen shared workflows in order.
- **Main flow:** pick workflows, set inputs, set triggers and permissions, test.
- **Alternatives and failures:** missing input: the workflow fails with the input name.
- **Dependencies:** use cases 5 and 8.

### UC candidate 11: Build and publish an artifact (P3)

- **Actor:** software engineer. **Goal:** a package or binary is built and published.
- **Trigger:** a tag or a manual run.
- **Preconditions:** destination decided; token with write access.
- **Success:** the artifact is available at the destination with a version.
- **Main flow:** build, test, package, publish, report the location.
- **Alternatives and failures:** publish denied: permission failure; version exists: fail without overwrite.
- **Dependencies:** use cases 5 and 6; destination decision (MIL-004 task 4).

### UC candidate 12: Publish a release (P3)

- **Actor:** software engineer. **Goal:** a release with validated version and notes.
- **Trigger:** a version tag.
- **Preconditions:** changelog entry exists.
- **Success:** a release page with notes from the changelog.
- **Main flow:** validate the version, build notes, create the release.
- **Alternatives and failures:** invalid version or missing notes: fail. This overlaps with use cases 6 and 11 and should be merged with one of them when the use cases are written.
- **Dependencies:** use cases 6 and 11.

---

[BC-001]: ./business-case.md
[SA-001]: ./stakeholder-analysis.md
[MIL-001]: ./milestones/mil-001-stabilise-metadata-sync.md
[MIL-002]: ./milestones/mil-002-onboarding-and-operations.md
[MIL-003]: ./milestones/mil-003-quality-checks.md
[MIL-004]: ./milestones/mil-004-versioned-release.md
[Milestone MIL-001]: https://git.tirsystem.com/TirSystem/github-action/milestone/18
[Milestone MIL-002]: https://git.tirsystem.com/TirSystem/github-action/milestone/19
[Milestone MIL-003]: https://git.tirsystem.com/TirSystem/github-action/milestone/20
[Milestone MIL-004]: https://git.tirsystem.com/TirSystem/github-action/milestone/21
