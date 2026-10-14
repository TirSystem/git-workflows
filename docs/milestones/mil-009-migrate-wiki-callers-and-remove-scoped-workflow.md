# MIL-009: Migrate the wiki callers and remove the scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-009 |
| CrossReference | [BC-001], [MIL-008], [ADR-0004], [ADR-0006], [ADR-0009] , [RC-066] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | Deprecated | Jens Tirsvad Nielsen | AI as stand-in for S01 | Plan accepted in chat with the defaults: target date 2026-11-30 confirmed, `027-sandbox` and `028-pomodoro` do not publish, framework release 0.7.0; reviewed (RC-064) | [2f267df] |
| 2026-10-14 | Accepted | Jens Tirsvad Nielsen | AI as stand-in for S01 | Verification results recorded for tasks 1 to 8; outcome reviewed (RC-066) | pending |

---

## Purpose

Decide whether the scoped `publish-wiki.yml` can be removed: every repository
that publishes its wiki through it has moved to `docs/wiki/` and calls the
reusable workflow `publish-wiki-pages.yml`, and ADR-0004 is superseded by
ADR-0009. MIL-008 deprecated the scoped workflow and kept it because seven
repositories still depended on it (checked on 2026-10-13).

## Deliverable

A released framework with the caller template; each of the seven repositories
publishing its wiki from `docs/wiki/` through a caller, with its marker removed;
the scoped workflow, its marker code path, its tests and every mention of the
marker as an opt-in removed; ADR-0004 marked superseded; and the major release
2.0.0 with the tag `v2`.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The framework is released as 0.7.0 with `templates/ci/publish-wiki.yml` and `process/wiki.md`, as a tag | The tag exists and each migrating repository pins it | No tag, or a repository pins an unmerged commit |
| 2 | Each of the seven repositories publishes from `docs/wiki/` through a caller of `publish-wiki-pages.yml`, and has no `wiki/.publish` | A scan of the instance lists the seven with a caller and no marker | Any marker or missing caller remains |
| 3 | The wiki of each of the seven equals its `docs/wiki/` after the first run | 0 differences read back through the API for each | A difference, or a failed run |
| 4 | A scan of every repository of the four organisations finds no `wiki/.publish` and no run of the scoped workflow that wrote | None found | Any found |
| 5 | The scoped `publish-wiki.yml`, the marker code path of `tools/publish_wiki.py`, their tests and the marker text of the guides, README and wiki pages are removed | Offline tests pass; a search finds no `wiki/.publish` outside the changelog and ADRs | A mention remains, or a test fails |
| 6 | ADR-0004 is `Superseded by ADR-0009` with a review record, and ADR-0009 links back | Both rows and RC present | Missing |
| 7 | Release 2.0.0 is published with a Breaking entry, `v2` points to it, and `v1` still points to 1.2.2 | Tags read back through the API | `v1` moved, or no Breaking entry |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-008 | Provides the reusable workflow, the deprecation and the list of repositories |
| `TirSystem/sqa-qc-framework` release | The caller template and `process/wiki.md` must be a tag before a repository pins them |

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

