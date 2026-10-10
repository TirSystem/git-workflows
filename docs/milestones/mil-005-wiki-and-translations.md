# MIL-005: Wiki and translations

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-005 |
| CrossReference | [BC-001], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Deprecated | Jens Tirsvad Nielsen | S01 | Decided how the wiki is published: source in `wiki/`, published by a workflow on merge<br>Added task 8 | [77c5277] |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Target date 2026-12-12 confirmed on 2026-10-10 by S01 (stand-in for S05) | [ea06eaa] |

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
| 4 | A native reader of each language has reviewed the translations | Review recorded | Unreviewed |
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

---

[BC-001]: ../business-case.md
[77c5277]: https://git.tirsystem.com/TirSystem/github-action/commit/77c52779c46bca35dee4d73e587ca7b611373790
[ADR-0002]: ../adr/adr-0002-s01-approves-as-stand-in.md
[ea06eaa]: https://git.tirsystem.com/TirSystem/github-action/commit/ea06eaaa698247d20e4a8e2694d7acbb1de58b63
