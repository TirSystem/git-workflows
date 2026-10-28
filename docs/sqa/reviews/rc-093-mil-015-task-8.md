# Review Record: MIL-015 task 8 and PP-001 (RC-093)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-093 |
| CrossReference | [MIL-015], [PP-001], [QC-MIL-001], [QC-PP-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted by the author in chat on 2026-10-29 as stand-in for S01 | pending |

---

## Artifact Under Review

- Instance reviewed: [MIL-015]; delta of [PP-001] for the MIL-015 row and schedule note
- Checklists used: [QC-MIL-001] for the milestone; [QC-PP-001] for the plan
- Scope: delta re-review of MIL-015 (new criterion 9 and task 8; criteria 1 to 6 of the checklist re-read) and of PP-001 (criteria 3, 8, 10, 11, 13 and 15), reason: the Gitea secrets were renamed to `TOKEN_FOR_<host>_<purpose>` and the plan-first gate refused the commit because no task row covered the work; earlier record [RC-088]
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, chose in chat on 2026-10-29 to add the task and stands in for S01; the AI prepared the evidence)

## Checklist Results

MIL-015 against [QC-MIL-001]:

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | Task 8 names the files that change (two workflows, `tools/sync_github_metadata.py`, its tests and fixtures, the guides, the wiki pages in three languages, `.env.example`, `AGENTS.md`, the README), the Breaking changelog entry and the framework pin. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Criterion 9 is objective: a search of named paths finds the bare name only in the changelog, the two workflows read the two new names, the offline tests pass and the wiki check is clean. Its No-Go cell is the opposite. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged. Task 8 depends on the framework release v0.18.0, which exists and names the same secrets; task 8 comes before the release of task 7. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | O2 and O4 of [BC-001], unchanged; the task row cites [BC-001]. The Business Case constraint "Secrets are supplied as repository or organization secrets" still holds. |
| 5 | Milestone owner and approving reviewer are identified | Pass | S05 and S01, unchanged. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | 2026-11-06 unchanged; the work is already in the working tree, the tests pass (674) and what remains is the commit, the secrets in the organizations and the release. |

Finding on the first read: task 8 describes work that was done before the row existed (the working tree held 25 changed files and the commit hook refused them). The row records it now; it is not a reason to waive the gate, and the record says so.

PP-001 delta against [QC-PP-001]:

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 3 | Decision dates agree with the `MIL-*` document | Pass | 2026-11-06 in both. |
| 8 | Planning assumptions are listed with their source | Pass | The MIL-015 note says task 8 was added on 2026-10-29 and points to this record. |
| 10 | Open issues are current | Pass | No open issue contradicts the row. |
| 11 | The plan deliverable matches the `MIL-*` deliverable | Pass | The row now adds "Gitea secrets named TOKEN_FOR_<host>_<purpose>", as the milestone's deliverable and criterion 9 do. |
| 13 | Schedule view and dependency view agree | Pass | Unchanged. |
| 15 | The plan is a singleton and changes are in Version History | Pass | One new row; the two latest rows are kept. |

## Overall Verdict

Go. The task and its criterion are objective and trace to the same objectives as the rest of MIL-015; the plan row and note agree with the milestone. The first read found that the row was written after the work; that is recorded above. The author accepted the change in chat on 2026-10-29 as stand-in for S01, not independent.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Store the secrets `TOKEN_FOR_GITEA_REPO` and `TOKEN_FOR_GITEA_ISSUES` in each organization before the release, because a run without them fails | S03 | 2026-11-06 |
| Remove the old secret `TOKEN_FOR_GITEA` after the first successful run of both workflows | S03 | 2026-11-13 |

---

[MIL-015]: ../../milestones/mil-015-rename-to-git-workflows.md
[PP-001]: ../../project-plan.md
[RC-088]: ./rc-088-mil-015-update.md
[BC-001]: ../../business-case.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[QC-PP-001]: ../../../framework/qc/artifacts/qc-project-plan.md
