# Review Record: MIL-008

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-060 |
| CrossReference | [MIL-008], [QC-MIL-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-13 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | pending |

---

## Artifact Under Review

- Instance reviewed: [MIL-008]
- Checklist used: [QC-MIL-001]
- Scope: full review
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised (S01, the user, accepted the plan in chat on 2026-10-13; the AI prepared the record)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | The Deliverable section names the reusable workflow, the caller template, tests, the superseding ADR, the moved wiki and the release. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Six criteria, each with a checkable Go and No-Go (tests, a read-back with 0 differences, the `v1` tag). |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | MIL-006, and the framework's `process/wiki.md`, which is still unmerged and is named as such. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | O2 and O3 of [BC-001], as for MIL-006. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Owner S05, approving reviewer S01. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | 2026-11-15; the Business Case sets no deadline and the plan's last decision is 2026-12-26. |

## Overall Verdict

Go - all six criteria pass. The release is a patch (1.2.1 to 1.2.2) by the owner's decision, although ADR-0006 classes a new workflow as minor and a removed one as breaking; task 7 records the deviation in the changelog, and S01 chose it over a minor release and over keeping the scoped workflow.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Add MIL-008 to the Project Plan (milestone table, CrossReference, dependency graph) and review it | S05 | before the pull request |
| Merge `process/wiki.md` in `sqa-qc-framework` before this repository pins it | S05 | before task 3 ships |
| List the repositories that publish through the scoped workflow before task 5 removes it | S05 | before task 5 |

---

---

[MIL-008]: ../../milestones/mil-008-wiki-reusable-workflow.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
