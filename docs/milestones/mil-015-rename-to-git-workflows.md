# MIL-015: Rename the repository references to git-workflows

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-015 |
| CrossReference | [BC-001], [MIL-014], [ADR-0006], [RC-087], [RC-088], [RC-093] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | Deprecated | Jens Tirsvad Nielsen | S01 | Updated to pull request 218 (live files renamed) and the removed required check: purpose, deliverable, criterion 5 and tasks 1, 3 and 4; reviewed (RC-088), accepted by the author in chat as stand-in for S01, not independent | [081a17d] |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Added criterion 9 and task 8: the Gitea secrets follow `TOKEN_FOR_<host>_<purpose>`; reviewed (RC-093), accepted by the author in chat on 2026-10-29 as stand-in for S01, not independent | pending |

---

## Purpose

Decide whether every place that names the repository `TirSystem/github-action`
now names `TirSystem/git-workflows`, which is its name on the instance. When this
milestone was accepted the old name was in 369 places outside the `framework/`
submodule. Since then pull request 218 (merged on 2026-10-27) renamed the live
files (code, configuration, README, guides and wiki pages), and the required
status check of `main` that carried the old name is gone: the protection of
`main` now has status checks switched off (read back through the API on
2026-10-27). What is left (checked on 2026-10-27): 194 places in milestones,
ADRs, review records and the plan, 16 in the Business Case, the use cases and the
user stories, and four mentions of `tailscale/github-action` and the changelog,
which are not the old name of this repository. What also remains is the
repositories that call a workflow here, whether the old name still resolves, and
a release.

## Deliverable

