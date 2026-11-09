# MIL-016 task 8, run time on the runner (RC-111)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-111 |
| CrossReference | [MIL-016], [QC-MIL-001], [ADR-0015], [RC-109], [RC-110] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-09 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version; verdict Go, prepared by the AI in supervised mode | pending |

---

## Artifact Under Review

- Instance reviewed: [MIL-016]
- Checklist used: [QC-MIL-001]
- Scope: delta re-review of the Version History row of 2026-11-09 that records the run time on the runner in task 8, after [RC-109]; the Go/No-Go criteria and the target date are unchanged
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the author asked in chat on 2026-11-09 to record the measurement; the AI prepared the evidence and the review; the row stays `Proposed` until the author accepts it in chat as stand-in for S01)

## Measurement

Read from the job and step times of the runs of `opengrep.yml` on this repository, through the Actions API on 2026-11-09. Run numbers are the ids in the run addresses (`/actions/runs/<id>`).

| Run | Script | Scan step | Whole job |
| --- | --- | --- | --- |
| 4628 (push, 3.3.0 at `v3`) | old, all twelve rule directories | 4 min 21 s | 5 min 1 s |
| 4644 (re-run of the push of the fix, `v3` = 3.3.2) | new, rule files of the languages present | 3 min 18 s | 3 min 52 s |
| 4652 (pull request 319, `v3` = 3.3.2) | new | 3 min 5 s | 3 min 30 s |

The scan step is about 25% shorter, and criterion 1 of [MIL-016] (at most 5 minutes) is met with about 1 min 40 s to spare. Release 3.3.1 is not in the table: its scan read the copy of the rules inside the repository as source, failed with 41 findings of severity `ERROR` in those files, and was fixed by 3.3.2 (`CHANGELOG.md`). A first version of this record took the old script's run 4628 for a run of 3.3.1 and was withdrawn.

The 5 min 28 s of [RC-109] and [RC-110] was the scan step of another repository (81 tracked files) before the change; it is not the baseline of this table, because the two repositories differ.

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | Task 8 now carries its result: the three run times, the steps, and the repository. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Unchanged, ten criteria. Criterion 1 is met by the scan step and by the whole job. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | Unchanged: objective O8 of [BC-001]. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Owner S05, approving reviewer S01. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | Unchanged, 2026-12-11. |

## Overall Verdict

Go - the row records what was measured and its limits: two runs of one repository, read from the step times of the runs, a margin of about 1 min 40 s. It does not claim a figure for repositories with more languages.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Accept the row of [MIL-016], set it to `Accepted` and the row before it to `Deprecated`, and this record to `Accepted` | S01 | When the author accepts in chat |
| Closes the action "record in [MIL-016] the run time on the runner" of [RC-109] and the action "measure the scan step on the runner after the release" of [RC-110]; those records are accepted and are not edited | S05 | With this record |
| Measure the scan step in a repository with several languages, and again when the margin of about 1 min 40 s is used up by a slower run; if the scan step passes 5 minutes, open a decision on the other options of [ADR-0015] | S05 | When a run is seen over 5 minutes |

---

[MIL-016]: ../../milestones/mil-016-semgrep-scoped-workflow.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[ADR-0015]: ../../adr/adr-0015-semgrep-scoped-workflow.md
[RC-109]: ./rc-109-mil-016-rule-directories.md
[RC-110]: ./rc-110-adr-0015-rule-selection.md
[BC-001]: ../../business-case.md
[e9b782d]: https://git.tirsystem.com/TirSystem/git-workflows/commit/e9b782dc0bc3984c66629047e00012024fd6ff93
