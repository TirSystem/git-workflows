# Business Case: TirSystem Reusable Workflows

## Metadata
| Key | Value |
| --- | --- |
| ID | BC-001 |
| CrossReference | [SA-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-28 | Accepted | Jens Tirsvad Nielsen | S01 | Objective O8, scope item, assumption, constraint and success criterion 8: a free static security scan with Semgrep as a scoped workflow (MIL-016); reviewed (RC-089), accepted by the author in chat as stand-in for S01 | [1690cf7] |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Risk for objective O8 (false positives, data leaving the instance); O8 reviewed against QC-BC-001 (RC-089), accepted by the author in chat as stand-in for S01, not independent | pending |

---

## Executive Summary

TirSystem repositories are hosted on a self-hosted Gitea instance and
push-mirrored to GitHub. Automation that every repository needs is currently
copied by hand. This project turns this repository into the single, reviewed
collection of reusable Gitea Actions workflows for DevOps professionals and
software engineers. Today it contains one workflow, which copies repository
description and topics from Gitea to the GitHub mirror. The proposal is to
harden that workflow first, document how repositories adopt it, and then add
shared quality-check and release workflows in priority order.

## Methodological and Standards Foundation

Documents follow the SQA and QC framework in `framework/` (use cases after
Larman, *Applying UML and Patterns*). Quality criteria are tagged with
ISO/IEC 25010:2023 characteristics. The domain language is English (IT).

## Problem Statement

- The only workflow exists as three diverging copies (`src/`,
  `.gitea/scoped_workflows/`, and others), and the scoped copy
  currently contains a Python syntax error (`exit 0`).
- There is no automated check of workflow files, so defects such as that one
  are found only when the workflow runs.
- There is no documented way to onboard a repository, set up credentials,
  choose runners or diagnose a failed run.
- Quality checks and release steps are not shared, so each project would
  reinvent them.

## Business Opportunity

A small, versioned, documented workflow collection lets every TirSystem
repository adopt the same secure automation in minutes, and lets a fix be
made once.

## Objectives

- **O1:** Keep the existing metadata sync correct, tested and documented as
  the single implemented capability.
- **O2:** Provide one canonical copy of each workflow with a defined way to
  reach consuming repositories (scoped workflow or copy).
- **O3:** Document and validate credentials, runner labels and failure
  diagnosis for every workflow.
- **O4:** Offer shared quality-check and release workflows, versioned so
  consumers can adopt changes deliberately.
- **O5:** Offer a shared workflow that counts the code files and the lines of
  code (without comment and blank lines) of a repository, reads its coverage
  report and publishes the three results as SVG badges.
- **O6:** Offer shared, versioned actions that bring a VPN (WireGuard or
  Tailscale) up for a deployment job on a Gitea runner, so the job can reach a
  private network.
- **O7:** Offer a shared workflow that checks that the comments in the source
  code of a pull request are written in English, blocks the pull request when
  they are not, and tells its author which comment and why.
- **O8:** Offer a free static security scan, as a scoped workflow, that finds known
  insecure patterns in the source code of a pull request with community rules
  and shows them to its author.

## Scope

### In Scope

- Gitea Actions workflows (and GitHub-compatible syntax where it is the same).
- Documentation for DevOps professionals and software engineers.
- A Gitea wiki with the same documentation in English, Danish and Bahasa Malaysia (MIL-005).
- Validation of workflow files and their documentation.
- A shared workflow for code metrics and coverage badges (MIL-010).
- Shared composite actions that connect a deployment job to a private network through WireGuard or Tailscale (MIL-012).
- A shared workflow that checks that comments in source code are in English and tells the author (MIL-013).
- A free static security scan with Semgrep Community Edition as a scoped workflow (MIL-016).

### Out of Scope

- Operating the Gitea instance or runners themselves.
- Application code of consuming repositories.
- Features not backed by an accepted milestone task.
- Behavior that is only proposed: documentation describes implemented
  workflows only; planned ones are marked as planned.

## Expected Benefits

### Tangible Benefits

- One fix reaches all consuming repositories.
- Fewer failed runs caused by missing or over-broad credentials.
- Less time to onboard a repository.

### Intangible Benefits

- Consistent, reviewable automation across TirSystem projects.
- Higher trust in automation that touches credentials.

## Strategic Alignment

Supports TirSystem's practice of a self-hosted primary repository with
public GitHub mirrors, and its SQA framework requirement that code follows
accepted plans.

## Success Criteria

| # | Criterion | Target | Measure |
| --- | --- | --- | --- |
| 1 | Workflow files that fail static validation | 0 on the default branch | Result of the validation task in MIL-001 |
| 2 | Canonical copies per workflow | 1 | Count of files per workflow name |
| 3 | Documented use cases that are implemented or marked planned | 100% | README capability table against workflows present |
| 4 | Repositories consuming a shared workflow | At least 1 besides this one by MIL-002 | Consumer list in README |
| 5 | Repositories that show the code metrics and coverage badges from the shared workflow | At least 1 besides this one by MIL-010 | README of the consuming repository |
| 6 | VPN actions that connect a deployment job on the instance, with no secret in the run log | 2 (WireGuard and Tailscale) by MIL-012 | Recorded runs of MIL-012 tasks 3 to 5 |
| 7 | Comments in source code that are not in English and reach the default branch of a repository that calls the check | 0 after MIL-013 | The check's run on the default branch; a throwaway pull request with a finding that cannot be merged |
| 8 | Findings of the blocking severity that reach the default branch of a repository with scanned source files | 0 after MIL-016 | The scan's run on the default branch; a throwaway pull request with a planted finding that cannot be merged |

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Gitea scoped workflows behave differently from assumption (feature and version not verified) | Onboarding design is wrong | Verify against the actual instance in MIL-002 before documenting it as supported. |
| Token with excess scope is stored in secrets | Compromise of repositories | Document minimum scope; validate token permissions before use. |
| A breaking change reaches consumers unannounced | Consumer pipelines fail | Version and changelog every release (MIL-004). |
| Security-relevant change accepted without security review | Credential or permission defect reaches production | S05 reviews every change to credentials, tokens, permissions and workflow code. |
| The static security scan blocks a pull request on a false positive, or the scan sends source code or usage data out of the instance (O8) | Work is blocked for no reason, or code leaves the organization | Metrics off and no login (MIL-016 task 2); the licences read before building (task 3); a documented way to silence a finding and a count of false positives in the trial (tasks 6 and 7). |

## Assumptions

- The Gitea instance has Actions enabled and an `ubuntu-latest` runner with `python3`.
- A mirrored repository has at most one GitHub push mirror. Repositories without a GitHub mirror are skipped successfully.
- S01 (Product Owner) and S05 (DevOps owner and security authority) are both maintainers.
- For the VPN actions (MIL-012), S03 provides a runner whose container has the capability `NET_ADMIN` and the device `/dev/net/tun`, and the test peers; the actions do not configure the runner.
- For the English-comments check (MIL-013), S03 provides a Gitea token that may comment on pull requests, as an organization secret, and S01 or S03 decide which repositories mark the check as required; the workflow does not change branch protection.
- For the security scan (MIL-016), the runner has `python3` and `pip` and can reach the Python package index and the rule registry of Semgrep; MIL-016 task 2 verifies it before anything is built.

## Constraints

- Workflows use only tools available on the runner; the current workflow uses the Python standard library only.
- Secrets are supplied as repository or organization secrets, never committed.
- A VPN key or token never appears in a log, an artifact or a command line (MIL-012).
- The English-comments check (MIL-013) runs without sending source text to a service outside the instance, and its token never appears in a log.
- The security scan (MIL-016) runs without a login, with metrics off, and does not send source code to a service outside the instance; MIL-016 task 2 verifies it, and the licences of the engine and the rules are read from their sources before the scan is built (MIL-016 task 3).
- Nothing is written under `src/` or `tests/` before the matching milestone is accepted.

## Cost–Benefit Assessment

| Costs | Benefits |
| --- | --- |
| Maintainer time for planning, documentation and tests (qualitative; no external cost) | Avoided duplication and fewer credential and configuration failures across repositories |

## Stakeholders

| Stakeholder ID (SA) | Interest in this project |
| --- | --- |
| S01 | Owns scope, accepts the documents and co-maintains the workflows |
| S02 | Consumes shared workflows |
| S03 | Operates runners and secrets |
| S05 | Co-maintains the workflows and reviews their security |
| S04 | Sees mirror metadata |

## Recommendation

Proceed — the first milestone fixes a known defect in the only existing workflow and the later ones add value only after it is accepted.

---

[SA-001]: ./stakeholder-analysis.md
[1690cf7]: https://git.tirsystem.com/TirSystem/git-workflows/commit/1690cf749c4ffb5e0a0174fe50fceb060b6e3f1c
