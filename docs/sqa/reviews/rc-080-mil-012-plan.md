# Review Record: MIL-012 and PP-001 (MIL-012)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-080 |
| CrossReference | [MIL-012], [PP-001], [BC-001], [QC-MIL-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted by the author in chat as stand-in for S01, after three corrections found in the first read | [c5d5941] |

---

## Artifact Under Review

- Instance reviewed: [MIL-012]; delta of [PP-001] for the added milestone
- Checklist used: [QC-MIL-001] for the milestone; for the plan, the criteria of `PP.md` (no QC checklist exists for PP-001)
- Scope: full review of MIL-012; delta re-review of PP-001, earlier record [RC-076]
- Language and domain: n/a (technical type)
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, asked in chat on 2026-10-19 for the acceptance and stands in for S01; the AI prepared the evidence)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | `## Deliverable` names release 2.2.0 with the two composite actions, their guides, README section, wiki pages in three languages, changelog entry and test; a record of one successful job per action; an ADR; and the framework templates pinned to the release tag. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Ten criteria, each with a checkable Go and No-Go: the `uses:` form that resolves, a recorded run per action with the cleanup shown, no secret in any log (a search with a count), verified runner requirements, linting with a seeded error, a search that finds no branch reference, the release level and tags, the framework pull request, the review record. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | [MIL-004] (the Release workflow) and [MIL-011] (`MAJOR_TAG`), [ADR-0006], and the two outside dependencies on S03 (runner, test peers) and on the branch of `TirSystem/sqa-qc-framework`; in the plan's dependency diagram (`MIL-004 + MIL-011 -> MIL-012`). The first read found the operator named S05; the Business Case and the Stakeholder Analysis give runners and secrets to S03, now corrected. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | Objective O6 and success criterion 6 of [BC-001], added in the same change and reviewed in [RC-081]. The first read found the milestone calling O6 "proposed in task 9", which would have left it untraceable until later; now the objective exists and task 9 writes the ADR only. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Owner S05, approving reviewer S01; both are in [SA-001]. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | 2026-11-06, confirmed by S01 in chat on 2026-10-19; the Business Case sets no deadline. The window (2026-10-26 to 2026-11-06) overlaps [MIL-002] and [MIL-003], which are documentation and quality checks and do not use the runner's network; the plan says so. |

## Plan delta (PP-001)

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | Every milestone has a `MIL-*` document and the plan's dates equal that document's target date | Pass | MIL-001 to MIL-012 exist; the MIL-012 decision date (2026-11-06) equals its Target Date. |
| 2 | Every Business Case scope item is covered by a gateway | Pass | The new scope item "Shared composite actions that connect a deployment job to a private network" is covered by [MIL-012] in the scope table. |
| 3 | The schedule respects the Business Case constraints | Pass | No deadline in the Business Case; the window is two weeks. |
| 4 | Dependencies between milestones are stated | Pass | `MIL-004 + MIL-011 -> MIL-012`. |
| 5 | Every gateway has an owner who is a stakeholder ID | Pass | S05. |
| 6 | Plan content is internally consistent | Pass | The first read found a broken link target in the milestone (a wrong ADR-0006 file name and two milestone file names), now checked by resolving every link of the file. The Purpose says "twelve", and the Gantt, the schedule, the scope table and the dependencies agree. |
| 7 | Open Issues are current | Pass | A plan risk is added: the runner cannot give `NET_ADMIN` and `/dev/net/tun`, or `tailscaled` does not survive to the next step, with the mitigation in tasks 2 to 4. |

## Overall Verdict

Go - all criteria pass after three corrections found in the first read (the operator S05 where the Business Case says S03, the objective O6 left as a proposal, and three wrong link targets). The author confirmed the acceptance in chat on 2026-10-19 as stand-in for S01; this is not an independent review.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Confirm this record by S01 when an independent reading is possible | S01 | 2026-11-02 |
| Task 2: ask the operator for the `vpn` runner and the test peers before task 3 starts; nothing in this milestone creates them | S03 | 2026-10-30 |
| The code of both actions, their tests and guides already exist on the unreleased branch `wireguard-vpn-action`; commit it with `Task: MIL-012#N` trailers (tasks 3, 4, 6 and 7 own it) only after the milestone is published as issues | S05 | Before the first commit on that branch |

---

[MIL-012]: ../../milestones/mil-012-vpn-actions-for-deployment.md
[PP-001]: ../../project-plan.md
[BC-001]: ../../business-case.md
[SA-001]: ../../stakeholder-analysis.md
[MIL-002]: ../../milestones/mil-002-onboarding-and-operations.md
[MIL-003]: ../../milestones/mil-003-quality-checks.md
[MIL-004]: ../../milestones/mil-004-versioned-release.md
[MIL-011]: ../../milestones/mil-011-code-metrics-default-tools-ref.md
[ADR-0006]: ../../adr/adr-0006-release-process-and-version-pinning.md
[RC-076]: ./rc-076-mil-011-plan.md
[RC-081]: ./rc-081-bc-001-o6.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[c5d5941]: https://git.tirsystem.com/TirSystem/github-action/commit/c5d59418698316866807388bf61dcb6166d9fa8b
