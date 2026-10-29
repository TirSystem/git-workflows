# Review Record: OpenGrep in O8, MIL-016 and PP-001

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-099 |
| CrossReference | [BC-001], [MIL-016], [PP-001], [ADR-0015], [RC-098], [RC-089], [RC-090], [QC-BC-001], [QC-MIL-001], [QC-PP-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; verdict Go; accepted by the author in chat as stand-in for S01, not independent | [d4901e0] |

---

## Artifact Under Review

- Instance reviewed: [BC-001] (objective O8 and its scope item, assumption, constraint and risk); [MIL-016]; delta of [PP-001] for the MIL-016 row
- Checklists used: [QC-BC-001], [QC-MIL-001], [QC-PP-001]
- Scope: delta re-review after the change of tool from Semgrep to OpenGrep decided in [ADR-0015] (reviewed in [RC-098]): Business Case criteria 2, 3, 4 and 7; MIL-016 criteria 1 to 6; PP-001 criteria 3, 8 and 11; earlier records [RC-089] and [RC-090]
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, accepted the change of tool in chat on 2026-10-29 and stands in for S01; the AI prepared the evidence)

## Checklist Results

[BC-001] against [QC-BC-001]:

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 2 | Risks are identified with documented impact and mitigation | Pass | The risk row now names no vendor registry and no login (task 2), the licences read before building (task 3), and the way to silence a finding and the false-positive count (tasks 6 and 7). The age of the rules is added to the plan risk, not here. |
| 3 | Success criteria are measurable, stating explicit targets | Pass | Criterion 8 (0 findings of the blocking severity on the default branch after MIL-016) is unchanged. First read: this repository has 3 `ERROR` findings with OpenGrep, so the target is reachable only after they are fixed or silenced; recorded as an action item, not a change of the criterion. |
| 4 | Scope separates In Scope from Out of Scope | Pass | The in-scope item reads "a free static security scan with OpenGrep as a scoped workflow (MIL-016)". |
| 7 | Assumptions and constraints are explicit and distinguished | Pass | The assumption is now a Linux x86_64 runner that reaches `github.com`; the constraint (no login, no source code to a service outside the instance) is kept; each names the MIL-016 task that verifies it. The statement "with metrics off" was removed because OpenGrep has no such option and the traffic was not captured. |

[MIL-016] against [QC-MIL-001]:

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | `opengrep.yml`, its script, ADR-0015, the guide `guides/opengrep.md`, the adoption row, README and wiki pages, a trial and a minor release. |
| 2 | Explicit Go/No-Go criteria | Pass | Criterion 1 now lists the outbound hosts and checks the sha256; criterion 6 names `.semgrepignore` and `# nosemgrep`, both checked on 2026-10-29. |
| 3 | Dependencies are mapped | Pass | Unchanged: MIL-014, MIL-013, ADR-0005 and objective O8. |
| 4 | Traceable to a Business Case objective | Pass | O8 of [BC-001]. |
| 5 | Owner and approving reviewer | Pass | S05 and S01. |
| 6 | Target date consistent with the constraints | Pass | 2026-12-11, unchanged. |

PP-001 delta against [QC-PP-001]:

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 3 | Decision dates agree with the `MIL-*` document | Pass | 2026-12-11 in both. |
| 8 | Assumptions are listed with their source | Pass | The plan risk now names the December 2024 rules fork under the Commons Clause as the licence and age risk. |
| 11 | The plan deliverable matches the `MIL-*` deliverable | Pass | "Scoped OpenGrep workflow with a pinned rules checkout, ADR-0015, guide, adoption row, wiki in three languages, trial on four repositories, released as the next minor". |

## Overall Verdict

Go. The change is a replacement of the tool in text; the dates, owners, dependencies and the measurable targets are unchanged. Task 2 now says what is done (a developer machine, 2026-10-29) and what is not (a runner of the instance with a capture of the outbound hosts). The author accepted the change in chat on 2026-10-29 as stand-in for S01; this is not an independent review.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Confirm this record by S01 when an independent reading is possible | S01 | 2026-11-06 |
| Fix or silence the 3 `ERROR` findings of this repository (two `dangerous-subprocess-use-audit`, one `use-defused-xml` in `tools/`) before the workflow runs here, so success criterion 8 of the Business Case can be met | S05 | 2026-12-04 |

---

[BC-001]: ../../business-case.md
[MIL-016]: ../../milestones/mil-016-semgrep-scoped-workflow.md
[PP-001]: ../../project-plan.md
[ADR-0015]: ../../adr/adr-0015-semgrep-scoped-workflow.md
[RC-098]: ./rc-098-adr-0015.md
[RC-089]: ./rc-089-bc-001-o8.md
[RC-090]: ./rc-090-mil-016.md
[QC-BC-001]: ../../../framework/qc/artifacts/qc-business-case.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[QC-PP-001]: ../../../framework/qc/artifacts/qc-project-plan.md
[d4901e0]: https://git.tirsystem.com/TirSystem/git-workflows/commit/d4901e026d9fdf0c3a9fb86f46a59bf1f73dc53b
