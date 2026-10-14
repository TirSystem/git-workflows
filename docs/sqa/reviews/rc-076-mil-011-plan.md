# Review Record: MIL-011 and PP-001 (MIL-011)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-076 |
| CrossReference | [MIL-011], [PP-001], [BC-001], [QC-MIL-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted by the author in chat as stand-in for S01, after three corrections found in the first read | pending |

---

## Artifact Under Review

- Instance reviewed: [MIL-011]; delta of [PP-001] for the added milestone
- Checklist used: [QC-MIL-001] for the milestone; for the plan, the criteria of `PP.md` (no QC checklist exists for PP-001)
- Scope: full review of MIL-011; delta re-review of PP-001, earlier record [RC-068]
- Language and domain: n/a (technical type)
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, asked in chat on 2026-10-14 for the review and the acceptance and stands in for S01; the AI prepared the evidence)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | `## Deliverable` names the patch release 2.1.1: the defaults, the test, the guides, README and three wiki languages at `@v2`, the changelog entry, and the framework `Badges` page without the workaround. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Eight criteria, each with a checkable Go and No-Go: reproduction, a list per workflow, a test that fails on a seeded default, a search that finds no `@v1`, a run on the instance, the release level and tags, the framework page, the review record. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | [MIL-010] (the workflow and its guide) and [ADR-0006] (the release process); in the plan's dependency diagram (`MIL-010 -> MIL-011`). |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | O5 of [BC-001]; the first read found its wording paraphrased wrongly, now quoted from the Business Case. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Owner S05, approving reviewer S01; both are in [SA-001]. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | 2026-10-23; the Business Case sets no deadline. The date precedes the planned decision date of [MIL-010] (2027-01-30) because that milestone was released on 2026-10-14; the milestone says so and does not change the MIL-010 row. |

## Plan delta (PP-001)

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | Every milestone has a `MIL-*` document and the plan's dates equal that document's target date | Pass | MIL-001 to MIL-011 exist; the MIL-011 decision date (2026-10-23) equals its Target Date. |
| 2 | Every Business Case scope item is covered by a gateway | Pass | The first read found a scope row that is not a Business Case item; it is removed and MIL-011 is listed beside MIL-010 for the badges item. |
| 3 | The schedule respects the Business Case constraints | Pass | No deadline in the Business Case; the window is one week. |
| 4 | Dependencies between milestones are stated | Pass | `MIL-003 + MIL-004 -> MIL-010 -> MIL-011`. |
| 5 | Every gateway has an owner who is a stakeholder ID | Pass | S05. |
| 6 | Plan content is internally consistent | Pass | The first read found "ten milestones" in the Purpose; it is now "eleven", and the Gantt, the schedule and the dependencies agree. |
| 7 | Open Issues are current | Pass | No plan risk was added for a default that names an old major; the release process and the test of task 3 carry the rule. Observation, not a failure. |

## Overall Verdict

Go - all criteria pass after three corrections found in the first read (the O5 wording, "ten milestones", and a scope row that was not a Business Case item). The author confirmed the acceptance in chat on 2026-10-14 as stand-in for S01; this is not an independent review.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Confirm this record by S01 when an independent reading is possible | S01 | 2026-10-30 |
| Task 1: reproduce the failure and list the defaults before any change to the workflows | S05 | 2026-10-16 |

---

[MIL-011]: ../../milestones/mil-011-code-metrics-default-tools-ref.md
[PP-001]: ../../project-plan.md
[BC-001]: ../../business-case.md
[SA-001]: ../../stakeholder-analysis.md
[ADR-0006]: ../../adr/adr-0006-release-process-and-version-pinning.md
[RC-068]: ./rc-068-mil-010-plan.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
