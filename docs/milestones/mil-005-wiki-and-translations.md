# MIL-005: Wiki and translations

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-005 |
| CrossReference | [BC-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version | pending |

---

## Purpose

Decide whether a reader can find the workflow documentation on the Gitea wiki
in English, Danish and Bahasa Malaysia, and whether the wiki stays current
because every pull request updates it.

## Deliverable

A Gitea wiki with the pages Home, Onboarding, Credentials, Troubleshooting
and Capabilities in English (authoritative), Danish and Bahasa Malaysia, a
script that builds the wiki pages from `README.md` and `guides/`, and a
pull request rule in `AGENTS.md` that keeps the wiki current.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The wiki is enabled and contains the five pages in all three languages | 15 pages present | Any page missing |
| 2 | Each English page is generated from `README.md` or `guides/`, and a check reports a page that differs from its source | Check passes | Hand-edited page drifts |
| 3 | Each Danish and Bahasa Malaysia page names the English source version it follows | Named on every page | Missing |
| 4 | A native reader of each language has reviewed the translations | Review recorded | Unreviewed |
| 5 | `AGENTS.md` requires a wiki update in every pull request that changes a workflow, a guide or the README, and the PR description lists the pages changed | Rule present and used by one PR | Missing |

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

2026-12-12 — proposed; to be confirmed by S01 and S05.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Decide wiki structure, languages and source of truth | Fix the page list, the page naming for `da` and `ms` (for example `Home`, `Home.da`, `Home.ms`) and that the English wiki pages are generated from `README.md` and `guides/`. Record the wiki languages in the `Languages` section of `docs/artifact-registry.md`, since the registry currently says no translations are kept. | No | |
| 2 | Enable the Gitea wiki and agree access | The wiki is a separate git repository (`github-action.wiki.git`). Enable it on the repository and decide whether the agent pushes to it with a token or prepares changes for review. | No | |
| 3 | Generate the English wiki pages | Add a script that builds the five pages from `README.md` and `guides/`, rewrites links so they work inside the wiki, and reports a page that differs from its source. | No | |
| 4 | Draft the Danish and Bahasa Malaysia pages | Translate each page and name the English source version at the top of the page. Keep technical terms (workflow, secret, runner, mirror) consistent through a small term list. | No | |
| 5 | Have the translations reviewed | A native reader of Danish and of Bahasa Malaysia reviews the drafts and the findings are fixed before publishing. | No | |
| 6 | Add the wiki update rule to the pull request process | Add a rule to `AGENTS.md`: a pull request that changes a workflow, a guide or the README also updates the matching wiki pages in all three languages, and its description lists the pages changed. | No | |
| 7 | Publish and verify | Publish the pages, open them in the browser in each language and check that links, code blocks and the capability table render. | No | |

---

[BC-001]: ../business-case.md
