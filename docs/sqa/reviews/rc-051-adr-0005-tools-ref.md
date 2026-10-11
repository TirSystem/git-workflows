# Review Record: ADR-0005 (tools-ref)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-051 |
| CrossReference | [ADR-0005], [QC-ADR-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-11 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | [670f0ac] |

---

## Artifact Under Review

- Instance reviewed: [ADR-0005] after the addition of the input `tools-ref`
- Checklist used: [QC-ADR-001]

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | The ID (`ADR-NNNN`, 4-digit) matches the filename number and is unique and sequential | Pass | Unchanged. |
| 2 | Context states the problem, the forces (cost, risk, constraints) and the options evaluated | Pass | Unchanged; the move of the shell steps to a script file is an implementation of the decided contract, not a new option. |
| 3 | At least two options were considered, or the absence of alternatives is justified | Pass | Unchanged. |
| 4 | Decision is stated in one or two unhedged sentences and matches one of the evaluated options | Pass | The decision sentence names the new optional input. |
| 5 | Consequences list both Positive and Negative outcomes | Pass | Finding noted for the next revision, not a blocker: a reusable workflow cannot learn the ref it was called at (the context fields `workflow_ref`, `workflow_sha`, `job_workflow_sha` and `action_ref` are empty on this instance, verified on 2026-10-11), so the script ref is an input and a call at an exact tag is pinned completely only with `tools-ref` set to the same tag. |
| 6 | Quality-attribute impacts (performance, security, portability, etc.) are named where the decision affects them | Pass | Maintainability gains (a script of this repository, linted and tested as a file); the pin limitation above is the reliability cost. |
| 7 | Affected Artifacts are listed as links, and each is also in CrossReference | Pass | Unchanged. |
| 8 | Status changes are recorded as new Version History rows with a Change summary and Commit link; retained rows are never rewritten | Pass | The earlier row is kept with status Deprecated and a new row added. |
| 9 | A superseded or deprecated ADR names its successor, and the successor links back | N-A | Nothing is superseded. |
| 10 | Written in business or technical language of the domain, with no unexplained abbreviations | Pass | Unchanged. |
| 11 | Status is one of `Proposed`, `Accepted`, `Rejected`, `Deprecated` or `Superseded by ADR-NNNN`, and every Version History row uses only these | Pass | Deprecated and Accepted. |

## Overall Verdict

Go - all applicable criteria pass. Adding an optional input is a minor change under ADR-0006. S01 gave the Go in chat on 2026-10-11, standing in for the other reviewers as ADR-0002 records; there is no independent reader.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Run a pinned consumer (`@v1.0.1` with `tools-ref: v1.0.1`) after the next release to confirm the complete pin | S05 | next release |

---

[ADR-0005]: ../../adr/adr-0005-quality-check-contract.md
[QC-ADR-001]: ../../../framework/qc/qc-adr.md
[670f0ac]: https://git.tirsystem.com/TirSystem/github-action/commit/670f0ac469043bb166c84290c0dbf62b4908e3cc
