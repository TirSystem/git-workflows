# Review Record: ADR-0009 superseded in part by ADR-0013

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-103 |
| CrossReference | [ADR-0009], [ADR-0013], [QC-ADR-001], [RC-063], [RC-086] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-06 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version; verdict Go, prepared by the AI in supervised mode and waiting for S01 to read it | pending |

---

## Artifact Under Review

- Instance reviewed: [ADR-0009]
- Checklist used: [QC-ADR-001]
- Scope: delta re-review of criteria 7, 8, 9 and 11 (the Version History row, the CrossReference and the Affected Artifacts of the supersede change); the decision text is unchanged and was reviewed in [RC-063]
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: supervised, not independent (the AI prepared the evidence and the review; S01 has not read it)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | The ID matches the filename number and is unique and sequential | N-A | Unchanged. |
| 2 | Context states the problem, the forces and the options evaluated | N-A | Unchanged. |
| 3 | At least two options were considered | N-A | Unchanged. |
| 4 | Decision is stated in one or two unhedged sentences and matches an evaluated option | N-A | Unchanged. |
| 5 | Consequences list both Positive and Negative outcomes | N-A | Unchanged. |
| 6 | Quality-attribute impacts are named where the decision affects them | N-A | Unchanged. |
| 7 | Affected Artifacts are listed as links, and each is also in CrossReference | Pass | [ADR-0013] is in the CrossReference and in Affected Artifacts, with what it replaces and what stands. |
| 8 | Status changes are recorded as new Version History rows with a Change summary and Commit link | Pass | One new row, `pending` until the commit exists; the retained row is not rewritten. The oldest row was removed by the two-row rule. |
| 9 | A superseded or deprecated ADR names its successor, and the successor links back | Pass | [ADR-0009] names [ADR-0013]; [ADR-0013] names [ADR-0009] in its CrossReference and Affected Artifacts (its delivery and caller parts replaced, token rule and `tools-ref` amendment stand). |
| 10 | Written in business or technical language of the domain | N-A | Unchanged. |
| 11 | Status is one of the allowed values | Pass | The new row is `Proposed`; the final value is `Superseded by ADR-0013`. |

## Overall Verdict

Go - the change records the supersede that [RC-086] named as an open condition: both ADRs read `Accepted` until now. It is a supersede in part (delivery and caller), so the ADR keeps its text as history. This is not independent: S01 has not read it.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| On a Go from S01, set the 2026-11-06 row of [ADR-0009] to `Superseded by ADR-0013` and the row before it to `Deprecated`, and set this record to `Accepted` | S01 | Before the pull request merges |

---

[ADR-0009]: ../../adr/adr-0009-wiki-publishing-reusable-workflow.md
[ADR-0013]: ../../adr/adr-0013-wiki-publishing-scoped-workflow.md
[RC-063]: ./rc-063-adr-0009.md
[RC-086]: ./rc-086-adr-0013-mil-014-pp-001.md
[QC-ADR-001]: ../../../framework/qc/artifacts/qc-adr.md
