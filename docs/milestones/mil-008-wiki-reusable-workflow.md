# MIL-008: Wiki publishing as a reusable workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-008 |
| CrossReference | [BC-001], [MIL-006], [ADR-0004], [RC-060], [RC-061] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-13 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version; reviewed (RC-060) | pending |
| 2026-10-13 | Accepted | Jens Tirsvad Nielsen | S01 | Task 5 changed to deprecate the scoped workflow (8 repositories still use it); reviewed (RC-061) | pending |

---

## Purpose

Decide whether the wiki can be published by a reusable workflow that each
repository calls, from `docs/wiki/` (the location `process/wiki.md` of the
framework prescribes), instead of a scoped workflow that runs in every
repository of the organisation and reads `wiki/`.

## Deliverable

A reusable workflow `publish-wiki-pages.yml` in `.gitea/workflows/` with a
`wiki_dir` input, a caller template for projects, offline tests, a superseding
ADR, updated guides and wiki pages, this repository publishing its own wiki
from `docs/wiki/` through it, the scoped workflow marked deprecated (not
removed), and a release that projects can pin.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The reusable workflow publishes the folder named by `wiki_dir` (default `docs/wiki`), and a repository that has no caller workflow is never written to | Offline tests pass; no caller means no run | Any write without a caller |
| 2 | An empty or missing folder never deletes pages, the failure names its category, and the secret is passed explicitly (criteria 1 and 4 of MIL-006 still hold) | Existing tests pass unchanged | A regression |
| 3 | This repository publishes its own wiki from `docs/wiki/` through a caller that uses the reusable workflow, and the pages on the host equal the folder | 0 differences read back through the API | Pages differ or the run fails |
| 4 | A caller template exists for projects, with the trigger `docs/wiki/**` and the secret named | File exists and is linted (QC-WF-001) | Missing |
| 5 | The scoped `publish-wiki.yml` is marked deprecated in its header, the README and ADR-0009, and the repositories that still use it are listed; it is not removed here | Notice present and the list recorded (8 repositories on 2026-10-13) | No notice, or the workflow was removed while a repository still depends on it |
| 6 | The change is released as patch 1.2.2 and the moving major tag points at it | `v1` includes the change | Not released |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-006 | The publisher script, the prune rule and the safety limits come from it |
| `TirSystem/sqa-qc-framework` `process/wiki.md` | Defines `docs/wiki/` and the English plus PO language minimum; unmerged when this was written |

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

2026-11-15 — the Business Case sets no deadline.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Record the decision | An ADR that supersedes the scoped-delivery part of ADR-0004: publishing is a reusable workflow called by each repository; the caller file is the opt-in, so `wiki/.publish` is no longer a gate; the `prune` setting becomes an input. Keep the rest of ADR-0004 (secret handling) as it stands. | No | |
| 2 | Add the reusable workflow | `.gitea/workflows/publish-wiki-pages.yml` with `on: workflow_call`, inputs `wiki_dir` (default `docs/wiki`) and `prune`, and the token as a declared secret. It runs `tools/publish_wiki.py` with `WIKI_DIR` and the prune setting from the inputs. Update the script and its tests: the marker is no longer required. | No | |
| 3 | Add the caller template | A `publish-wiki.yml` caller for projects (`uses: TirSystem/github-action/.gitea/workflows/publish-wiki-pages.yml@v1`, `paths: docs/wiki/**`, `secrets:` mapped). Proposed in `sqa-qc-framework` under `templates/ci/` once this is released. | No | |
| 4 | Move this repository's wiki and call the workflow | `git mv wiki docs/wiki`, check the links and the translation hash comments, add the caller, publish, read the pages back. | No | |
| 5 | Deprecate the scoped workflow | Do not remove it: on 2026-10-13, 8 repositories still publish through it with `wiki/.publish` (`sqa-and-qc`, `sqa-qc-framework`, `sqa-qc-checklists`, `github-action`, `repo-foundry` and three of `Tirsvad-Udemy-100-days-of-code`), and none calls the reusable workflow yet. Add a deprecation notice to its header, the README table and ADR-0009, and record the list. The migrations and the removal are a follow-up milestone after this release (ADR-0006: a removed workflow is a new major). | No | |
| 6 | Update guides and wiki pages | Describe the caller, `docs/wiki/` and the removed marker in the onboarding and credentials guides and in the English, Danish and Bahasa Malaysia pages (rule 8 of `AGENTS.md`). | No | |
| 7 | Release | Release as a patch, 1.2.1 to 1.2.2, as the owner instructed: changelog entry and a release through the release workflow; the `v1` tag moves with it. ADR-0006 classes a new workflow as minor, so the changelog entry states the deviation and the reason. Nothing is removed, so no consumer breaks. | No | |

---

[BC-001]: ../business-case.md
[MIL-006]: ./mil-006-shared-wiki-publishing.md
[ADR-0004]: ../adr/adr-0004-shared-wiki-publishing-opt-in.md
[RC-060]: ../sqa/reviews/rc-060-mil-008-plan.md
[RC-061]: ../sqa/reviews/rc-061-mil-008-task-5-deferred.md
