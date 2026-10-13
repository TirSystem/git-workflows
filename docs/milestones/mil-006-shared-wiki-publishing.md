# MIL-006: Shared wiki publishing

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-006 |
| CrossReference | [BC-001], [MIL-005], [ADR-0003], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-11 | Deprecated | Jens Tirsvad Nielsen | S01 | Criterion 1 evidence amended; added the verification results of the pilot | [d575f27] |
| 2026-10-13 | Accepted | Jens Tirsvad Nielsen | AI as stand-in for S01 | Task 6 added and reviewed (RC-058): the publisher sends page titles with spaces, so a hyphenated page (`Home-da`) is stored as `Home-da.md` and its links resolve | pending |

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
| 1 | A repository without the opt-in marker is never written to, shown by offline tests and by the trigger rule (a run in such a repository cannot be started: a scoped workflow is not dispatchable through the API and runs only on a push that changes `wiki/**`) | No request writes to its wiki | Any write |
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

2026-12-26 — confirmed on 2026-10-10 by S01, standing in for S05 (ADR-0002); the Business Case sets no deadline.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Decide the opt-in rule and the secret handling | A scoped workflow runs in every repository of an organisation, and the publisher deletes pages that are not in `wiki/`. Choose how a repository opts in (a marker file such as `wiki/.publish`, a repository variable, or an allow list), what happens when the secret is missing, and whether the pilot uses `TOKEN_FOR_GITEA_WIKI` or the fallback. Record it as an ADR that refines ADR-0003. | No | |
| 2 | Make the publisher a scoped workflow | Embed the publish script in `.gitea/scoped_workflows/publish-wiki.yml` as the metadata sync does, so it needs nothing from `tools/` in the target repository, and run it only on a change under `wiki/`. Remove `.gitea/workflows/publish-wiki.yml` and `tools/publish_wiki.py` so the workflow has one source, and keep this repository's drift check in the validation tests. | No | |
| 3 | Implement the opt-in gate and the safety limits | Skip, successfully and with a log line, any repository that has not opted in. Keep the refusal on an empty `wiki/` and the categorised errors, and add offline tests with a fake Gitea for opted-in, not opted-in and missing-secret runs. | No | |
| 4 | Pilot in one other repository | Choose one repository outside this one, add a `wiki/` folder with the marker, store `TOKEN_FOR_GITEA_WIKI` in its organisation (S03), publish, and read the pages back. Also confirm that a repository without the marker was not touched. | No | |
| 5 | Update the guides and the wiki | Describe how a repository opts in and which secrets its organisation needs in the onboarding and credentials guides, regenerate the wiki pages and update the Danish and Bahasa Malaysia translations (rule 8 of `AGENTS.md`). | No | |
| 6 | Fix the page title of hyphenated pages | Gitea keeps a hyphen in a title literal, so the publisher created `Home-da` as `Home-da.-.md`, addressed `Home%2Dda`, and every link to `Home-da` led to the page list (found on the `sqa-and-qc`, `sqa-qc-framework` and `sqa-qc-checklists` wikis). Send the title with spaces (`Home da`, stored `Home-da.md`), cover it with a test and a changelog entry. The stale `*.-.md` pages are deleted after the release, by hand. | No | |

## Verification results

The pilot was `TirSystem/sqa-qc-checklists` (its PR 10, merged 2026-10-11).
The scoped workflow ran as run 629 on `d4ddbb6`, fetched the scripts at `v1`,
passed the token preflight and reported `Published 13 page(s): 0 created,
0 updated, 0 deleted`. The 13 pages of the wiki were then read back through
the API and equal `wiki/*.md` on `main` (0 differences).

| # | Criterion | Result |
| --- | --- | --- |
| 1 | A repository without the marker is never written to | Go by the offline tests (`test_a_repository_without_the_marker_is_never_written_to`: no request, the existing page unchanged; `..._does_not_need_the_secret`; `..._without_a_wiki_directory_is_skipped`) and by the trigger rule. A live run was tried on 2026-10-11 in `TirSystem/IaC.server-setup-4-linux`: the API answered 404, the workflow is not listed for that repository and cannot be dispatched. S01 accepted the weaker evidence on 2026-10-11 (RC-049) |
| 2 | The workflow exists once | Go: only `.gitea/scoped_workflows/publish-wiki.yml`; no copy in `.gitea/workflows/` and nothing is needed from `tools/` in the target repository (the script is fetched from `TirSystem/github-action`, MIL-004 task 6) |
| 3 | One repository outside this one publishes its wiki | Go: `TirSystem/sqa-qc-checklists`, run 629, 13 pages equal |
| 4 | An empty or missing `wiki/` never deletes pages; a failure names its category | Go: `test_an_empty_source_never_deletes_pages_even_with_prune` and the category tests |
| 5 | `TOKEN_FOR_GITEA_WIKI` is documented and stored in the pilot's organisation | Go: `guides/credentials.md`; run 629 used the organisation secret |
| 6 | The onboarding and credentials guides and their wiki languages describe opting in | Go: `wiki/.publish` and `TOKEN_FOR_GITEA_WIKI` appear in the guides and the English, Danish and Bahasa Malaysia pages |

---

[BC-001]: ../business-case.md
[ADR-0002]: ../adr/adr-0002-s01-approves-as-stand-in.md
[ea06eaa]: https://git.tirsystem.com/TirSystem/github-action/commit/ea06eaaa698247d20e4a8e2694d7acbb1de58b63
[d575f27]: https://git.tirsystem.com/TirSystem/github-action/commit/d575f272fcb044e3165951013464177a6e659ea6
