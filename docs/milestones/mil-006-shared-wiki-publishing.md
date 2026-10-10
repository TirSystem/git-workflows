# MIL-006: Shared wiki publishing

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-006 |
| CrossReference | [BC-001], [MIL-005], [ADR-0003] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | [6b8e36d] |

---

## Purpose

Decide whether any repository on the instance can publish its own wiki from a
`wiki/` folder through one shared workflow, without a copy of the workflow and
without risk to repositories that did not ask for it.

## Deliverable

A scoped workflow `publish-wiki.yml` in `.gitea/scoped_workflows/` with its
publish script embedded, an opt-in rule that leaves every repository without
it untouched, offline tests, updated guides and wiki pages, and one
repository other than this one that publishes its wiki through it.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | A repository without the opt-in marker is never written to, shown by offline tests and by a run in one such repository | No request writes to its wiki | Any write |
| 2 | The workflow exists once: the copy in `.gitea/workflows/` is removed and no script is needed from `tools/` | Count is 1 | A second copy exists |
| 3 | One repository outside this one publishes its wiki through the shared workflow | Pages on the wiki equal its `wiki/` | Pages differ or run fails |
| 4 | An empty or missing `wiki/` never deletes pages, and a failure names its category | Verified by tests | A wiki was emptied |
| 5 | The per-organisation secret `TOKEN_FOR_GITEA_WIKI` is documented, and stored in the pilot's organisation | Documented and stored | Missing |
| 6 | The onboarding and credentials guides and their three wiki languages describe opting in | Pages updated | Out of date |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-005 | The publisher, the page layout and the wiki rules come from it |
| MIL-002 | Scoped delivery across organisations was verified there (issue #9) |

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

2026-12-26 — proposed; to be confirmed by S01 and S05 (the Business Case sets no deadline).

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Decide the opt-in rule and the secret handling | A scoped workflow runs in every repository of an organisation, and the publisher deletes pages that are not in `wiki/`. Choose how a repository opts in (a marker file such as `wiki/.publish`, a repository variable, or an allow list), what happens when the secret is missing, and whether the pilot uses `TOKEN_FOR_GITEA_WIKI` or the fallback. Record it as an ADR that refines ADR-0003. | No | |
| 2 | Make the publisher a scoped workflow | Embed the publish script in `.gitea/scoped_workflows/publish-wiki.yml` as the metadata sync does, so it needs nothing from `tools/` in the target repository, and run it only on a change under `wiki/`. Remove `.gitea/workflows/publish-wiki.yml` and `tools/publish_wiki.py` so the workflow has one source, and keep this repository's drift check in the validation tests. | No | |
| 3 | Implement the opt-in gate and the safety limits | Skip, successfully and with a log line, any repository that has not opted in. Keep the refusal on an empty `wiki/` and the categorised errors, and add offline tests with a fake Gitea for opted-in, not opted-in and missing-secret runs. | No | |
| 4 | Pilot in one other repository | Choose one repository outside this one, add a `wiki/` folder with the marker, store `TOKEN_FOR_GITEA_WIKI` in its organisation (S03), publish, and read the pages back. Also confirm that a repository without the marker was not touched. | No | |
| 5 | Update the guides and the wiki | Describe how a repository opts in and which secrets its organisation needs in the onboarding and credentials guides, regenerate the wiki pages and update the Danish and Bahasa Malaysia translations (rule 8 of `AGENTS.md`). | No | |

---

[BC-001]: ../business-case.md
[6b8e36d]: https://git.tirsystem.com/TirSystem/github-action/commit/6b8e36d67ac9af165b180bc0045289e41cfd1fc3
