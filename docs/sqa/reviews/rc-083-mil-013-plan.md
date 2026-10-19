# Review Record: MIL-013 and PP-001 (MIL-013)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-083 |
| CrossReference | [MIL-013], [PP-001], [BC-001], [QC-MIL-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted by the author in chat as stand-in for S01, after one correction found in the first read | pending |

---

## Artifact Under Review

- Instance reviewed: [MIL-013]; delta of [PP-001] for the added milestone
- Checklist used: [QC-MIL-001] for the milestone; for the plan, the criteria of `PP.md` (no QC checklist exists for PP-001)
- Scope: full review of MIL-013; delta re-review of PP-001, earlier record [RC-080]
- Language and domain: n/a (technical type)
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, asked in chat on 2026-10-19 for the acceptance and stands in for S01; the AI prepared the evidence)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | `## Deliverable` names release 2.3.0 with the reusable workflow, its scripts under `tools/`, guide, README section, wiki pages in three languages, changelog entry, offline tests, an ADR for the detection method and a review record, and the two pull requests in the other repositories. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Eleven criteria, each with a checkable Go and No-Go. The first is measurable (a corpus of named size, recall of at least 90 % for Danish and Malay, at most one false positive per 200 English comments); the others are runs, searches or a verified setting. Criterion 7 (the merge is blocked) depends on a setting that only the repository owner makes, and says so. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | [MIL-010] (the comment scanner), [MIL-004] (the Release workflow), [MIL-011] (`MAJOR_TAG`), [ADR-0005]; the outside dependencies (a Gitea token from S03, branch protection by S01 or S03, the framework and checklist repositories) are named. The first read noted that the planned window of [MIL-004] (2026-11-16 to 2026-11-28) starts after this milestone does; [MIL-004] is already released (`v1`, `v2`), so the dependency is met and the plan says nothing wrong. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | Objective O7 and success criterion 7 of [BC-001], added in the same change and reviewed in [RC-084]. The first read found the traceability row still saying O7 was "added at acceptance of this milestone", which is now false; it states the objective plainly. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Owner S05, approving reviewer S01; both are in [SA-001]. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | 2026-11-20, confirmed by S01 in chat on 2026-10-19; the Business Case sets no deadline. The window (2026-11-09 to 2026-11-20) follows [MIL-012] (2026-11-06) and overlaps [MIL-009], which is wiki callers and does not use the check's token or reviewer. |

## Plan delta (PP-001)

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | Every milestone has a `MIL-*` document and the plan's dates equal that document's target date | Pass | MIL-001 to MIL-013 exist; the MIL-013 decision date (2026-11-20) equals its Target Date. |
| 2 | Every Business Case scope item is covered by a gateway | Pass | The new scope item "A shared workflow that checks that comments in source code are in English and tells the author" is covered by [MIL-013] in the scope table. |
| 3 | The schedule respects the Business Case constraints | Pass | No deadline in the Business Case; the window is two weeks. |
| 4 | Dependencies between milestones are stated | Pass | `MIL-004 + MIL-010 + MIL-011 -> MIL-013`. |
| 5 | Every gateway has an owner who is a stakeholder ID | Pass | S05. |
| 6 | Plan content is internally consistent | Pass | The Purpose says "thirteen"; the Gantt, the schedule, the scope table, the dependencies and the planning assumption agree. Unused commit link definitions left by the history roll were removed. |
| 7 | Open Issues are current | Pass | A plan risk is added: the check calls a correct comment non-English or misses a Danish or Malay one, with the mitigation in tasks 1 and 2 and the exception marker. |

## Overall Verdict

Go - all criteria pass after one correction found in the first read (the stale "added at acceptance" wording). The author confirmed the acceptance in chat on 2026-10-19 as stand-in for S01; this is not an independent review.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Confirm this record by S01 when an independent reading is possible | S01 | 2026-11-02 |
| Task 9: decide which repositories mark the check as required and set it; the workflow cannot, and the AI does not change branch protection | S01 | Before task 8 ends |
| Ask the operator for a Gitea token that may comment on pull requests, stored as an organization secret, before task 8 | S03 | 2026-11-13 |

---

[MIL-013]: ../../milestones/mil-013-english-comments-check.md
[PP-001]: ../../project-plan.md
[BC-001]: ../../business-case.md
[SA-001]: ../../stakeholder-analysis.md
[MIL-004]: ../../milestones/mil-004-versioned-release.md
[MIL-009]: ../../milestones/mil-009-migrate-wiki-callers-and-remove-scoped-workflow.md
[MIL-010]: ../../milestones/mil-010-code-metrics-badges.md
[MIL-011]: ../../milestones/mil-011-code-metrics-default-tools-ref.md
[MIL-012]: ../../milestones/mil-012-vpn-actions-for-deployment.md
[ADR-0005]: ../../adr/adr-0005-quality-check-contract.md
[RC-080]: ./rc-080-mil-012-plan.md
[RC-084]: ./rc-084-bc-001-o7.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
