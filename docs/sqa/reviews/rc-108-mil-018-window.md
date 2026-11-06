# Review Record: MIL-018 window and PP-001 (RC-108)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-108 |
| CrossReference | [MIL-018], [PP-001], [QC-MIL-001], [QC-PP-001], [RC-092], [RC-105] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-07 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted by the author in chat on 2026-11-07 as stand-in for S01 | pending |

---

## Artifact Under Review

- Instance reviewed: [MIL-018] (`Target Date` section); delta of [PP-001] for the MIL-018 row, note, Gantt lines and the MIL-020 note
- Checklists used: [QC-MIL-001] for the milestone; [QC-PP-001] for the plan
- Scope: delta re-review of MIL-018 (criteria 3 and 6) and of PP-001 (criteria 2, 3, 5 and 13), reason: closes the action item of [RC-105], the plan still showed the window planned in [RC-092] (2026-12-21 to 2026-12-30) after the milestone was delivered
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, asked in chat on 2026-11-07 to correct the window and stands in for S01; the AI prepared the evidence)

## What changed

| Item | Before | After | Source of the new date |
| --- | --- | --- | --- |
| Window of MIL-018 | 2026-12-21 to 2026-12-30 | 2026-10-29 to 2026-11-05 | Scoped release delivered and released as 3.0.0 on 2026-10-29; trial on three repositories and release 3.1.0 on 2026-11-05 |
| Decision date of MIL-018 | 2026-12-30 | 2026-11-05 | The delivery of the trial and of release 3.1.0 |

The dependency on MIL-017 is kept in the documents, but the status the release waits for comes from the scoped validation that MIL-014 had delivered, so the milestone could run ahead of MIL-017. The window of MIL-017 is not changed here.

## Checklist Results

MIL-018 against [QC-MIL-001]:

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged; the section `Target Date` now says why the window lies ahead of MIL-017. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | 2026-11-05 is inside the plan's window, which ends 2026-12-26; the earlier date after that end (2026-12-30) is gone. |

PP-001 delta against [QC-PP-001]:

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 2 | Every milestone is listed once with its document, decision date and owner | Pass | MIL-018 has one row with decision date 2026-11-05. |
| 3 | Every decision date lies inside the plan's window and is consistent with the `MIL-*` document | Pass | 2026-11-05 equals the `Target Date` of [MIL-018] and lies inside the window. |
| 5 | Dependencies are stated, acyclic and consistent with the schedule order | Pass, with an exception | MIL-018 now ends before MIL-017 starts although it lists MIL-017 as a dependency; the note says the status it needs was delivered by MIL-014. MIL-017 keeps its planned window until it is delivered. |
| 13 | The schedule view and the dependency view agree | Pass | Table, Gantt lines and the note give the same window. |

## Overall Verdict

Go. Both criteria of MIL-018 and the four of the plan delta pass; criterion 5 passes with the exception above. The AI records the decision as stand-in for S01 on the author's request in chat; there is no independent reader and the decision stays open to challenge. The open tasks of MIL-018 on the host (verify, dry runs, release) are done in fact; closing them is a separate step.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Close the issues of MIL-018 that were done (verify that a scoped release can write, run the dry runs, release) | S05 | 2026-11-13 |
| Correct the window of MIL-017 when it is delivered, if it moves | S05 | 2026-11-13 |

---

[MIL-018]: ../../milestones/mil-018-scoped-release-workflow.md
[PP-001]: ../../project-plan.md
[RC-092]: ./rc-092-mil-018-pp-001.md
[RC-105]: ./rc-105-mil-020-pp-001.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[QC-PP-001]: ../../../framework/qc/artifacts/qc-project-plan.md
