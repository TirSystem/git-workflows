# MIL-019: Publish accepted milestones with a scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-019 |
| CrossReference | [BC-001], [MIL-014], [MIL-015], [ADR-0013], [RC-096] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version; not reviewed yet | [0693426] |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Reviewed (RC-096); accepted by the author in chat on 2026-10-29 as stand-in for S01, not independent | [0693426] |

---

## Purpose

Decide whether the workflow that publishes accepted milestones as Milestones and
Issues on Gitea becomes a **scoped** workflow, delivered by the instance to every
repository that keeps `docs/milestones/`, so that no repository copies
`sync-milestones.yml` and none has to update its copy. Today this repository and
`sqa-and-qc` each carry a copy (with the checkout and token defect that
[MIL-015] task 9 and the framework template showed), and every other project that
installs the workflow would add one more. The wiki publishing took the same step
in [MIL-014]: the folder is the opt-in, and the secrets belong to the
organization. The decision also settles where the milestone scripts come from: a
private framework submodule of the project, or a pinned release that the workflow
fetches itself.

## Deliverable

The scoped workflow `.gitea/scoped_workflows/sync-milestones.yml` that publishes
the accepted milestones of the repository it runs in; an ADR (the opt-in, where
the scripts come from, the secrets, the dry run, what is never done); offline
tests; the guide `guides/sync-milestones.md`, the README section, the wiki pages
in three languages and the changelog entry; the copy in this repository removed
and the copies in the other repositories found and removed; and a minor release.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The workflow runs in a repository with `docs/milestones/` and no caller or copy | A run in this repository (copy removed) and one in a test repository without `.gitea/` both publish the accepted milestones | It needs a file in the repository |
| 2 | A repository without `docs/milestones/` ends green without doing anything | A run in such a repository prints that there is nothing to publish | It fails or calls the API |
| 3 | The scripts of a published release are used, and the choice is recorded | The ADR names the source; the log of a run prints the tag it used | The scripts come from an unpinned branch |
| 4 | The secrets are organization secrets with no fallback to older names | `TOKEN_FOR_GITEA_ISSUES` publishes and `TOKEN_FOR_GITEA_REPO` reads the framework; a run without one fails with a message that names it | An older secret name is read, or a token is printed |
| 5 | A push publishes, a manual run is a dry run unless switched off | A manual run with `dry_run` on prints the plan and creates nothing; a push to the default branch that changes `docs/milestones/**` or `docs/sqa/reviews/**` publishes only milestones that are Accepted with a Go review | A Proposed milestone is published, or a dry run writes |
| 6 | Nothing is closed or deleted | A test with a milestone removed from the folder leaves its issues untouched | An issue or milestone is closed or deleted |
| 7 | The copies are gone and the first run of every repository is read back | A scan of the organizations finds no `sync-milestones.yml` copy; each repository's first scoped run is green and its milestones and issues equal the accepted documents | A copy remains or a run fails |
| 8 | The offline tests pass and `python tools/build_wiki.py --check` is clean | Both succeed | A test fails or a page is stale |
| 9 | The release is published with a changelog entry that names the workflow and the removed copies | Tag and release page read back through the API | No entry, or a moved major tag |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-014 | The scoped delivery, the folder as the opt-in and the organization secret were verified there |
| MIL-015 | The secrets are named `TOKEN_FOR_<host>_<purpose>`, and task 9 of that milestone fixed the test helper that this milestone's tests use |
| ADR-0013 | The same decision for the wiki: a scoped workflow that runs everywhere and acts where the folder exists |
| Business Case objective O4 | Shared workflows, versioned; S01 confirms that a scoped workflow serves it, as for the wiki |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O4 (shared quality-check and release workflows, versioned) | [BC-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2027-02-12 — proposed by the author; the Business Case sets no deadline. The window (2027-02-01 to 2027-02-12) follows MIL-010 (2027-01-30), because MIL-007 and MIL-010 fill January and a single owner works one milestone at a time. S01 confirms the date when accepting the plan, or moves it ahead of MIL-016.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Verify what a scoped run can read | In a test repository run a scoped workflow that reads the organization secrets `TOKEN_FOR_GITEA_ISSUES` and `TOKEN_FOR_GITEA_REPO`, checks out the private framework and filters on `docs/milestones/**`; record what works, and list the repositories of the four organizations that have `docs/milestones/` or a `sync-milestones.yml` copy. | No | [MIL-014] |
| 2 | Decide the contract (ADR) | Write the ADR: the folder as the opt-in; where the scripts come from (the project's submodule or a pinned framework release fetched by the workflow, with the tag printed); the secrets without fallback; the dry run; the guarantee that nothing is closed or deleted. | No | [ADR-0013] |
| 3 | Write the workflow and its tests | `.gitea/scoped_workflows/sync-milestones.yml` and, where logic is needed, a script in `tools/`; offline tests for the nothing-to-publish, dry-run and missing-secret cases. | No | |
| 4 | Document it | `guides/sync-milestones.md`, the README section and table, the wiki pages in three languages, the changelog entry; the framework's wording about the workflow is updated in its repository. | No | |
| 5 | Remove the copies | Remove `.gitea/workflows/sync-milestones.yml` here and, in a pull request per repository, in `sqa-and-qc` and every other repository found in task 1; read back each first scoped run. | No | |
| 6 | Release | Release as the next minor (Added, and Removed for the copy) through the release workflow; the moving major tag moves with it. | No | |

---

[BC-001]: ../business-case.md
[MIL-014]: ./mil-014-wiki-publishing-scoped-again.md
[MIL-015]: ./mil-015-rename-to-git-workflows.md
[ADR-0013]: ../adr/adr-0013-wiki-publishing-scoped-workflow.md
[RC-096]: ../sqa/reviews/rc-096-mil-019-pp-001.md
[0693426]: https://git.tirsystem.com/TirSystem/git-workflows/commit/06934262e96d8874c8ebfcc55682ebf99e7cbac8
