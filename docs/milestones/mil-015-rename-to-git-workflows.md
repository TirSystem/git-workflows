# MIL-015: Rename the repository references to git-workflows

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-015 |
| CrossReference | [BC-001], [MIL-014], [ADR-0006], [RC-087] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted on a Go review (RC-087); accepted by the author in chat on 2026-10-27 as stand-in for S01, not independent | [851b24c] |

---

## Purpose

Decide whether every place that names the repository `TirSystem/github-action`
now names `TirSystem/git-workflows`, which is its name on the instance. The old
name is in 369 places outside the `framework/` submodule (checked on 2026-10-27:
41 in code and configuration, 128 in user documentation, 184 in milestones, ADRs,
review records and the plan, and 16 in the Business Case, the use cases and the
user stories). Two things follow from it today: the workflows that fetch their
scripts name a repository that may now exist only through a redirect (task 2 checks it), and the branch
protection of `main` requires a check named `TirSystem/github-action: Sync
GitHub mirror metadata / sync-metadata (push)`, which no run of
`TirSystem/git-workflows` can produce, so a pull request cannot satisfy it.

## Deliverable

Code, configuration and user documentation that name `TirSystem/git-workflows`
(`repository:` and `uses:` lines, the wiki source URL, the tests, `AGENTS.md`,
README, guides and the wiki pages in three languages); the history (milestones,
ADRs, review records, changelog) left as written, with the rename recorded once
in the Project Plan; a branch protection whose required checks can be produced;
the repositories that call a workflow of this repository pointing at the new
name; and a release that carries the change.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | A search of code and configuration (`.gitea/`, `actions/`, `tools/`, `tests/`, `AGENTS.md`) finds `TirSystem/github-action` only in the changelog | Search result lists none outside `CHANGELOG.md` and the unrelated `tailscale/github-action` | A match remains |
| 2 | A search of README, `guides/` and `docs/wiki/` finds the old name only where a sentence explains the rename | Offline tests pass and `python tools/build_wiki.py --check` is clean | A match remains, or a test fails |
| 3 | The history is unchanged | `git diff` of `docs/milestones/`, `docs/adr/` and `docs/sqa/reviews/` against `main` shows only the files of this milestone | A past milestone, ADR or review record is rewritten |
| 4 | The old name still resolves for `uses:`, `repository:` and the tags `v1` and `v2` on this instance, or the release is major | A workflow that calls `TirSystem/github-action/...@v2` and one that checks it out succeed in a test repository | Either fails and the release is not major |
| 5 | The required checks of `main` can be produced by a pull request | The pull request of this milestone shows every required check as passed or not required | A required check name that no run produces |
| 6 | Every repository of the four organizations that calls a workflow of this repository, or checks it out, names the new repository | A scan lists none with the old name | Any remains, or a run fails after its change |
| 7 | The GitHub push mirror and the description and topics sync still work | The next run of **Sync GitHub mirror metadata** succeeds and the GitHub repository shows the same description and topics | A run fails |
| 8 | The release is published with a changelog entry that names the rename | Tag and release page read back through the API | No entry, or `v1` or `v2` moved |

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
| 1 | Rename in code and configuration | Replace `TirSystem/github-action` in the workflows that fetch their scripts, `tools/build_wiki.py`, the tests, the comment fixtures and `AGENTS.md`, and rebuild the wiki pages that depend on the source URL. Leave `tailscale/github-action`, a different repository. Done in the working tree and tested (674 tests pass); it needs this milestone accepted to be committed. | No | |
| 2 | Check the old name on the instance | In a test repository run a workflow that calls `TirSystem/github-action/.gitea/workflows/...@v2` and one that checks the repository out at `v2`, and record whether the redirect holds; check the GitHub push mirror and the metadata sync. The result decides the version of the release (criterion 4). | No | |
| 3 | Fix the required checks | Ask S01 or S03 to remove the required check `TirSystem/github-action: Sync GitHub mirror metadata / sync-metadata (push)` from the protection of `main` (it runs only on a push to `main`, so a pull request never produces it); the AI does not change branch protection. | No | |
| 4 | Rename in user documentation | Replace the old name in README, the guides and the wiki pages in three languages (128 places) and mention the rename once in the Project Plan; leave milestones, ADRs, review records and the changelog as written, and list the Business Case, Stakeholder Analysis, use cases, use case diagram and user stories (16 places) for S01 to decide, because they name the project as it was. Start after the pull request of MIL-014 has merged. | No | |
| 5 | Update the callers | Scan the four organizations for `uses: TirSystem/github-action/` and `repository: TirSystem/github-action`, and change each in a pull request per repository; include the framework (`sqa-qc-framework`, its `AGENTS.md` table and templates), which is released first. | No | |
| 6 | Verify | After the changes read back: the searches of criteria 1 and 2, the first run of every changed caller, the next metadata sync. Record the results in this milestone. | No | |
| 7 | Release | Changelog entry that names the rename; version as decided in task 2; release through the release workflow; the moving major tags are unchanged. | No | |

---

[BC-001]: ../business-case.md
[MIL-014]: ./mil-014-wiki-publishing-scoped-again.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
[RC-087]: ../sqa/reviews/rc-087-mil-015.md
[851b24c]: https://git.tirsystem.com/TirSystem/git-workflows/commit/851b24c63a8cd8a054cb380c1396a20de0686161
