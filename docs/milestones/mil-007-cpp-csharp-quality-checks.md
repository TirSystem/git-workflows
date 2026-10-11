# MIL-007: Quality checks for C++ and C#

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-007 |
| CrossReference | [BC-001], [US-001], [UC-005], [MIL-003], [MIL-004], [ADR-0005], [ADR-0006] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-11 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version | pending |

---

## Purpose

Decide whether a C++ or C# project can run the same kind of quality checks
as a Python or shell project, through a shared workflow of this repository,
and whether the runners of the instance can run them.

## Deliverable

Reusable quality-check workflows for C++ and for C#, each with a documented
set of inputs and pinned tool versions, a guide for reading its results on the
wiki in English, Danish and Bahasa Malaysia, a use of each in at least one
other repository, and a release that makes them available at the major tag.
The existing workflow `quality-checks.yml` for Python and shell keeps its
name and contract.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The runner of the instance can run the tools of each language (installed in the run or provided by the image), verified and recorded | Verified for both | A tool cannot be had without changing the runner |
| 2 | The contract (tools, versions, inputs, what a pass and a fail mean) is decided in an ADR, and a language that cannot be checked without a build system says what it needs | ADR accepted | Open |
| 3 | A failing check shows the tool, file and line in the log, verified with a seeded failure for each workflow | Verified | Cause not visible |
| 4 | One other repository runs each workflow and its status appears on pull requests | Appears for both | Does not run |
| 5 | The workflows embed no script: each runs a file of this repository, and the offline tests exercise the file | Count of embedded scripts is 0 | Embedded script remains |
| 6 | A release (a minor version) makes both available, and the changelog and the wiki name them | Released | Unreleased |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-003 | The contract, the reusable workflow mechanism and the guide for reading results |
| MIL-004 | The release process and the release workflow publish the result |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O4 | [BC-001] |
| US-001.09, US-001.10 (extended to C++ and C#) | [US-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2027-01-16 — proposed on 2026-10-11, to be confirmed by S01 standing in for S05 (ADR-0002); it follows the last decision of the plan, 2026-12-26, with two weeks from 2027-01-04. The Business Case sets no deadline.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Write the use case and stories for C++ and C# checks | Extend UC-005 (Run Project Quality Checks) so that its Brief names C++ and C#, and add stories to US-001 for a C++ project and a C# project, each with a pass and a fail acceptance criterion. Review them with the checklists of the `artifact` skill. | Yes | UC-005, US-001.09, US-001.10 |
| 2 | Verify what the runner provides | On a throwaway branch, run a job on `ubuntu-latest` that prints which of `clang-format`, `clang-tidy`, `cppcheck` and the .NET SDK (`dotnet --version`) exist, and whether each can be installed in the run (for example from PyPI, apt or the dotnet install script) and how long that takes. Record the result in the milestone like MIL-003 task 1. | No | |
| 3 | Decide the contract | Record an ADR that decides: one workflow for both languages or one per language; the tools and pinned versions (C++: `clang-format --dry-run -Werror`, `clang-tidy`, `cppcheck` or compiler warnings; C#: `dotnet format --verify-no-changes`, a build with analyzers and warnings as errors); the inputs (languages or paths, working directory, build command or compile database); what a build-dependent check needs from the caller; whether C is included with C++; and the names of the workflows and wiki pages (they follow `QualityChecksPythonShell`). Must be accepted before tasks 4 and 5. | No | ADR-0005 (refined) |
| 4 | Implement the C++ workflow | Add the reusable workflow and its script file `tools/quality-checks-cpp.sh` (or as the ADR decides), pinned tool versions, least-privilege permissions and offline tests with stub tools, as `quality-checks.yml` does. | No | |
| 5 | Implement the C# workflow | The same for C#, with its script file and tests. | No | |
| 6 | Write the guides and the wiki pages | One guide per workflow in `guides/` for reading its results, the wiki pages in English, Danish and Bahasa Malaysia, the Home workflow list and diagrams (a test requires every workflow to be listed), and an update of the upgrade guide. | No | |
| 7 | Adopt each workflow in one other repository | Onboard a real C++ project and a real C# project, or a throwaway repository when none exists, and fix the gaps in the guides that appear. Verify a seeded failure. | No | |
| 8 | Release | Add the changelog entry (a new workflow is a minor change, ADR-0006) and run the Release workflow; record the results in this milestone and review it. | No | |

---

[BC-001]: ../business-case.md
[US-001]: ../user-stories.md
[UC-005]: ../uc-005/uc.md
[MIL-003]: ./mil-003-quality-checks.md
[MIL-004]: ./mil-004-versioned-release.md
[ADR-0005]: ../adr/adr-0005-quality-check-contract.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
