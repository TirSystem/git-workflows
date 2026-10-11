# MIL-005: Wiki and translations

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-005 |
| CrossReference | [BC-001], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Deprecated | Jens Tirsvad Nielsen | S01 | Target date 2026-12-12 confirmed on 2026-10-10 by S01 (stand-in for S05) | [ea06eaa] |
| 2026-10-11 | Accepted | Jens Tirsvad Nielsen | S01 | Criterion 4 amended (accepted by S01 as stand-in when no native reader exists); added the verification results | pending |

---

## Purpose

Decide whether a reader can find the workflow documentation on the Gitea wiki
in English, Danish and Bahasa Malaysia, and whether the wiki stays current
because every pull request updates it.

## Deliverable

A Gitea wiki with the pages Home, Onboarding, Credentials, Troubleshooting
and Capabilities in English (authoritative), Danish and Bahasa Malaysia. The
page source lives in `wiki/` in this repository and is reviewed through pull
requests. A script builds the English pages from `README.md` and `guides/`,
a workflow publishes `wiki/` to the wiki repository when a change is merged
to `main`, and a pull request rule in `AGENTS.md` keeps the wiki current.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The wiki is enabled and contains the five pages in all three languages | 15 pages present | Any page missing |
| 2 | Each English page is generated from `README.md` or `guides/`, and a check reports a page that differs from its source | Check passes | Hand-edited page drifts |
| 3 | Each Danish and Bahasa Malaysia page names the English source version it follows | Named on every page | Missing |
| 4 | The translations are reviewed and accepted: by a native reader of each language, or, when none is available, by S01 as the stand-in of ADR-0002, with the lack of a native reader stated | Acceptance recorded, and a native review where one exists | Unreviewed |
| 5 | `AGENTS.md` requires a wiki update in every pull request that changes a workflow, a guide or the README, and the PR description lists the pages changed | Rule present and used by one PR | Missing |
| 6 | The wiki is published only by the workflow from `main`; no agent or person pushes to the wiki repository by hand | Last wiki commit is by the workflow | A manual push exists |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-002 | The wiki pages are built from the onboarding, credentials and troubleshooting guides |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O3 | [BC-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-12-12 — confirmed on 2026-10-10 by S01, standing in for S05 (ADR-0002); the Business Case sets no deadline.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Decide wiki structure, languages and source of truth | Fix the page list, the page naming for `da` and `ms` (for example `Home`, `Home.da`, `Home.ms`) and that the English wiki pages are generated from `README.md` and `guides/`. Record the wiki languages in the `Languages` section of `docs/artifact-registry.md`, since the registry currently says no translations are kept. | No | |
| 2 | Enable the Gitea wiki and agree access | Decision (2026-10-10): the page source lives in `wiki/` in this repository and reaches the wiki repository (`github-action.wiki.git`) only through a workflow that runs on merge to `main`; the agent edits `wiki/` on a branch and opens a pull request and never pushes to the wiki repository. This task enables the wiki on the repository and creates a secret that can write to the wiki repository only, approved by S05 and stored by S03. Edits made in the Gitea web UI are overwritten on the next publish, and the wiki home page says so. | No | |
| 3 | Generate the English wiki pages | Add a script that builds the five pages into `wiki/` from `README.md` and `guides/`, rewrites links so they work inside the wiki, and reports a page that differs from its source. | No | |
| 4 | Draft the Danish and Bahasa Malaysia pages | Translate each page and name the English source version at the top of the page. Keep technical terms (workflow, secret, runner, mirror) consistent through a small term list. | No | |
| 5 | Have the translations reviewed | A native reader of Danish and of Bahasa Malaysia reviews the drafts and the findings are fixed before publishing. | No | |
| 6 | Add the wiki update rule to the pull request process | Add a rule to `AGENTS.md`: a pull request that changes a workflow, a guide or the README also updates the matching wiki pages in all three languages, and its description lists the pages changed. | No | |
| 7 | Publish and verify | Publish the pages, open them in the browser in each language and check that links, code blocks and the capability table render. | No | |
| 8 | Add the wiki publishing workflow | Add a Gitea workflow, canonical in `.gitea/scoped_workflows/`, that runs on push to `main` when `wiki/` changes and copies `wiki/` to the wiki repository with the secret from task 2. It needs least-privilege permissions, must not print the secret, and gets offline tests like the metadata sync, with the same categorized error messages. | No | |

## Verification results

Checked on 2026-10-11 against `main` at the merge of PR 83.

| # | Criterion | Result |
| --- | --- | --- |
| 1 | The wiki is enabled and contains the pages in all three languages | Go: 21 pages (seven pages in English, Danish and Bahasa Malaysia), more than the 15 the criterion names |
| 2 | Each English page is generated from `README.md` or `guides/`, and a check reports a page that differs | Go: `python tools/build_wiki.py --check` passes and the tests fail on a stale page |
| 3 | Each translation names the English source version it follows | Go: every `.da` and `.ms` file starts with `translation of X.md, source sha256`, and the tests check it |
| 4 | The translations are reviewed and accepted | Go on the stand-in: no native reader of Danish or Bahasa Malaysia reviewed the pages. S01 accepted them on 2026-10-11 (RC-050) and the checklist `docs/wiki-translation-review.md` stays available for a native reader. The accuracy of the text rests on the author and S01, not on a native reader |
| 5 | `AGENTS.md` requires a wiki update and the PR lists the pages | Go: rule 8 of `AGENTS.md`; used by PR 78, PR 82 and others, each listing the wiki pages it changed |
| 6 | The wiki is published only by the workflow from `main` | Go: the last commit of all 21 pages has the message `Publish wiki from the repository`, which only the publisher writes |

---

[BC-001]: ../business-case.md
[ADR-0002]: ../adr/adr-0002-s01-approves-as-stand-in.md
[ea06eaa]: https://git.tirsystem.com/TirSystem/github-action/commit/ea06eaaa698247d20e4a8e2694d7acbb1de58b63
