# MIL-016 task 8, run time on the runner (RC-111)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-111 |
| CrossReference | [MIL-016], [QC-MIL-001], [ADR-0015], [RC-109], [RC-110] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-09 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; verdict Go, prepared by the AI in supervised mode; accepted by the author in chat on 2026-11-09 as stand-in for S01 | [e9b782d] |

---

## Artifact Under Review

- Instance reviewed: [MIL-016]
- Checklist used: [QC-MIL-001]
- Scope: delta re-review of the Version History row of 2026-11-09 that records the run time on the runner in task 8, after [RC-109]; the Go/No-Go criteria and the target date are unchanged
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the author asked in chat on 2026-11-09 to record the measurement; the AI prepared the evidence and the review; the author accepted the row in chat on 2026-11-09 as stand-in for S01)

## Measurement

Read by the author from the run pages of `opengrep.yml` on this repository and given to the AI as screenshots on 2026-11-09. The AI did not read the logs.

| Run | Commit | Script | Time |
| --- | --- | --- | --- |
| 767 | 0861897, the release preparation, before `v3` moved | old, all twelve rule directories | 8 min 0 s for the run |
| 771 | c8beb0c, the merge of the release, after `v3` moved to 3.3.1 | new, rule files of the languages present | 5 min 1 s for the run |

Steps of run 771: set up job 10 s, check out 8 s, fetch the shared script 10 s, install OpenGrep and its rules 7 s, **scan 4 min 21 s**, complete job 3 s. The run is 37% shorter than run 767. Criterion 1 of [MIL-016] (at most 5 minutes) is met for the scan step with 39 s to spare; the whole run is 1 s over.

The 5 min 28 s of [RC-109] and [RC-110] was the scan step of another repository (81 tracked files) before the change; it is not the baseline of this table, because the two repositories differ.

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | Task 8 now carries its result: the two run times, the steps, and the repository. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Unchanged, ten criteria. Criterion 1 is met by the scan step; the whole run takes 1 s more than the limit, and the row says so. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | Unchanged: objective O8 of [BC-001]. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Owner S05, approving reviewer S01. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | Unchanged, 2026-12-11. |

## Overall Verdict

Go - the row records what was measured and its limits: one run, one repository, read from the run pages, a margin of 39 s. It does not claim a figure for repositories with more languages.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Accept the row of [MIL-016], set it to `Accepted` and the row before it to `Deprecated`, and this record to `Accepted` | S01 | Done on 2026-11-09 |
| Closes the action "record in [MIL-016] the run time on the runner" of [RC-109] and the action "measure the scan step on the runner after the release" of [RC-110]; those records are accepted and are not edited | S05 | With this record |
| Measure the scan step in a repository with several languages, and again when the margin of 39 s is used up by a slower run; if the scan step passes 5 minutes, open a decision on the other options of [ADR-0015] | S05 | When a run is seen over 5 minutes |

---

[MIL-016]: ../../milestones/mil-016-semgrep-scoped-workflow.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[ADR-0015]: ../../adr/adr-0015-semgrep-scoped-workflow.md
[RC-109]: ./rc-109-mil-016-rule-directories.md
[RC-110]: ./rc-110-adr-0015-rule-selection.md
[BC-001]: ../../business-case.md
[e9b782d]: https://git.tirsystem.com/TirSystem/git-workflows/commit/e9b782dc0bc3984c66629047e00012024fd6ff93
