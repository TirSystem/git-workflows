# Review Record: ADR-0010 (the coverage report as an artifact of the caller)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-073 |
| CrossReference | [ADR-0010], [QC-ADR-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | Accepted | Jens Tirsvad Nielsen | AI as stand-in for S01 | Initial version; accepted | [0dc5132] |

---

## Artifact Under Review

- Instance reviewed: [ADR-0010]
- Checklist used: [QC-ADR-001]
- Scope: delta re-review of the Coverage report and Inputs rules, the Consequences and the Version History after the implementation of MIL-010 task 6 showed that a called workflow cannot see the files of the caller's test job; earlier record RC-072
- Language and domain: n/a (technical type)
- Language reviewer: none
- Mode: autonomous, not independent (the reviewer is `AI as stand-in for S01`; the user accepted the plan in chat on 2026-10-14)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | The ID (`ADR-NNNN`, 4-digit) matches the filename number and is unique and sequential | Pass | Unchanged. |
| 2 | Context states the problem, the forces (cost, risk, constraints) and the options evaluated | Pass | Unchanged; the new force (a called workflow runs in its own job) is stated in the Decision rule that it explains. |
| 3 | At least two options were considered, or the absence of alternatives is justified | Pass | Unchanged. For the report: an artifact of the caller's run, or a file committed to the repository; both are supported. |
| 4 | Decision is stated in one or two unhedged sentences and matches one of the evaluated options | Pass | The Decision sentence is unchanged; the coverage rule is a refinement of it. |
| 5 | Consequences list both Positive and Negative outcomes | Pass | The negative consequence about the report now names the earlier job, the upload and the dependency on the artifact service, which task 8 verifies. |
| 6 | Quality-attribute impacts (performance, security, portability, etc.) are named where the decision affects them | Pass | The security bullet says the artifact is parsed as XML with entity declarations refused. |
| 7 | Affected Artifacts are listed as links, and each is also in CrossReference | Pass | Unchanged. |
| 8 | Status changes are recorded as new Version History rows with a Change summary and Commit link; retained rows are never rewritten | Pass | A new row; the earlier Accepted row became Deprecated and was not rewritten otherwise. |
| 9 | A superseded or deprecated ADR names its successor, and the successor links back | N-A | The ADR is amended, not superseded. |
| 10 | Written in business or technical language of the domain, with no unexplained abbreviations | Pass | Artifact is the term of the Actions runtime. |
| 11 | Status is one of `Proposed`, `Accepted`, `Rejected`, `Deprecated` or `Superseded by ADR-NNNN`, and every Version History row uses only these | Pass | Deprecated and Accepted. |

## Overall Verdict

Go - all applicable criteria pass; the amendment keeps the decisions of the user of 2026-10-14 and corrects a mechanism that cannot work as first written. The AI records the decision as stand-in for S01; there is no independent reader and the decision stays open to challenge in the run summary.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| None | - | - |

---

[ADR-0010]: ../../adr/adr-0010-code-metrics-badges-contract.md
[QC-ADR-001]: ../../../framework/qc/artifacts/qc-adr.md
[0dc5132]: https://git.tirsystem.com/TirSystem/github-action/commit/0dc5132a2ea419ba05035ee3594cec63335c240b
