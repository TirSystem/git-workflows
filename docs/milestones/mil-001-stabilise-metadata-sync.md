# MIL-001: Stabilise the metadata sync

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-001 |
| CrossReference | [BC-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-03 | Accepted | Jens Tirsvad Nielsen | S01 | Owner is S05 (security authority); S01 remains approving reviewer | [4de5438] |
| 2026-10-03 | Proposed | Jens Tirsvad Nielsen | S01 | Recorded decisions for tasks 1 and 3 | [cbb9688] |

---

## Purpose

Decide whether the only implemented workflow is correct, tested and has one
canonical copy, so later milestones build on a sound base.

## Deliverable

A single canonical metadata-sync workflow that passes automated validation
and tests, a README that separates implemented from planned behavior, and a
successful manual run on the Gitea instance.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The embedded Python compiles and every workflow YAML parses in an automated check | Check passes | Any failure |
| 2 | Exactly one canonical source per workflow; other copies are generated or removed | Count is 1 | Count above 1 |
| 3 | Unit tests cover credential parsing and push mirror URL parsing, and run without network access or `.env` | Tests pass | Missing or failing |
| 4 | README capability table matches the workflows present | Matches | Claims unimplemented behavior |
| 5 | Manual `workflow_dispatch` run on Gitea succeeds and the GitHub description and topics match | Match | Mismatch or failure |

## Dependencies

| Depends on | Reason |
| --- | --- |
| None | First milestone |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O1, O2 | [BC-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-10-17 — proposed; to be confirmed by S01 and S05 (the Business Case sets no deadline).

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Decide behavior for an invalid push mirror response | The committed workflow fails with an error when Gitea returns a non-list push mirror response. The uncommitted scoped copy instead prints a message and tries to exit successfully, and the README diagram showed that. Choose fail or skip, record the decision, and align code and README. Decision: skip with a visible warning and a successful run, following the maintainer's edit to the scoped copy; zero, several or malformed GitHub mirrors still fail. | No | |
| 2 | Fix the Python syntax error in the scoped workflow | `exit 0` is not valid Python, so the whole embedded script fails to compile in the scoped copy. Replace it according to the decision in task 1 (`sys.exit(0)` also needs `import sys`). | No | |
| 3 | Reduce the workflow to one canonical source | The same workflow exists in `src/` and `.gitea/scoped_workflows/` (and a legacy copy that is no longer documented), and the scoped copy has diverged. Choose the canonical location, and generate or remove the others. Decision: `.gitea/scoped_workflows/` is canonical because the script must be embedded in the YAML to work as a scoped workflow; the `src/` copy is removed. | No | |
| 4 | Add static validation of workflow files | Parse each workflow YAML and compile its embedded Python in an automated check that runs on pull requests, so defects such as task 2 fail before merge. | No | |
| 5 | Add offline unit tests for the sync logic | Move credential and mirror URL parsing into testable code and test bare token, JSON token, SSH and HTTPS mirror addresses, and zero or several mirrors. Replace `tests/test_.ps1`, which probes a hard-coded real repository and reads `.env`. | No | |
| 6 | Keep the README accurate | Maintain the capability table (implemented, partial, planned), and align the sequence diagram with the final behavior from task 1. | No | |
| 7 | Verify a live run | Trigger the workflow manually on Gitea and compare the GitHub description and topics with the Gitea repository. | No | |

---

[BC-001]: ../business-case.md
[4de5438]: https://git.tirsystem.com/TirSystem/github-action/commit/4de5438a88b4bbf18b165f52f797d1a52af89f6d
[cbb9688]: https://git.tirsystem.com/TirSystem/github-action/commit/cbb9688ed4217ee953d5843b846e2e79f22aaf45
