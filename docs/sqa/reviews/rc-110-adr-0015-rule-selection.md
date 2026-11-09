# Review Record: ADR-0015 amendment, rule selection (RC-110)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-110 |
| CrossReference | [ADR-0015], [MIL-016], [QC-ADR-001], [RC-098] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-09 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version; verdict Go, prepared by the AI in supervised mode | pending |

---

## Artifact Under Review

- Instance reviewed: [ADR-0015]
- Checklist used: [QC-ADR-001]
- Scope: delta review of the amendment of 2026-11-09 (the script passes only the rule files of the languages the repository has; MIL-016 task 8) and of the lines of the Decision and the Consequences it changes; the earlier record is [RC-098]
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, asked in chat on 2026-11-09 to do task 8; the AI prepared the evidence and the review; S01 accepts or rejects the row in chat)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | The ID matches the filename number and is unique and sequential | Pass | Unchanged: `ADR-0015`. |
| 2 | Context states the problem, the forces and the options evaluated | Pass | The amendment names the problem (a scan step over 5 minutes 28 seconds on the runner, criterion 1 of [MIL-016]) and the force (the time follows the number of rules and the cores, not the repository), with the measurements. |
| 3 | At least two options were considered | Pass | Four: keep all rules, skip whole directories, skip rule files, fewer directories for everyone. Excluding `docs/` was also measured and has no effect. |
| 4 | Decision is stated in one or two unhedged sentences and matches an evaluated option | Pass | The Decision names option 3 of the amendment and the rule for what is kept; the fail-safe cases are listed. |
| 5 | Consequences list both Positive and Negative outcomes | Pass | A positive line with the measured result and a negative line for the dependence on the structure of the rule files and the table of extensions. |
| 6 | Quality-attribute impacts are named where the decision affects them | Pass | Performance efficiency (run time) and reliability of the result (no rule dropped on a doubt, findings equal on two repositories). The time on the runner is not yet measured. |
| 7 | Affected Artifacts are listed as links, and each is also in CrossReference | Pass | Unchanged list; [RC-110] is added to CrossReference and the links. |
| 8 | Status changes are recorded as new Version History rows | Pass | A new row, `Proposed`; the earlier row stays `Accepted` until S01 accepts, then becomes `Deprecated`. |
| 9 | A superseded or deprecated ADR names its successor, and the successor links back | Not applicable | The amendment changes parts of one ADR, not another ADR. |
| 10 | Written in the language of the domain, with no unexplained abbreviations | Pass | |
| 11 | Status is one of the allowed values | Pass | `Proposed`. |

Facts the amendment rests on, each measured on 2026-11-09 with OpenGrep 1.33.1 and the pinned rules:

| Claim | Evidence |
| --- | --- |
| The scan step on the runner took over 5 minutes 28 seconds, install 4 seconds | The step list of the run of another repository of the organization (81 tracked files), seen by the author |
| 23 s on 20 cores, 2 min 39 s with one job, for all twelve directories | Timed on a clean export of that repository |
| Excluding `docs/` changes nothing | 24.9 s without and 25.5 s with the ignore file, no finding in `docs/` |
| Findings equal with the filtered rules | 34 findings (this repository) and 12 (the second) equal by path, line and rule name |
| 18.5 s and 14.8 s filtered; 1 min 15 s with one job | Same runs |

## Overall Verdict

Go - the amendment records the problem, the options and the measured result, and the Decision is stated plainly. The time on the runner after release is not measured; MIL-016 task 8 records it.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Accept the row of [ADR-0015], set it to `Accepted` and the row before it to `Deprecated`, and this record to `Accepted` | S01 | On acceptance in chat |
| Measure the scan step on the runner after the release and record it in [MIL-016] (criterion 1) | S05 | After the release |

---

[ADR-0015]: ../../adr/adr-0015-semgrep-scoped-workflow.md
[MIL-016]: ../../milestones/mil-016-semgrep-scoped-workflow.md
[QC-ADR-001]: ../../../framework/qc/artifacts/qc-adr.md
[RC-098]: ./rc-098-adr-0015.md
