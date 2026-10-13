# Review Record: MIL-008 (task 5 deferred)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-061 |
| CrossReference | [MIL-008], [QC-MIL-001], [RC-060] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-13 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | pending |

---

## Artifact Under Review

- Instance reviewed: [MIL-008] after the amendment of 2026-10-13: task 5 changed from removing the scoped workflow to deprecating it, with the criterion that follows from it
- Checklist used: [QC-MIL-001]
- Scope: delta re-review of the amended task 5, criterion 5 and the Deliverable; the earlier record is [RC-060]
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised (S01, the user, chose option 1, defer the removal, in chat on 2026-10-13; the AI prepared the record)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | The Deliverable now says the scoped workflow is marked deprecated, not removed. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Criterion 5 is checkable: a notice in the header, the README and ADR-0009, and the list of repositories recorded; No-Go if it was removed while a repository depends on it. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged: MIL-006 and the framework's `process/wiki.md`. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | Unchanged: O2, O3. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Owner S05, approving reviewer S01. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | 2026-11-15, unchanged. |

## Overall Verdict

Go - all six criteria pass. The amendment follows from a scan on 2026-10-13: 8 repositories still publish through the scoped workflow and none calls the reusable one, so removal would have broken them. Removal and the migrations move to a follow-up milestone that needs its own plan.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Plan the follow-up milestone: migrate the 8 repositories (move `wiki/` to `docs/wiki/`, add the caller from `templates/ci/publish-wiki.yml`), then remove the scoped workflow in a major release | S05 | after the 1.2.2 release |
| Add MIL-008 to the Project Plan and review it (open since RC-060) | S05 | before the pull request |

---

---

[MIL-008]: ../../milestones/mil-008-wiki-reusable-workflow.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[RC-060]: ./rc-060-mil-008-plan.md