Code, configuration and user documentation that name `TirSystem/git-workflows`
(done by this milestone's task 1 and by pull request 218); the history
(milestones, ADRs, review records, changelog) left as written, with the rename
recorded once in the Project Plan; a branch protection whose required checks can
be produced (status checks are off today); the repositories that call a workflow
of this repository pointing at the new name; and a release that carries the
change.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | A search of code and configuration (`.gitea/`, `actions/`, `tools/`, `tests/`, `AGENTS.md`) finds `TirSystem/github-action` only in the changelog | Search result lists none outside `CHANGELOG.md` and the unrelated `tailscale/github-action` | A match remains |
| 2 | A search of README, `guides/` and `docs/wiki/` finds the old name only where a sentence explains the rename | Offline tests pass and `python tools/build_wiki.py --check` is clean | A match remains, or a test fails |
| 3 | The history is unchanged | `git diff` of `docs/milestones/`, `docs/adr/` and `docs/sqa/reviews/` against `main` shows only the files of this milestone | A past milestone, ADR or review record is rewritten |
| 4 | The old name still resolves for `uses:`, `repository:` and the tags `v1` and `v2` on this instance, or the release is major | A workflow that calls `TirSystem/github-action/...@v2` and one that checks it out succeed in a test repository | Either fails and the release is not major |
| 5 | The required checks of `main` can be produced by a pull request | Status checks are off, or every required context is produced by a run of this repository, read back through the API | A required context that no run produces |
| 6 | Every repository of the four organizations that calls a workflow of this repository, or checks it out, names the new repository | A scan lists none with the old name | Any remains, or a run fails after its change |
| 7 | The GitHub push mirror and the description and topics sync still work | The next run of **Sync GitHub mirror metadata** succeeds and the GitHub repository shows the same description and topics | A run fails |
| 8 | The release is published with a changelog entry that names the rename | Tag and release page read back through the API | No entry, or `v1` or `v2` moved |
| 9 | The Gitea secrets follow `TOKEN_FOR_<host>_<purpose>` in the workflows, the scripts, the guides and the wiki pages | A search of `.gitea/`, `tools/`, `tests/`, `guides/`, `docs/wiki/` and `README.md` finds the bare name `TOKEN_FOR_GITEA` only in the changelog; `sync-github-metadata.yml` reads `TOKEN_FOR_GITEA_REPO` and `sync-milestones.yml` reads `TOKEN_FOR_GITEA_ISSUES`; the offline tests pass and `python tools/build_wiki.py --check` is clean | A workflow or guide still names `TOKEN_FOR_GITEA`, or a test fails |

## Dependencies

| Depends on | Reason |
| --- | --- |
| Pull request of MIL-014 (not the milestone) | It changes the same README, guides and wiki pages; the documentation task follows its merge so the two do not conflict. MIL-015 is decided before MIL-014 and does not depend on its decision |
| ADR-0006 | Decides the version of the release: a rename that keeps the old name working is a patch; one that does not is a major |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O2, O4 | [BC-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-11-06 — proposed by the author: the branch protection blocks pull requests now, and the change is small; the Business Case sets no deadline. S01 confirms the date when accepting the plan.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Rename in code and configuration | Done. Replaced `TirSystem/github-action` in the workflows that fetch their scripts, `tools/build_wiki.py`, the tests, the comment fixtures and `AGENTS.md`, and rebuilt the wiki pages that depend on the source URL; `tailscale/github-action`, a different repository, is untouched. Pull request 218 made the same change in the live files at the same time; the merge into the branch resolved to one result (674 tests pass, wiki check clean). | No | |
| 2 | Check the old name on the instance | In a test repository run a workflow that calls `TirSystem/github-action/.gitea/workflows/...@v2` and one that checks the repository out at `v2`, and record whether the redirect holds; check the GitHub push mirror and the metadata sync. The result decides the version of the release (criterion 4). | No | |
| 3 | Fix the required checks | Done by S01 or S03: the required check `TirSystem/github-action: Sync GitHub mirror metadata / sync-metadata (push)` is gone; on 2026-10-27 the protection of `main` showed status checks off (`enable_status_check` false, no contexts). The AI did not change branch protection. What remains is a decision: switch status checks back on with only `Validate workflows / validate (pull_request)`, so the offline tests gate the merge again. | No | |
| 4 | Record the rename and the rest of the documents | Mention the rename once in the Project Plan (done in the planning assumption) and list the Business Case, Stakeholder Analysis, use cases, use case diagram and user stories (16 places) for S01 to decide, because they name the project as it was. README, guides and the wiki pages were renamed by pull request 218 and need nothing more. Milestones, ADRs, review records and the changelog stay as written. | No | |
| 5 | Update the callers | Scan the four organizations for `uses: TirSystem/github-action/` and `repository: TirSystem/github-action`, and change each in a pull request per repository; include the framework (`sqa-qc-framework`, its `AGENTS.md` table and templates), which is released first. | No | |
| 6 | Verify | After the changes read back: the searches of criteria 1 and 2, the first run of every changed caller, the next metadata sync. Record the results in this milestone. | No | |
| 7 | Release | Changelog entry that names the rename; version as decided in task 2; release through the release workflow; the moving major tags are unchanged. | No | |
| 8 | Name the Gitea secrets | Rename `TOKEN_FOR_GITEA` to `TOKEN_FOR_GITEA_REPO` (metadata sync) and `TOKEN_FOR_GITEA_ISSUES` (milestone sync) in the two workflows, `tools/sync_github_metadata.py`, its tests and fixtures, the guides, the wiki pages in three languages, `.env.example`, `AGENTS.md` and the README; add a Breaking entry to the changelog (store the new secrets in each organization before the release); move the framework pin to v0.18.0, which names the same secrets. Do this before the release of task 7. | No | [BC-001] |

---

[BC-001]: ../business-case.md
[MIL-014]: ./mil-014-wiki-publishing-scoped-again.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
[RC-087]: ../sqa/reviews/rc-087-mil-015.md
[RC-088]: ../sqa/reviews/rc-088-mil-015-update.md
[RC-093]: ../sqa/reviews/rc-093-mil-015-task-8.md
[081a17d]: https://git.tirsystem.com/TirSystem/git-workflows/commit/081a17d07f4c7d7145cdc50984c669dfb798b48d
