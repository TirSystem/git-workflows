# Review Record: MIL-014 task 11 (RC-097)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-097 |
| CrossReference | [MIL-014], [QC-MIL-001], [RC-095] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted by the author in chat on 2026-10-29 as stand-in for S01 | [07c2261] |

---

## Artifact Under Review

- Instance reviewed: [MIL-014]; delta for criterion 11 and task 11
- Checklist used: [QC-MIL-001]
- Scope: delta re-review of MIL-014 (criteria 1 to 6 re-read), reason: the rename of the wiki pages (task 10, [RC-095]) leaves old pages on the wiki, the publisher never deletes, and the author asked on 2026-10-29 to keep the clean-up script for other repositories
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, chose in chat on 2026-10-29 to keep the script in this repository and stands in for S01; the AI prepared the evidence)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | Task 11 names the script `tools/gitea_cleanup.py`, its three options and its tests. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Criterion 11 is objective: a dry run by default, only pages whose replacement exists, no tag deleted, no token printed, tests and coverage at 95%. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged; task 11 follows task 10 of the same milestone. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | [BC-001], unchanged; the task row cites it. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Unchanged. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | 2026-11-27 unchanged. |

Finding on the first read: the script was written and used as a personal file before the row existed, and it deletes data. The row records that a person runs it with `--apply` and that the AI does not; it is not a reason to waive the gate.

## Overall Verdict

Go. The task and its criterion are objective, the destructive part is behind a flag, and the tests cover the dry run, the selection and the refusals. The author accepted the change in chat on 2026-10-29 as stand-in for S01, not independent.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Run the script in a dry run for the wiki of git-workflows and the releases of the framework, read the list, then run it with `--apply` | S03 | 2026-11-06 |

---

[MIL-014]: ../../milestones/mil-014-wiki-publishing-scoped-again.md
[RC-095]: ./rc-095-adr-0014-mil-014.md
[BC-001]: ../../business-case.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[07c2261]: https://git.tirsystem.com/TirSystem/git-workflows/commit/07c22617736d0e125134ee1286fe04652c98a93c
