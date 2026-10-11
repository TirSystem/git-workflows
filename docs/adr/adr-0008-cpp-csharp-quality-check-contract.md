# ADR-0008: Quality-check contract for C++ and C#

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0008 |
| CrossReference | [MIL-007], [UC-005], [US-001], [ADR-0005], [ADR-0006] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-11 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version | [11cba35] |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

ADR-0005 defines the contract of the shared quality-check workflow for Python
and shell: inputs with working defaults, a pinned version per tool, every tool
runs, a failure names tool, file and line, and a language without files
passes with a notice. MIL-007 adds C++ and C#. Two requirements came from S01
on 2026-10-11 and bound the decision:

- C++ and C# are separate workflows, not an extension of `quality-checks.yml`.
- Old tools are not run: the .NET SDK is version 10 or later, and a tool that
  is only available as an old version is not used.

Facts (MIL-007 task 2, runs 692 and 699 on `ubuntu-latest`, Ubuntu 24.04,
root, `gcc`/`g++` 13.3 present):

- `clang-format` 23.1.3 and `clang-tidy` 22.1.8 install from PyPI in a few
  seconds with an exact version.
- `cppcheck` is only available as an old version (apt 2.13.0; the latest
  release is 2.22.0; the PyPI package of that name is another project).
- The .NET SDK 10.0.401 installs with the official `dotnet-install.sh` in about
  20 s with an exact `--version`; apt gives an older band (10.0.112).
- A `clang-tidy` run needs flags or a compile database, and a C# format check
  and build need the project's package restore, which needs the network.

Options:

1. **One combined workflow for C++ and C#.** One page and one place to call,
   but two unrelated toolchains in one job, and an input set that mixes both.
2. **One workflow per language** (`quality-checks-cpp.yml`,
   `quality-checks-csharp.yml`), each with its own inputs and tools.
3. **Extend `quality-checks.yml`** with two more values of `languages`.
   Rejected by S01 (separate workflows) and it would make the contract of
   ADR-0005 grow with every language.

For `cppcheck`: (a) keep the apt version, (b) build a current release from
source in every run, (c) drop it. For the SDK: (a) a channel such as `10.0`,
(b) an exact version.

## Decision

C++ and C# are checked by two separate reusable workflows,
`quality-checks-cpp.yml` and `quality-checks-csharp.yml`, each running a script
file of this repository (`tools/quality-checks-cpp.sh`,
`tools/quality-checks-csharp.sh`) that it fetches at its input `tools-ref`
(default `v1`), with the contract of ADR-0005 for pass, fail, logs and
skipped languages; `cppcheck` is not used, and the .NET SDK is installed at an
exact version of 10 or later.

The rules that follow from it:

- **C++ (and C):** `clang-format --dry-run -Werror` and `clang-tidy` on the
  tracked `*.c`, `*.cc`, `*.cpp`, `*.cxx`, `*.h`, `*.hh`, `*.hpp` files under
  `working-directory`, both from PyPI at the exact versions of the inputs
  `clang-format-version` (default `23.1.3`) and `clang-tidy-version` (default
  `22.1.8`). Inputs: `working-directory` (default `.`), `std` (default
  `c++20`), `compile-commands-dir` (default empty: the flags `-std=<std>` are
  used; set it to the directory of a `compile_commands.json` the caller built
  before the call), `tools-ref`. A `.clang-format` and a `.clang-tidy` of the
  project configure the tools; a missing `.clang-format` is a
  `[configuration]` failure.
- **C#:** `dotnet format --verify-no-changes` and `dotnet build
  -warnaserror` with the analyzers the project enables in `.editorconfig`,
  on the solution or project found under `working-directory`. Inputs:
  `working-directory` (default `.`), `project` (default empty: the single
  `*.sln`, `*.slnx` or `*.csproj` found; none or several is a
  `[configuration]` failure that names them), `dotnet-sdk-version` (default
  an exact `10.0.x`, installed with `dotnet-install.sh --version`),
  `tools-ref`.
- **No `cppcheck`:** `clang-tidy` does the static analysis with a current
  release; a future version of the contract may add a static analyzer when a
  current release is a package.
- **Exact pins:** every tool input is an exact version, never a channel or a
  range; raising a default is a breaking change under ADR-0006.
- **Names:** the wiki pages are `QualityChecksCpp` and `QualityChecksCSharp`
  with the usual `.da` and `.ms` translations; the guides are
  `guides/quality-checks-cpp.md` and `guides/quality-checks-csharp.md`.
- **C is included with C++:** the same tools check both and the files are
  told apart by extension; `QC-CL-001` and `QC-CPP-001` stay the review
  checklists of the code itself.

## Consequences

**Positive:**

- Each workflow has inputs that fit its language, and a consumer of one never
  sees the inputs of the other.
- Only current tools run; a run is reproducible because every version is exact.
- The scripts are files that are linted and tested with stub tools, as for
  `quality-checks.yml`.

**Negative:**

- Two workflows, two guides and two wiki pages to keep; a repository with both
  languages calls both.
- Without `cppcheck` the C++ checks are `clang-tidy` and the compiler only; a
  defect class that `cppcheck` finds may go unchecked.
- A C# check needs the network for the package restore, and a C++ check needs
  the caller to build a compile database for precise results; both are the
  caller's responsibility and are said in the guides.
- Raising the exact default of a tool, including the SDK, is a breaking
  change and costs a major version (ADR-0006).
- A caller pinned to an exact tag is pinned completely only when `tools-ref`
  names the same tag (as for `quality-checks.yml`).

## Affected Artifacts

- [MIL-007] — decides its criterion 2 and unlocks tasks 4 and 5.
- [UC-005] — the use case these workflows serve.
- [US-001] — US-001.16 and US-001.17 state their acceptance criteria.
- [ADR-0005] — the contract that this decision extends, unchanged.
- [ADR-0006] — raising a default tool version is breaking.

---

[MIL-007]: ../milestones/mil-007-cpp-csharp-quality-checks.md
[UC-005]: ../uc-005/uc.md
[US-001]: ../user-stories.md
[ADR-0005]: ./adr-0005-quality-check-contract.md
[ADR-0006]: ./adr-0006-release-process-and-version-pinning.md
[11cba35]: https://git.tirsystem.com/TirSystem/github-action/commit/11cba358b83cb7b6624f6b0956ae7b0c112d3692
