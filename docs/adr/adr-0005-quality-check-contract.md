# ADR-0005: Contract of the shared quality-check workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0005 |
| CrossReference | [MIL-003], [UC-005], [US-001], [ADR-0004] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-11 | Accepted | Jens Tirsvad Nielsen | S01 | Added the input tools-ref: the shell steps moved to a script file fetched at that ref (RC-051) | [670f0ac] |
| 2026-10-14 | Proposed | Jens Tirsvad Nielsen | S01 | Amendment: the default `tools-ref` is the current major tag (MIL-011) | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

MIL-003 offers one workflow that any repository calls to run lint, format and
type checks. Before it is built (task 3) its inputs and the meaning of a pass
and a fail must be fixed, because consumers in four organizations will depend
on them and MIL-004 will version them. Facts found on 2026-10-10:

- The runner image (Ubuntu 24.04, Python 3.12, `git`, Node.js, `jq`, `make`,
  run as `root`) has **none** of ruff, mypy, pytest, shellcheck or shfmt.
- PyPI is reachable, and a virtual environment installs all four tools with
  pinned versions: `ruff` 0.6.9, `mypy` 1.11.2, `shellcheck-py` 0.10.0.1
  (ShellCheck 0.10.0) and `shfmt-py` 3.11.0.2 (shfmt 3.11.0).
- Each tool exits non-zero on a finding and prints `path:line` and a message.
  `shellcheck` also exits 1 on an empty file, so a language with no files must
  be skipped before the tool runs.
- Reusable workflows work from the same repository and from other
  organizations (issue #15). Secrets passing is untested, and the checks need
  none.
- The conventions name the tools: ruff and `mypy --strict` for Python
  (QC-PY-001) and shellcheck and shfmt for shell (QC-SH-001).

Options for the shape of the workflow:

1. **One reusable workflow with a `languages` input** that selects the tool
   sets, defaults that work with no configuration, and one version input per
   tool.
2. **One reusable workflow per language** (`python-checks.yml`,
   `shell-checks.yml`). Simple, but a mixed repository calls two workflows and
   the contract exists twice.
3. **Detect the languages from the files and take no inputs.** Zero
   configuration, but a repository cannot opt out of a tool, and versions
   change only with the workflow.
4. **The consumer passes its own commands.** Most flexible, but it is not a
   shared check any more and defeats the point of a contract.

## Decision

The shared workflow `quality-checks.yml` is one reusable workflow with the
inputs `languages` (a comma list of `python` and `shell`, default both),
`working-directory` (default `.`), one version input per tool whose
defaults are the pinned versions above, and `tools-ref` (default `v1`, the
tag or branch from which the workflow fetches its script
`tools/quality-checks.sh`), and it installs the tools from PyPI into a virtual
environment. A call at an exact tag is pinned completely only when `tools-ref`
names the same tag; with the default the script follows the major tag. A run passes when every selected tool exits 0 and
fails when any exits non-zero, and a language with no files is skipped with a
notice and counts as a pass.

The rules that follow from it:

- **Python:** `ruff check`, `ruff format --check` and `mypy --strict`, run on
  the files under `working-directory`.
- **Shell:** the tracked `*.sh` files are checked with `shellcheck` and
  `shfmt -d`.
- **Configuration:** projects configure the tools in the standard way
  (`pyproject.toml`, `.shellcheckrc`, `.editorconfig`); the workflow adds none
  and changes no file.
- **Reporting:** each tool runs in its own log group named after the tool, and
  its own output carries `path:line` and the message; the job status is the
  pull request status.
- **Out of scope for the first version:** running the project's tests
  (`pytest` needs the project's dependencies), auto-fixing, and other
  languages.

## Consequences

**Positive:**

- A repository gets the checks with one `uses:` and no configuration, and a
  mixed repository gets both language sets from one call.
- Tool versions are explicit and reviewed, so a new tool release cannot turn
  every consumer red overnight.
- A failure is read from the tool's own message, so the workflow needs no
  parser of its own.

**Negative:**

- Every run installs the tools from PyPI (about half a minute) and depends on
  PyPI being reachable; caching is not part of the first version.
- Projects that need their tests or their own dependencies in the type check
  (`mypy` with third-party stubs) must configure that themselves or wait for a
  later version.
- `mypy --strict` on an existing codebase is likely to fail at first; a
  project that cannot meet it has to configure the tool, which weakens the
  shared meaning of "pass".
- Pinned versions need a release (MIL-004) to move; until then they are
  updated by changing the workflow on `main`.
- **Security:** the tools are downloaded from PyPI on every run and execute
  with the consumer's repository content on a runner that runs as `root`.
  Versions are pinned but the packages are not hash-pinned, so a
  compromised release of one of the four packages would reach every
  consumer; hash pinning is a later hardening step.

## Affected Artifacts

- [MIL-003] — tasks 3 to 5 (issues #17 to #19) implement, adopt and document
  this contract.
- [UC-005] — the use case this contract serves.
- [US-001] — stories US-001.09 and US-001.10 state its acceptance criteria.
- [ADR-0004] — the same pattern of a shared scoped or reusable workflow with an
  explicit gate; this ADR does not change it.


## Amendment (MIL-011)

The default of the input `tools-ref` in the quality-check contract is the current major tag, defined once in the file
`MAJOR_TAG` of this repository (`v2` from release 2.1.1), and no longer `v1`. A default must
name a tag that holds the script the workflow runs; a test checks it. Callers at `@v1` are
not affected: the `v1` tag keeps the `v1` workflow files.

---

[MIL-003]: ../milestones/mil-003-quality-checks.md
[UC-005]: ../uc-005/uc.md
[US-001]: ../user-stories.md
[ADR-0004]: ./adr-0004-shared-wiki-publishing-opt-in.md
[385d2fb]: https://git.tirsystem.com/TirSystem/github-action/commit/385d2fb7cb9be1fdc8fd3503d0af624fa38eafc7
[670f0ac]: https://git.tirsystem.com/TirSystem/github-action/commit/670f0ac469043bb166c84290c0dbf62b4908e3cc
