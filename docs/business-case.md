# Business Case: TirSystem Reusable Workflows

## Metadata
| Key | Value |
| --- | --- |
| ID | BC-001 |
| CrossReference | [SA-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | A mirrored repository has at most one GitHub push mirror; repositories without one are skipped | [0c06789] |
| 2026-10-10 | Proposed | Jens Tirsvad Nielsen | S01 | Scope: wiki pages in English, Danish and Bahasa Malaysia | [08ef26a] |

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

## Scope

### In Scope

- Gitea Actions workflows (and GitHub-compatible syntax where it is the same).
- Documentation for DevOps professionals and software engineers.
- A Gitea wiki with the same documentation in English, Danish and Bahasa Malaysia (MIL-005).
- Validation of workflow files and their documentation.

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

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Gitea scoped workflows behave differently from assumption (feature and version not verified) | Onboarding design is wrong | Verify against the actual instance in MIL-002 before documenting it as supported. |
| Token with excess scope is stored in secrets | Compromise of repositories | Document minimum scope; validate token permissions before use. |
| A breaking change reaches consumers unannounced | Consumer pipelines fail | Version and changelog every release (MIL-004). |
| Security-relevant change accepted without security review | Credential or permission defect reaches production | S05 reviews every change to credentials, tokens, permissions and workflow code. |

## Assumptions

- The Gitea instance has Actions enabled and an `ubuntu-latest` runner with `python3`.
- A mirrored repository has at most one GitHub push mirror. Repositories without a GitHub mirror are skipped successfully.
- S01 (Product Owner) and S05 (DevOps owner and security authority) are both maintainers.

## Constraints

- Workflows use only tools available on the runner; the current workflow uses the Python standard library only.
- Secrets are supplied as repository or organization secrets, never committed.
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
[0c06789]: https://git.tirsystem.com/TirSystem/github-action/commit/0c06789a2779382672712cd483f4964b28a0ebe9
[08ef26a]: https://git.tirsystem.com/TirSystem/github-action/commit/08ef26a6d3eb98c066b45634c2271e578e6c0a0b