2026-11-30 — confirmed on 2026-10-14 by S01 in chat; the Business Case sets no deadline.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Release the framework | `TirSystem/sqa-qc-framework` has the caller template and `process/wiki.md` merged (pull request 45). Add the changelog entry, tag the release and record the tag. Needed before any repository pins the template. | No | |
| 2 | Migrate the three TirSystem projects | `sqa-and-qc`, `sqa-qc-framework` and `sqa-qc-checklists`: move `wiki/` to `docs/wiki/`, copy the caller from `templates/ci/publish-wiki.yml`, remove `wiki/.publish`, fix the paths in their generators and documents, move the framework pin to the released tag, one pull request each. Confirm the organisation secret `TOKEN_FOR_GITEA_WIKI` is present. | No | |
| 3 | Migrate `repo-foundry` | Same steps for `TirSystem-BashScript/repo-foundry` (21 wiki files); the organisation `TirSystem-BashScript` needs its own `TOKEN_FOR_GITEA_WIKI` secret (S03). | No | |
| 4 | Migrate the three Udemy repositories | Same steps for `021-snake-game`, `024-snake` and `025-weather` of `Tirsvad-Udemy-100-days-of-code` (5 wiki files each). `027-sandbox` and `028-pomodoro`, which have `docs/wiki/` and no marker, do not publish (decided by S01 on 2026-10-14). | No | |
| 5 | Verify the migration | After each first run read the wiki back and compare it with `docs/wiki/`; then scan the four organisations for `wiki/.publish` and for repositories still publishing through the scoped workflow. Record the results in this milestone. | No | |
| 6 | Remove the scoped workflow | Delete `.gitea/scoped_workflows/publish-wiki.yml`, the marker path of `tools/publish_wiki.py` (the `WIKI_PRUNE` input becomes required), the tests that cover it and the marker text in the guides, the README and the three wiki languages. Keep the drift test for the remaining scoped workflow. | No | |
| 7 | Supersede ADR-0004 | Mark ADR-0004 `Superseded by ADR-0009` for the delivery and marker parts (new version row, review record), and make ADR-0009 link back. | No | |
| 8 | Release 2.0.0 | Breaking entry (a removed workflow and marker); upgrade guide for callers; release through the release workflow; `v2` is created and `v1` stays at 1.2.2. Move the examples in the guides to `@v2` where the guide describes the new major. | No | |

---

## Verification results

Recorded on 2026-10-14 by the autonomous run.

| # | Criterion | Result |
| --- | --- | --- |
| 1 | The framework is released as 0.7.0 with the template and `process/wiki.md`, and each repository pins it | Go: tag `v0.7.0` on `70fc558`. `sqa-and-qc`, `repo-foundry`, `021-snake-game`, `024-snake` and `025-weather` pin it; `sqa-qc-framework` and `sqa-qc-checklists` have no `framework/` submodule to pin |
| 2 | Each of the seven repositories publishes from `docs/wiki/` through a caller and has no `wiki/.publish` | Go: `sqa-and-qc` #168, `sqa-qc-framework` #47, `sqa-qc-checklists` #17, `repo-foundry` #96, `021-snake-game` #29, `024-snake` #46, `025-weather` #31 |
| 3 | The wiki of each equals its `docs/wiki/` after the first run | Go: 0 differences read back through the API (10, 16, 13, 19, 4, 4 and 4 pages); each first run succeeded |
| 4 | A scan of every repository of the four organisations finds no `wiki/.publish` | Go: 48 repositories scanned, none found |
| 5 | The scoped workflow, the marker path, their tests and the marker text are removed | Go with a note: pull request #151; `wiki/.publish` remains only in the changelog, the ADRs, the milestone and review records and the sentence of the upgrading guide that explains the removal |
| 6 | ADR-0004 is `Superseded by ADR-0009` with a review record, and ADR-0009 links back | Go: RC-065 |
| 7 | Release 2.0.0 is published with a Breaking entry, `v2` points to it, and `v1` still points to 1.2.2 | Go: `v2.0.0` and `v2` on `6e8e548`, `v1` and `v1.2.2` on `9bf0a2b`; the release page shows the Breaking group |

Things that did not go as planned: the three Udemy pull requests were opened through a script that hit a network timeout once and was repeated; the `repo-foundry` test suite fails two tests on `main` and on the branch alike (pre-existing, not caused by this milestone).

---

[BC-001]: ../business-case.md
[RC-066]: ../sqa/reviews/rc-066-mil-009-outcome.md
[MIL-008]: ./mil-008-wiki-reusable-workflow.md
[ADR-0004]: ../adr/adr-0004-shared-wiki-publishing-opt-in.md
[ADR-0009]: ../adr/adr-0009-wiki-publishing-reusable-workflow.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
[2f267df]: https://git.tirsystem.com/TirSystem/github-action/commit/2f267df2a270087cb7dc482af4ce4f4341e97b03
