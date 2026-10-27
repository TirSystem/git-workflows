# MIL-014: Publish wiki pages as a scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-014 |
| CrossReference | [BC-001], [MIL-009], [ADR-0004], [ADR-0009], [ADR-0013], [RC-086] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; Accepted on a Go review (RC-086); accepted by the author in chat on 2026-10-27 as stand-in for S01, not independent | pending |

---

## Purpose

Decide whether wiki publishing returns to a scoped workflow: the instance runs
`publish-wiki-pages.yml` in every repository of the organizations, and a
repository opts in by having a `docs/wiki/` folder. MIL-008 and MIL-009 replaced
the scoped workflow by a reusable one that each of seven repositories calls; the
owner now wants the call and the caller file gone, because the folder
`docs/wiki/` is already the convention of the framework and a caller file adds
nothing a repository decides. This reverses part of [ADR-0009].

## Deliverable

The scoped workflow `.gitea/scoped_workflows/publish-wiki-pages.yml` (already
written in the working tree, with its tests and the guides, README and wiki
pages in three languages); the reusable workflow and this repository's own
caller removed; [ADR-0013] accepted and [ADR-0009] marked superseded; the seven
repositories that call the reusable workflow have dropped their caller; the
framework template `templates/ci/publish-wiki.yml` retired in the framework
repository; and the major release 3.0.0 with the tag `v3`.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The scoped workflow runs in a repository with `docs/wiki/` and ends without publishing in one without | A run in this repository publishes; a run in a test repository without the folder succeeds and logs that there is nothing to publish | Either run fails, or the second one writes a wiki |
| 2 | The wiki of this repository equals `docs/wiki/` after the first run, and pages that are only in the wiki are kept | 0 differences read back through the API for the pages in the folder | A difference, or a deleted page |
| 3 | The organization secret `TOKEN_FOR_GITEA_WIKI` is available to the scoped run in each organization that has a repository with `docs/wiki/` | A scan lists each such organization with the secret present | A repository with the folder and no secret that is not named as an accepted failure |
| 4 | A scan of the four organizations lists every repository with `docs/wiki/` that has no wiki enabled, or where the first run would write unwanted pages (for example `027-sandbox` and `028-pomodoro`, which MIL-009 decided must not publish) | Each such repository is named and resolved (wiki disabled, folder renamed or owner accepts publishing) before the release | A repository would publish that its owner did not accept |
| 5 | The reusable workflow, this repository's caller, and every mention of calling it are removed; the tests, README, guides and the three wiki languages describe the scoped workflow | Offline tests pass and `python tools/build_wiki.py --check` is clean | A mention remains, or a test fails |
| 6 | [ADR-0013] is `Accepted` with a review record, [ADR-0009] is `Superseded by ADR-0013` with a review record, and [ADR-0013] links back | Both rows and the `RC-*` records present | Missing |
| 7 | The seven repositories no longer call `publish-wiki-pages.yml`, and each wiki still equals its `docs/wiki/` after the first scoped run | 0 differences for each, and no caller workflow found by the scan | A caller remains, or a difference |
| 8 | The framework has retired `templates/ci/publish-wiki.yml` and `process/wiki.md` describes the scoped workflow, released as a tag that this project pins | The tag exists and this project pins it | The pin is an unmerged commit |
| 9 | Release 3.0.0 is published with a Breaking entry, `v3` points to it, and `v2` still points to the last 2.x release | Tags read back through the API | `v2` moved, or no Breaking entry |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-009 | Removed the first scoped workflow, migrated the seven callers and set the list of repositories this milestone migrates back |
| MIL-013 | Release 2.3.0 comes first, so the 3.0.0 release carries one breaking change and nothing else |
| `TirSystem/sqa-qc-framework` release | `process/wiki.md` and the CI template must be a tag before a repository pins them |

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

2026-11-27 — proposed after MIL-013 (2026-11-20); the Business Case sets no deadline, and S01 confirms the date when accepting the plan.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Record the decision | Write [ADR-0013] (wiki publishing as a scoped workflow, with the opt-in, the fixed settings and the security consequence of a token that every repository of an organization can reach) and review it. Mark [ADR-0009] `Superseded by ADR-0013` for the delivery and caller parts, with a review record, once [ADR-0013] is accepted. | No | [ADR-0013] |
| 2 | Check the instance | Verify on this Gitea instance that a scoped workflow with a `paths:` filter fires only on a push that changes `docs/wiki/**`, that the organization secret reaches a scoped run, how the file in `.gitea/scoped_workflows/` reaches the instance (S03), and list every repository of the four organizations that has `docs/wiki/`, its wiki setting and whether its owner wants it published (`027-sandbox` and `028-pomodoro` did not in MIL-009). | No | |
| 3 | Make the repository change | Review the working-tree change (scoped workflow, removed reusable workflow and caller, `tools/publish_wiki.py` message, tests, fixtures, README, guides, wiki pages in three languages) and merge it; confirm the first run on `main` publishes and a repository without the folder is skipped. | No | |
| 4 | Move the framework | In `TirSystem/sqa-qc-framework` retire `templates/ci/publish-wiki.yml`, rewrite `process/wiki.md` and the install guide for the scoped workflow, add the changelog entry and tag the release; then this project moves the submodule pin to the tag. | No | |
| 5 | Remove the callers | In each of `sqa-and-qc`, `sqa-qc-framework`, `sqa-qc-checklists`, `repo-foundry`, `021-snake-game`, `024-snake` and `025-weather`: delete the caller workflow (it would publish twice), keep `docs/wiki/`, one pull request each. Do this only after task 3 is merged and released, so no repository is left without publishing. | No | |
| 6 | Verify the migration | After each first scoped run read the wiki back and compare it with `docs/wiki/`; scan the four organizations for callers of `publish-wiki-pages.yml` and for repositories whose wiki would be written without their owner's agreement. Record the results in this milestone. | No | |
| 7 | Release 3.0.0 | Breaking entry (a removed reusable workflow and its inputs); upgrade guide for callers: remove the call and rely on the scoped workflow; release through the release workflow; `v3` is created and `v2` stays at the last 2.x release, so a caller still pinned at `@v2` keeps working. Move the examples in the guides to `@v3` where they describe the new major. | No | |

---

[BC-001]: ../business-case.md
[MIL-009]: ./mil-009-migrate-wiki-callers-and-remove-scoped-workflow.md
[ADR-0004]: ../adr/adr-0004-shared-wiki-publishing-opt-in.md
[ADR-0009]: ../adr/adr-0009-wiki-publishing-reusable-workflow.md
[ADR-0013]: ../adr/adr-0013-wiki-publishing-scoped-workflow.md
[RC-086]: ../sqa/reviews/rc-086-adr-0013-mil-014-pp-001.md
