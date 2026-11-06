# Review Record: MIL-012 out of scope for now

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-104 |
| CrossReference | [MIL-012], [QC-MIL-001], [RC-082], [BC-001], [PP-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-06 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; verdict Go-with-conditions, prepared by the AI in supervised mode | [67ffbeb] |

---

## Artifact Under Review

- Instance reviewed: [MIL-012]
- Checklist used: [QC-MIL-001]
- Scope: delta re-review of the Version History row of 2026-11-06 (the open tasks are out of scope for now), after [RC-082]; the tasks and gate criteria are unchanged
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the AI prepared the evidence and the review; S01 read it and accepted the row in chat on 2026-11-06 with criterion 6 still open)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | Unchanged. The row states what was delivered (release 2.2.0, issue 191) and what was not (trials on a runner, guides and wiki pages, ADR review, framework templates, final review). |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Unchanged, ten criteria. The row does not claim any of the open ones. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | Unchanged: objective O6 of [BC-001]. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Author Jens Tirsvad Nielsen, reviewer S01. |
| 6 | Milestone has a defined target date consistent with project constraints | Pending | The Version History row says the date 2026-11-06 no longer applies, but the `Target Date` section of [MIL-012] still reads 2026-11-06 and [PP-001] still has the schedule row, the Gantt bar and a Go/No-Go on 2026-11-06. The two disagree until S01 decides: a new date, or none while the milestone is out of scope. |

## Overall Verdict

Go-with-conditions - the row records the product owner's decision accurately: it names the closed issues and the delivered release and claims nothing more. Criterion 6 is Pending because the target date and the plan still show 2026-11-06. A Pending criterion allows Go-with-conditions at most, so the row would stay `Proposed` until the condition is closed. S01 accepted the row in chat on 2026-11-06 without deciding the target date, so the row is `Accepted` with the condition open: the `Target Date` section of [MIL-012] and the schedule of [PP-001] still read 2026-11-06. This is not independent: the AI prepared it.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Decide the target date of [MIL-012]: a new date, or none while it is out of scope; then change its `Target Date` section and the schedule row, Gantt bar and Go/No-Go of [PP-001] to match | S01 | Open: no date was decided when the row was accepted |
| Row of [MIL-012] set to `Accepted` and the row before it to `Deprecated`, and this record to `Accepted`, on S01's acceptance in chat | S01 | Done on 2026-11-06 |

---

[MIL-012]: ../../milestones/mil-012-vpn-actions-for-deployment.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[RC-082]: ./rc-082-mil-012-results.md
[BC-001]: ../../business-case.md
[PP-001]: ../../project-plan.md
[67ffbeb]: https://git.tirsystem.com/TirSystem/git-workflows/commit/67ffbeb2f61a432732ddc3b40dbe40df97bf6247
