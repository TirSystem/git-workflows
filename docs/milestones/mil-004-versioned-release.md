# MIL-004: Versioned release and publishing

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-004 |
| CrossReference | [BC-001], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-03 | Deprecated | Jens Tirsvad Nielsen | S01 | Owner is S05 (security authority); S01 remains approving reviewer | [4de5438] |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Target date 2026-11-28 confirmed on 2026-10-10 by S01 (stand-in for S05) | [ea06eaa] |

---

## Purpose

Decide whether workflow updates can be released with a version and adopted
safely, and whether a project can publish an artifact through a shared
workflow.

## Deliverable

A documented release process for this repository (validation, version tag,
changelog), a consumer upgrade guide and a reusable release workflow.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | A release is validated by the MIL-001 checks before a tag is created | Enforced | Tag possible without checks |
| 2 | Each release has a version tag and a changelog entry that marks breaking changes | Present | Missing |
| 3 | A consumer pinned to the previous version keeps working after a release | Verified | Breaks |
| 4 | The publish destination (release page or package registry) is decided and its token scope documented | Decided | Open |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-003 | Reuses the reusable workflow mechanism |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O4 | [BC-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-11-28 — confirmed on 2026-10-10 by S01, standing in for S05 (ADR-0002); the Business Case sets no deadline.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Define the release process for this repository | Describe how a workflow change is validated, tagged and announced, and how consumers pin a version. | Yes | Use case candidate: release a reusable workflow |
| 2 | Add a changelog and tag convention | Create `CHANGELOG.md` and a tag scheme (for example `v1` plus `v1.2.3`) that separates breaking from compatible changes. | No | |
| 3 | Write the consumer upgrade guide | Explain how to read a changelog entry, test an update in one repository and roll back. | Yes | Use case candidate: consume a workflow update |
| 4 | Decide the publish destination | Choose the release or package destination for built artifacts and document the token scope it needs. | No | |
| 5 | Implement the reusable release workflow | Validate the version, build release notes from the changelog and publish to the chosen destination. | Yes | Use case candidate: publish a release |

---

[BC-001]: ../business-case.md
[4de5438]: https://git.tirsystem.com/TirSystem/github-action/commit/4de5438a88b4bbf18b165f52f797d1a52af89f6d
[ADR-0002]: ../adr/adr-0002-s01-approves-as-stand-in.md
[ea06eaa]: https://git.tirsystem.com/TirSystem/github-action/commit/ea06eaaa698247d20e4a8e2694d7acbb1de58b63
