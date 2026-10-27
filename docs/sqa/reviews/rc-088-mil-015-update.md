# Review Record: MIL-015 after pull request 218 and PP-001 (MIL-015)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-088 |
| CrossReference | [MIL-015], [PP-001], [RC-087], [QC-MIL-001], [QC-PP-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted by the author in chat on 2026-10-27 as stand-in for S01 | [081a17d] |

---

## Artifact Under Review

- Instance reviewed: [MIL-015]; delta of [PP-001] for the changed row and assumption
- Checklists used: [QC-MIL-001] for the milestone; [QC-PP-001] for the plan
- Scope: delta re-review of MIL-015 (purpose, deliverable, criterion 5, tasks 1, 3 and 4; criteria 1 to 6 of the checklist re-read) and of PP-001 (criteria 3, 8, 10, 11, 13 and 15), reason: pull request 218 renamed the live files and the required check of `main` was removed after RC-087; earlier record [RC-087]
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, asked in chat on 2026-10-27 for the update and the review and stands in for S01; the AI prepared the evidence)

## Checklist Results

MIL-015 against [QC-MIL-001]:

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | The deliverable now says what is done (live files, by task 1 and pull request 218) and what is not (history stays, status checks are off, callers, a release). |
| 2 | Explicit Go/No-Go criteria | Pass | Eight criteria. Criterion 5 now reads: status checks off, or every required context produced by a run of this repository, read back through the API; the old wording ("passed or not required") could not be read back. |
| 3 | Dependencies are mapped | Pass | Unchanged: the pull request of MIL-014 and ADR-0006. The documentation task that waited for it is replaced by a record-only task. |
| 4 | Traceable to a Business Case objective | Pass | O2 and O4 of [BC-001], unchanged. |
| 5 | Owner and approving reviewer | Pass | S05 and S01. |
| 6 | Target date consistent with the constraints | Pass | 2026-11-06 unchanged; fewer tasks remain. |

Facts the update rests on, each read on 2026-10-27:

| Claim | Evidence |
| --- | --- |
| Pull request 218 renamed the live files | Merged into `main` as `8327038`; `git grep github-action` in code, configuration, README, guides and wiki pages now finds only `tailscale/github-action` (another repository) and one changelog line. |
| The required check is gone | `GET .../branch_protections/main`: `enable_status_check` false, `status_check_contexts` null, `required_approvals` 0. |
| What remains | 194 places in 114 history files, 16 in 12 project documents. |

PP-001 delta against [QC-PP-001]:

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 3 | Decision dates agree with the `MIL-*` document | Pass | 2026-11-06 in both. |
| 8 | Assumptions are listed with their source | Pass | The MIL-015 assumption now records that pull request 218 and the removed check changed the scope, and what remains. |
| 10 | Open issues are current | Pass | No open issue contradicts the row. |
| 11 | The plan deliverable matches the `MIL-*` deliverable | Pass | The plan row (code, configuration and documentation name the new repository, callers updated, producible checks, released) still matches. |
| 13 | Schedule view and dependency view agree | Pass | Unchanged. |
| 15 | The plan is a singleton and changes are in Version History | Pass | New row; the two latest are kept. |

## Overall Verdict

Go. The update is smaller than the plan accepted in RC-087: tasks 1 and 3 are done and task 4 shrinks to a record and a list for S01. The first read found one weakness, now fixed: switching status checks off removed the gate for the offline tests too, so the protection is weaker than before the rename; this is an action item, not a fault in the milestone. The author accepted the update in chat on 2026-10-27 as stand-in for S01; this is not an independent review.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Confirm this record by S01 when an independent reading is possible | S01 | 2026-11-06 |
| Decide whether to switch status checks on `main` back on with only `Validate workflows / validate (pull_request)`; today no check gates the merge | S01 | 2026-11-06 |
| Decide whether the Business Case, Stakeholder Analysis, use cases, use case diagram and user stories change the name (16 places) | S01 | 2026-11-06 |

---

[MIL-015]: ../../milestones/mil-015-rename-to-git-workflows.md
[PP-001]: ../../project-plan.md
[BC-001]: ../../business-case.md
[RC-087]: ./rc-087-mil-015.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[QC-PP-001]: ../../../framework/qc/artifacts/qc-project-plan.md
[081a17d]: https://git.tirsystem.com/TirSystem/git-workflows/commit/081a17d07f4c7d7145cdc50984c669dfb798b48d
