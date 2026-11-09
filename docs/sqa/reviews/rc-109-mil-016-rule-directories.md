# MIL-016 task 8, rule directories by language (RC-109)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-109 |
| CrossReference | [MIL-016], [QC-MIL-001], [ADR-0015], [RC-099] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-09 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; verdict Go, prepared by the AI in supervised mode; accepted by the author in chat on 2026-11-09 as stand-in for S01 | [bc0157e] |

---

## Artifact Under Review

- Instance reviewed: [MIL-016]
- Checklist used: [QC-MIL-001]
- Scope: delta re-review of the Version History row of 2026-11-09 (new task 8, Release is now task 9), after [RC-099]; the Go/No-Go criteria are unchanged
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the author asked in chat on 2026-11-09 to add the task to MIL-016; the AI prepared the evidence and the review; the author accepted the row in chat on 2026-11-09 as stand-in for S01)

## Why the task is added

A run of the OpenGrep scoped workflow in another repository of the organization (81 tracked files) was still in its scan step after 5 minutes 28 seconds, while install took 4 seconds. The same scan of that repository took 23 seconds on a developer machine with 20 cores, and 56 seconds with one job and four of the twelve rule directories. The run time is set by the rules and the cores of the runner, not by the repository, so criterion 1 (a run ends in at most 5 minutes) fails for every repository on that runner. Excluding `docs/` was measured and changes nothing (no findings there, 24.9 s without and 25.5 s with the ignore file). The task loads only the rule directories of the languages a repository has.

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | Task 8 names its deliverable: the change to `tools/opengrep_scan.py`, the amendment of [ADR-0015], the printed list of chosen directories, and the comparison of findings between the full and the chosen set on this repository and three others, one with C and C++. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Unchanged, ten criteria. Criterion 1 (at most 5 minutes) is the one the task serves; the proof of equal findings is a task result, not a new criterion. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged. The task references [ADR-0015], which it amends, and Release (task 9) follows it. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | Unchanged: objective O8 of [BC-001]. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Owner S05, approving reviewer S01. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | The date 2026-12-11 and its window are unchanged. The new task is not estimated; the window was not re-planned for it. |

## Overall Verdict

Go - the row records the new task and its reason accurately, and claims nothing that is not measured. The time on the slow runner and the time after the change are not yet measured; task 8 requires them.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Accept the row of [MIL-016], set it to `Accepted` and the row before it to `Deprecated`, and this record to `Accepted` | S01 | Done on 2026-11-09 |
| Record in [MIL-016] the run time on the runner before and after the change (criterion 1) | S05 | With task 8 |

---

[MIL-016]: ../../milestones/mil-016-semgrep-scoped-workflow.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[ADR-0015]: ../../adr/adr-0015-semgrep-scoped-workflow.md
[RC-099]: ./rc-099-opengrep-bc-o8-mil-016.md
[BC-001]: ../../business-case.md
[bc0157e]: https://git.tirsystem.com/TirSystem/git-workflows/commit/bc0157ea2a017fe8a9377e8266dfda2878467865
