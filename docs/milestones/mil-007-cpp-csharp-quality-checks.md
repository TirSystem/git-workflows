# MIL-007: Quality checks for C++ and C#

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-007 |
| CrossReference | [BC-001], [US-001], [UC-005], [MIL-003], [MIL-004], [ADR-0005], [ADR-0006], [ADR-0008] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-13 | Deprecated | Jens Tirsvad Nielsen | AI as stand-in for S01 | Task 7 results added and reviewed (RC-059): adoption in two throwaway repositories, seeded failures verified, a guide gap fixed | [2481c26] |
| 2026-10-13 | Accepted | Jens Tirsvad Nielsen | AI as stand-in for S01 | Throwaway repositories of task 7 deleted at the user's request; action item of RC-059 closed | [daecb7b] |

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
name and contract. The workflows run current tools only: a .NET SDK of version
10 or later, and the latest stable release of each clang tool; a tool that
is only available as an old version is not used.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The runner of the instance can run the tools of each language (installed in the run or provided by the image), verified and recorded | Verified for both, at current versions (.NET SDK 10 or later) | A tool cannot be had without changing the runner, or only as an old version |
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

2027-01-16 — confirmed on 2026-10-11 by S01, standing in for S05 (ADR-0002); it follows the last decision of the plan, 2026-12-26, with two weeks from 2027-01-04. The Business Case sets no deadline.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Write the use case and stories for C++ and C# checks | Extend UC-005 (Run Project Quality Checks) so that its Brief names C++ and C#, and add stories to US-001 for a C++ project and a C# project, each with a pass and a fail acceptance criterion. Review them with the checklists of the `artifact` skill. | Yes | UC-005, US-001.09, US-001.10, US-001.16, US-001.17 |
| 2 | Verify what the runner provides | On a throwaway branch, run a job on `ubuntu-latest` that prints which of `clang-format`, `clang-tidy`, `cppcheck` and the .NET SDK (`dotnet --version`) exist, and whether each can be installed in the run (for example from PyPI, apt or the dotnet install script) and how long that takes. Record the result in the milestone like MIL-003 task 1. | No | |
| 3 | Decide the contract | Decided in ADR-0008 (accepted on 2026-10-11, RC-054): two separate reusable workflows, `quality-checks-cpp.yml` for C and C++ and `quality-checks-csharp.yml`, each running a script file fetched at `tools-ref`; C++: `clang-format --dry-run -Werror` and `clang-tidy` at exact current versions, no `cppcheck`; C#: `dotnet format --verify-no-changes` and a build with analyzers and warnings as errors, with the .NET SDK installed at an exact `10.0.x`; the inputs, the names of the workflows, guides and wiki pages and the consequences are in the ADR. | No | ADR-0008 |
| 4 | Implement the C++ workflow | Add the reusable workflow `quality-checks-cpp.yml` and its script file `tools/quality-checks-cpp.sh` as ADR-0008 decides, exact tool versions, least-privilege permissions and offline tests with stub tools, as `quality-checks.yml` does. | No | |
| 5 | Implement the C# workflow | The same for C#: `quality-checks-csharp.yml`, `tools/quality-checks-csharp.sh` and tests, as ADR-0008 decides. | No | |
| 6 | Write the guides and the wiki pages | One guide per workflow in `guides/` for reading its results, the wiki pages in English, Danish and Bahasa Malaysia, the Home workflow list and diagrams (a test requires every workflow to be listed), and an update of the upgrade guide. | No | |
| 7 | Adopt each workflow in one other repository | Onboard a real C++ project and a real C# project, or a throwaway repository when none exists, and fix the gaps in the guides that appear. Verify a seeded failure. | No | |
| 8 | Release | Add the changelog entry (a new workflow is a minor change, ADR-0006) and run the Release workflow; record the results in this milestone and review it. | No | |

## Verification results

Task 2 was run on 2026-10-11 with a throwaway branch, `verify-runner-tools`,
in `TirSystem/github-action` (run 692, deleted afterwards). One job on
`ubuntu-latest` printed what the image has and tried each way of installing a
tool.

