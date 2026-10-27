<!-- Generated from guides/quality-checks.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`guides/quality-checks.md`](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/quality-checks.md). Changes made here are overwritten the next time the wiki is published.

English | [Dansk](QualityChecksPythonShell.da) | [Bahasa Melayu](QualityChecksPythonShell.ms)

# Reading quality-check results

How a software engineer calls the shared quality checks, reads a failed run and
makes it pass. The workflow lints and format-checks the Python and shell files
of a repository with pinned tools, changes no file and needs no secret. Its
contract is ADR-0005 in this repository.

## Calling the workflow

```yaml
name: Quality

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  quality:
    permissions:
      contents: read
    uses: TirSystem/github-action/.gitea/workflows/quality-checks.yml@v1
    with:
      languages: python,shell
```

| Input | Default | Meaning |
| --- | --- | --- |
| `languages` | `python,shell` | Comma list of the languages to check |
| `working-directory` | `.` | Directory, relative to the repository root, whose files are checked |
| `ruff-version` | `0.6.9` | Version of ruff |
| `mypy-version` | `1.11.2` | Version of mypy |
| `shellcheck-py-version` | `0.10.0.1` | Version of the shellcheck-py package (ShellCheck 0.10.0) |
| `shfmt-py-version` | `3.11.0.2` | Version of the shfmt-py package (shfmt 3.11.0) |
| `tools-ref` | `v2` | Tag or branch of `TirSystem/github-action` from which the script `tools/quality-checks.sh` is fetched |

Reference the workflow at the major tag (`@v1`) or at an exact tag
(`@v1.0.0`), never at `main` and never at the branch of a pull request: that
branch is deleted when the pull request is merged and the reference stops
working. See the upgrade guide for what each choice receives.

The workflow file calls a script of this repository, fetched at `tools-ref`. A
call at an exact tag is pinned completely only when `tools-ref` names the same
tag, for example `@v1.0.1` with `tools-ref: v1.0.1`; with the default the
script follows `v1`.

## What is checked

| Language | Files | Tools |
| --- | --- | --- |
| Python | tracked `*.py` under the working directory | `ruff check`, `ruff format --check`, `mypy --strict` |
| Shell | tracked `*.sh` under the working directory | `shellcheck`, `shfmt -d` |

Untracked files are not checked. A language without files is skipped with a
notice and counts as a pass. Project tests are not run.

## Reading a run

1. Open the status check on the pull request, then the job `quality-checks`.
2. Each tool has its own log group named after it. Every tool runs even when an
   earlier one failed, so one run shows all findings.
3. A tool ends with `PASS <tool>` or `FAIL <tool>`. The last line of a failed
   run names the tools that failed:
   `Quality checks failed: ruff check shellcheck`.
4. A finding is written by the tool itself as `path:line:column: CODE message`.
   Paths are relative to `working-directory`.

## Typical failures and fixes

| Tool | What the log shows | Fix |
| --- | --- | --- |
| `ruff check` | `F401 ... imported but unused` | Remove the import, or use it |
| `ruff format --check` | `Would reformat: <file>` | Run `ruff format <file>` and commit |
| `mypy --strict` | `Function is missing a type annotation` | Add parameter and return types |
| `shellcheck` | `SC2086 ... Double quote to prevent globbing` | Quote the expansion: `"$1"` |
| `shfmt -d` | a diff of `<file>.orig` and `<file>` | Run `shfmt -w <file>` with the project's options and commit |

To reproduce a run on your machine, install the same versions and run the
commands of the table:

```bash
python3 -m venv .qc
.qc/bin/pip install ruff==0.6.9 mypy==1.11.2 shellcheck-py==0.10.0.1 shfmt-py==3.11.0.2
.qc/bin/ruff check . && .qc/bin/ruff format --check .
```

## Configuring the tools

The workflow adds no configuration; it runs from the repository root, so the
files of the project apply:

| Tool | File | Example |
| --- | --- | --- |
| ruff | `pyproject.toml` | `[tool.ruff]` with `line-length = 100` |
| mypy | `pyproject.toml` | `[tool.mypy]` with per-module `ignore_missing_imports` |
| shellcheck | `.shellcheckrc` | `external-sources=true` and `source-path=SCRIPTDIR` |
| shfmt | `.editorconfig` | `[*.sh]` with `indent_size = 2` and `switch_case_indent = true` |

shfmt follows a project's style only through `.editorconfig`. A shell project
that formats with its own flags (for example `shfmt -i 2 -ci`) should expect a
first formatting failure and express the flags there; in the first adoption
(RepoFoundry) one line, `switch_case_indent = true`, was enough and no script
changed.

## When the workflow itself fails

| Message | Cause | Fix |
| --- | --- | --- |
| `[configuration] Unknown language '<x>'` | `languages` has a value other than `python` or `shell` | Correct the input |
| `[configuration] working-directory must be a relative path inside the repository.` | An absolute path or `..` | Use a path inside the repository |
| `[configuration] working-directory '<x>' does not exist.` | The directory is not in the repository | Correct the input |
| The install step fails | PyPI or the runner network is unreachable | Re-run the job; see [troubleshooting.md](Troubleshooting) |
