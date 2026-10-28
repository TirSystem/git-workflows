# MIL-018: Release any repository with a scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-018 |
| CrossReference | [BC-001], [MIL-014], [MIL-017], [ADR-0005], [ADR-0006], [ADR-0007], [ADR-0013], [RC-092], [US-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; reviewed (RC-092), accepted by the author in chat on 2026-10-29 as stand-in for S01, not independent | [1690cf7] |

---

## Purpose

Decide whether the release of a repository becomes a **scoped** workflow, so
that the same workflow releases any repository of the TirSystem organizations
when someone starts it there, and whether the token it needs is described and
named `TOKEN_FOR_GITEA_RELEASE`. Today `release.yml` releases this repository
only; the framework repository makes its tag and release page by hand. The
scoped workflow checks that the commit is the tip of the default branch, that
the validation of MIL-017 is green and that the changelog has an entry for the
version, then makes the tag and the release page. This replaces `release.yml`
and reverses the part of ADR-0007 that lets the run use its own token: a scoped
workflow runs in repositories where that token cannot write tags.

## Deliverable

The scoped workflow `.gitea/scoped_workflows/release.yml`; `tools/release.py`
made general (the default branch from the API, both changelog formats, the
major tag only from 1.0, the validation status of MIL-017); an ADR (the token,
the formats, the tags, what is checked); the description of
`TOKEN_FOR_GITEA_RELEASE` in `guides/credentials.md` (scope, where it is
stored, who approves it, rotation), in `guides/release-process.md`, the README,
the wiki pages in three languages, `.env.example` and the changelog; the old
`.gitea/workflows/release.yml` removed; offline tests; a dry run in three
repositories; and the next major release of this repository made with the new
workflow.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The workflow is started by hand in any repository with a version and `dry_run`, and a dry run writes nothing | A dry run in this repository and in two others prints what it would do and creates no tag and no release page | A dry run changes anything |
| 2 | The secret `TOKEN_FOR_GITEA_RELEASE` is required, with no fallback to the token of the run or to another secret | A run without it ends with a configuration error that names the secret; with it the run creates the tag and the page | A fallback token is used |
| 3 | The token is described: scope, where it is stored, who approves it, how it is rotated, and which calls the workflow makes | `guides/credentials.md` has the section, and the calls listed are the calls in the script, checked by a test | The section is missing or differs from the script |
| 4 | The workflow refuses a commit that is not the tip of the default branch, a missing or red `Validate / validate (push)` status, a changelog without an entry for the version, and a tag that exists | One test per refusal passes with the message of the category | A refusal does not happen |
| 5 | Both changelog formats are read: `## [1.2.0] - date` and `## 0.18.0 (date)` | Fixtures of this repository and of the framework repository give the right notes | Either format fails |
| 6 | The major tag `vN` moves only from version 1.0 and only for the highest version of its major | Tests for 0.x (no major tag), the first 1.x and a lower patch of an older major | A 0.x release makes a major tag, or an older release moves it |
| 7 | The tag and the release page are made with the notes of the changelog entry, and read back through the API | A release in a test repository shows the tag, the page and the notes | They differ from the entry |
| 8 | The workflow writes no secret to the log and has the permissions it needs and no more | `permissions: contents: read` in the file, the token only in the environment of the one step, never in a command line | The token appears in a log or an argument |
| 9 | The old `release.yml` is gone and the documents say so | The file is removed; `guides/release-process.md`, ADR-0006 and ADR-0007 name the new workflow and what it supersedes | A document still sends the reader to `release.yml` |
| 10 | The offline tests pass and `python tools/build_wiki.py --check` is clean | Both succeed | A test fails or a page is stale |
| 11 | The release of this repository is made with the new workflow, and a dry run is recorded for `sqa-qc-framework` and `sqa-and-qc` | The release page is read back through the API, and the two dry runs are in this milestone | The release is made by hand |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-017 | The release requires the status `Validate / validate (push)` in every repository |
| MIL-014 | The delivery of scoped workflows and their start by hand |
| ADR-0006 | The versioning rules (exact tags never move, the major tag follows the highest) that this workflow applies |
| ADR-0007 | The release page is the only destination; this milestone changes which token makes it |
| Business Case objective O4 | Shared quality-check and release workflows; S01 confirms that a scoped workflow serves it |

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

2026-12-30 — proposed by the author; the Business Case sets no deadline. The window (2026-12-21 to 2026-12-30) follows MIL-017 (2026-12-18) and ends before MIL-007 (2027-01-04). S01 confirmed the date, which is after the plan's last decision date 2026-12-26, in chat on 2026-10-29 (RC-092).

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Verify that a scoped release can write a tag and a page | In a test repository start a scoped workflow by hand, once with the token of the run and once with a token stored as `TOKEN_FOR_GITEA_RELEASE`, and record which of them can create a tag, a release page and move a tag. The ADR rests on the result. | No | [ADR-0007] |
| 2 | Decide the contract (ADR) | Write the ADR: the secret is required, no fallback, its scope and who approves and stores it (S05 and S03, as for the wiki token), the two changelog formats, the major tag from 1.0, the status that is required, what the workflow refuses and what it writes. Mark ADR-0006 and ADR-0007 as amended. | No | [ADR-0006] |
| 3 | Make the script general and extend the tests | `tools/release.py`: the default branch from the repository API, the status name as a setting with the default of MIL-017, both changelog formats, the major tag rule; offline tests for every row of the criteria. | No | |
| 4 | Write the scoped workflow and remove the old one | `.gitea/scoped_workflows/release.yml` with the inputs `version` and `dry_run` (default `true`); remove `.gitea/workflows/release.yml`; keep the concurrency group. | No | |
| 5 | Describe `TOKEN_FOR_GITEA_RELEASE` | The section in `guides/credentials.md` (content, scope `write:repository` for a dedicated user, organization secret, rotation, the calls made), the change in `guides/release-process.md`, `.env.example`, the README, the wiki pages in three languages and the changelog entry under Breaking (the old workflow is removed and the secret is now required). | No | |
| 6 | Run the dry runs | Dry runs in this repository, `sqa-qc-framework` and `sqa-and-qc`; record the output, and fix what the framework repository's changelog needs. | No | |
| 7 | Release | Release this repository as the next major with the new workflow; read the tag, the page and the major tag back through the API. | No | |

---

[BC-001]: ../business-case.md
[US-001]: ../user-stories.md
[MIL-014]: ./mil-014-wiki-publishing-scoped-again.md
[MIL-017]: ./mil-017-scoped-validation-workflow.md
[ADR-0005]: ../adr/adr-0005-quality-check-contract.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
[ADR-0007]: ../adr/adr-0007-release-publish-destination.md
[ADR-0013]: ../adr/adr-0013-wiki-publishing-scoped-workflow.md
[RC-092]: ../sqa/reviews/rc-092-mil-018-pp-001.md
[1690cf7]: https://git.tirsystem.com/TirSystem/git-workflows/commit/1690cf749c4ffb5e0a0174fe50fceb060b6e3f1c