| Fact | Result |
| --- | --- |
| Image | Ubuntu 24.04, `x86_64`, the job runs as root, `sudo`, `curl`, `python3` 3.12 and `pip` present |
| Present in the image | `gcc` and `g++` 13.3, `make`; missing: `clang-format`, `clang-tidy`, `cppcheck`, `cmake`, `dotnet` |
| `clang-format` | from PyPI in 2 s (23.1.3); from apt in 9 s |
| `clang-tidy` | from PyPI in 5 s (22.1.8); from apt in 25 s |
| `cppcheck` | apt gives 2.13.0 in 6 s, which is old (the latest release is 2.22.0); the PyPI package named `cppcheck` is a different project (1.5.3) and is not used; a current release needs a build from source |
| .NET SDK | the official script `dot.net/v1/dotnet-install.sh` with `--channel 10.0` gives 10.0.401 in 20 s; apt `dotnet-sdk-10.0` gives 10.0.112 in 23 s, an older feature band; the same script also offers 11.0 as a release candidate, which is not used |

A first run (run 692) looked at .NET SDK 8, which is not used: the requirement
is a .NET SDK of version 10 or later, and old tools are not run. A second run
(run 699, also deleted afterwards) checked current versions. The current
clang tools come from PyPI in a few seconds with an exact version, as
`quality-checks.yml` already does for its tools, and the .NET SDK 10 comes from
the official script in 20 s, with no change to the runner. `cppcheck` is the
exception: only an old version is a package. ADR-0008 drops it, because
`clang-tidy` does the static analysis and a current `cppcheck` would have to
be built from source, which costs minutes per run.
Not covered by this task: running a tool against a real C++ project (a
`clang-tidy` run needs a compile database or flags) or a real C# solution
(`dotnet format` and a build need the project's restore of packages from the
network), a private runner with no internet, and an image that differs from
`ubuntu-latest`. Those belong to the contract (task 3) and to the adoption
(task 7).

Task 7 was run on 2026-10-13 in two throwaway private repositories of the
organisation, `TirSystem/qc-adoption-cpp` and `TirSystem/qc-adoption-csharp`
(no real C++ or C# project exists there; the user chose throwaways in chat).
Each holds a small passing project, a style file, and a workflow that calls the
released `v1.2.0` (`quality-checks-cpp.yml`, `quality-checks-csharp.yml`) with
the guide's call. A branch `seeded-failure` with a pull request added a
formatting error and a null dereference.

| Repository | Baseline on `main` | Seeded failure (pull request 1) |
| --- | --- | --- |
| `qc-adoption-cpp` | Pass (runs 899, 900) | Fail (run 906): `main.cpp:3:13: error: code should be clang-formatted`, `main.cpp:5:18: error: Dereference of null pointer ... [clang-analyzer-core.NullDereference]`, `FAIL clang-format`, `FAIL clang-tidy (C++)`, last line `Quality checks failed: clang-format clang-tidy (C++)` |
| `qc-adoption-csharp` | Pass (runs 901, 902) | Fail: `src/Program.cs(5,3): error WHITESPACE`, `src/Program.cs(8,27): error CS8602`, `FAIL dotnet format --verify-no-changes`, `FAIL dotnet build -warnaserror` |

Both statuses (`quality` and `quality-checks-cpp` / `quality-checks-csharp`)
appear on the pull requests. One gap in the guides was found and fixed: they
said the paths are relative to `working-directory`, but `clang-tidy` and
`dotnet` print absolute paths in the workspace of the runner. The guides and
their three wiki languages now say so.

Not covered: a real C++ project with a compile database and a real C# solution
with many packages; both stay open until a project of that kind adopts the
workflows. The throwaway repositories were deleted at the user's request on 2026-10-13;
the run numbers above are kept as the record.

---

[BC-001]: ../business-case.md
[US-001]: ../user-stories.md
[UC-005]: ../uc-005/uc.md
[MIL-003]: ./mil-003-quality-checks.md
[MIL-004]: ./mil-004-versioned-release.md
[ADR-0005]: ../adr/adr-0005-quality-check-contract.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
[ADR-0008]: ../adr/adr-0008-cpp-csharp-quality-check-contract.md
[7bcc67a]: https://git.tirsystem.com/TirSystem/github-action/commit/7bcc67a065ac5f67b4e13ebf243a4bbbe2af47d9
[faf13b2]: https://git.tirsystem.com/TirSystem/github-action/commit/faf13b2c2a4901c0171977de1ffc2841023f537a
[2481c26]: https://git.tirsystem.com/TirSystem/github-action/commit/2481c26d802464decd51d75539157093b60e08e8
[daecb7b]: https://git.tirsystem.com/TirSystem/github-action/commit/daecb7b452197643b39752b9b453a8c376562354
