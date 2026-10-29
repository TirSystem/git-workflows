<!-- Generated from guides/validate.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`guides/validate.md`](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/validate.md). Changes made here are overwritten the next time the wiki is published.

**English** · [Dansk](Validate-da) · [Bahasa Melayu](Validate-ms)

# Validation of workflow files and shell scripts

How a software engineer reads and handles the result of the scoped workflow
`validate.yml`. It checks the workflow files and the tracked shell scripts of the
repository against the criteria of the workflow checklist (`QC-WF-001`) that a
script can decide, and runs `shellcheck` and `shfmt` on the shell scripts. It
changes no file and has no secret. Its decision is ADR-0016 in this repository;
when a repository uses it is set out in the
[adoption rules](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/adoption-rules.md#validate).

## Nothing to add

The workflow is scoped: the instance runs it in every repository of the
organization, on a pull request, on a push to `main` and by hand. A repository
adds no file. It has `permissions: contents: read` and no secret. It checks out
the repository, fetches the script `tools/validate_repo.py` from
`TirSystem/git-workflows` at `v2`, installs the tools into a virtual environment
with `pip` and runs the checks.

- **Workflow files** are the `*.yml` and `*.yaml` files directly in
  `.gitea/workflows`, `.gitea/scoped_workflows` and `.github/workflows`.
- **Shell scripts** are the tracked `*.sh` files.

A repository with neither ends green and prints "nothing to validate".

## What is checked

Each finding names the file, the line and the criterion:
`::error file=...,line=...::[WF-8] message`.

| Criterion | What it means |
| --- | --- |
| `WF-1` | The file is not valid YAML. |
| `WF-2` | A workflow of the same name exists in `.gitea/workflows` and in `.github/workflows`. |
| `WF-3` | The workflow lacks `name`, `on` or `jobs`. |
| `WF-5` | A job or a step has no name, or a name is used twice in a job. A warning. |
| `WF-7` | Neither the workflow nor the job declares `permissions`. |
| `WF-8` | An action is not pinned to a commit, an exact tag, or a moving major tag of the `TirSystem` organisation; a branch is rejected. |
| `WF-9` | The workflow reads `secrets.GITEA_*` or `secrets.GITHUB_*` (except `GITHUB_TOKEN`), or puts a secret in a `run:` command. |
| `WF-10` | A `run:` interpolates `inputs.*`, `*.event.*` or a step output. |
| `WF-14` | A job lacks `runs-on` or `timeout-minutes`. |
| `WF-20` | A `run:` block has more than five lines; move the logic to a script file. |

The other criteria of `QC-WF-001` are judgement, a header text or a host
behaviour, and are not checked here. The script reads the structure of the YAML,
not its meaning; it is not a replacement for `actionlint`.

## What fails the run

| Finding | In the log | Fails the run |
| --- | --- | --- |
| Any criterion except `WF-5` | `::error file=...,line=...::[WF-8] ...` | Yes |
| `WF-5` | `::warning file=...,line=...::[WF-5] ...` | No |
| `shellcheck` or `shfmt -d` finds a problem | the tool's own output | Yes |

A failure of the tool itself is `[tool]`: the packages could not be installed
(PyPI was not reachable) or the tool did not start; run it again before looking
for a finding.

## The status name

The status that the pull request and the commit show is
`Validate / validate (<event>)`, where the event is `pull_request` or `push`. The
release workflow requires the one the push produces on the default branch. The
exact string the instance produces is still to be verified (MIL-017, task 1).

## Silencing a finding

A false positive is silenced where it is, and the reason belongs in the pull
request:

- On the line: `# validate-ignore: WF-8` (several criteria are separated by a
  comma).
- For the whole file: `# validate-ignore-file: WF-5`, anywhere in the file.
- Shell: the usual `# shellcheck disable=SC2086` before the command.
- Formatting of shell: `shfmt` reads the `.editorconfig` of the repository
  (`indent_style`, `indent_size`, `shell_variant`); set it there.

A finding that is real is fixed, not silenced.

## Mark the check as required

Setting the check as required in the branch protection is what blocks the merge
on an error. It is a branch protection setting, so the repository owner does it.
A warning never blocks.

## The pinned tools and their licences

The tools are pinned in the script and moved only in a release of this
repository. The licences were read on 2026-10-29.

| Tool | Version | Licence |
| --- | --- | --- |
| PyYAML | 6.0.3 | MIT |
| `shellcheck-py` (carries the binary) | 0.10.0.1 | MIT |
| ShellCheck | the one in `shellcheck-py` | GPL-3.0 |
| `shfmt-py` (carries the binary) | 3.11.0.2 | MIT |
| shfmt | the one in `shfmt-py` | BSD-3-Clause |

The tools run as separate programs and nothing of them is copied into a
repository, so the copyleft of ShellCheck is not touched.

## A trial on this repository

A local run on 2026-10-29 found:

- 1 error: `WF-20`, the `run:` of `publish-wiki-pages.yml` has six lines.
- 11 warnings: `WF-5`, jobs without a name.
- `shfmt` 3.14.1 would change `tools/code-metrics.sh` and
  `tools/quality-checks.sh`; the pinned 3.11.0.2 is read in the trial on the
  instance, and it may format differently.
- `shellcheck` found nothing.

On this repository the check would therefore fail until the `WF-20` error is
fixed or silenced.
