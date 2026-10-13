# Reading C and C++ quality-check results

How a software engineer calls the shared C and C++ quality checks, reads a
failed run and makes it pass. The workflow format-checks and statically checks
the C and C++ files of a repository with clang tools at exact versions, changes
no file and needs no secret. Its contract is ADR-0008 in this repository.

## Calling the workflow

```yaml
name: Quality C++

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  quality:
    permissions:
      contents: read
    uses: TirSystem/github-action/.gitea/workflows/quality-checks-cpp.yml@v1
    with:
      std: c++20
```

| Input | Default | Meaning |
| --- | --- | --- |
| `working-directory` | `.` | Directory, relative to the repository root, whose files are checked |
| `std` | `c++20` | C++ standard given to clang-tidy when there is no compile database, such as `c++17` or `gnu++20` |
| `compile-commands-dir` | empty | Directory, relative to the repository root, with a `compile_commands.json` that your pipeline built before the call; when set, clang-tidy uses it and ignores `std` |
| `clang-format-version` | `23.1.3` | Exact version of the clang-format package |
| `clang-tidy-version` | `22.1.8` | Exact version of the clang-tidy package |
| `tools-ref` | `v1` | Tag or branch of `TirSystem/github-action` from which the script `tools/quality-checks-cpp.sh` is fetched |

Reference the workflow at the major tag (`@v1`) or at an exact tag, never at
`main`. A call at an exact tag is pinned completely only when `tools-ref` names
the same tag. See the upgrade guide. The tool versions are exact: a newer
version of a tool is a new release of this repository, not a silent change.

## What the repository needs

- A `.clang-format` in the working directory or in a directory above it, up to
  the top of the repository. Without one the run fails with `[configuration]`
  and no tool runs.
- Optionally a `.clang-tidy` with the checks of the project (for example the
  C++ Core Guidelines). Without one the workflow runs the compiler diagnostics
  and the static analyzer (`clang-diagnostic-*` and `clang-analyzer-*`),
  because clang-tidy itself enables no check when there is no configuration.
- For precise static checks, a compile database: build it first (for example
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`) and pass
  `compile-commands-dir: build`. The workflow does not build your project.

## What is checked

| Files | Tool | What it reports |
| --- | --- | --- |
| tracked `*.c`, `*.cc`, `*.cpp`, `*.cxx`, `*.h`, `*.hh`, `*.hpp`, `*.hxx` | `clang-format --dry-run -Werror` | formatting that differs from `.clang-format` |
| the same files | `clang-tidy` | findings of the checks of `.clang-tidy` (or of `clang-diagnostic-*` and `clang-analyzer-*` without one); `*.c` files are checked as C17, the other files as the C++ standard of `std`; every finding is an error (`--warnings-as-errors=*`), so a warning fails the run |

Untracked files are not checked. A repository without these files passes with a
notice. There is no `cppcheck`: only an old version of it is available as a
package, and old tools are not run (ADR-0008).

## Reading a run

1. Open the status check on the pull request, then the job `quality-checks-cpp`.
2. Each tool has its own log group. Every tool runs even when an earlier one
   failed, so one run shows all findings.
3. A tool ends with `PASS <tool>` or `FAIL <tool>`; the last line of a failed
   run names them: `Quality checks failed: clang-format`.
4. A finding is written by the tool itself as `path:line:column: message`.
   `clang-format` prints paths relative to `working-directory`; `clang-tidy`
   prints absolute paths in the workspace of the runner
   (`/workspace/<owner>/<repo>/main.cpp:5:18`).

## Typical failures and fixes

| Tool | What the log shows | Fix |
| --- | --- | --- |
| `clang-format` | `code should be clang-formatted [-Wclang-format-violations]` | Run `clang-format -i <file>` with the same version and commit |
| `clang-tidy` | `warning: ... [modernize-use-nullptr]` | Fix the code, or switch the check off in `.clang-tidy` with a reason |
| `clang-tidy` | `error: 'x.h' file not found` | Build the compile database and set `compile-commands-dir`, or add the include path to it |

To reproduce a run on your machine, install the same versions:

```bash
python3 -m venv .qc
.qc/bin/pip install clang-format==23.1.3 clang-tidy==22.1.8
git ls-files '*.cpp' '*.hpp' | xargs .qc/bin/clang-format --dry-run -Werror
```

## When the workflow itself fails

| Message | Cause | Fix |
| --- | --- | --- |
| `[configuration] std '<x>' is not a C++ standard` | `std` is not like `c++20` or `gnu++20` | Correct the input |
| `[configuration] ... is not an exact version` | A tool version is a range, a channel or empty | Give an exact version such as `23.1.3` |
| `[configuration] working-directory must be a relative path inside the repository.` | An absolute path or `..` | Use a path inside the repository |
| `[configuration] No .clang-format found` | The project has no style file | Add a `.clang-format` |
| `[configuration] compile-commands-dir '<x>' has no compile_commands.json` | The database was not built before the call | Build it in an earlier step of the job or in a job it depends on |
| The install step fails | PyPI or the runner network is unreachable | Re-run the job; see [troubleshooting.md](troubleshooting.md) |
