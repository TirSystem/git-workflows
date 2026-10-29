# ADR-0016: Validation of every repository as a scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0016 |
| CrossReference | [MIL-017], [MIL-018], [ADR-0005], [ADR-0015] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; reviewed (RC-100), accepted by the author in chat as stand-in for S01, not independent | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

The release workflow of [MIL-018] must refuse a release when the repository is
not green, and it must do so in any repository, not only in this one. The
validation of this repository (`validate-workflows.yml`) runs its own offline
tests under coverage and says nothing about other repositories. [MIL-017] asks
for the smallest check that makes sense everywhere: the workflow files and the
shell scripts of the repository, with one status of a fixed name.

A script decides only the criteria of the workflow checklist (`QC-WF-001`) that
are a fact about the file. Read from the checklist and from a first run on this
repository on 2026-10-29:

| Criterion | What the script checks | Decidable |
| --- | --- | --- |
| 2 | no workflow of the same name in `.gitea/workflows` and `.github/workflows` | yes |
| 3 | `name`, `on` and `jobs` exist | yes |
| 5 | every job and step has a name, unique within its job | yes, a warning: a job key is often descriptive enough |
| 7 | every job, or the workflow, declares `permissions` | yes |
| 8 | an action is pinned to a commit, an exact tag, or a moving major tag of `TirSystem` | yes |
| 9 | no `secrets.GITEA_*` or `secrets.GITHUB_*` (except `GITHUB_TOKEN`), no secret in a `run:` command | yes |
| 10 | no `inputs.*`, `*.event.*` or step output interpolated into a `run:` | yes |
| 14 | every job has `runs-on` and `timeout-minutes` | yes |
| 20 | a `run:` block has at most five lines, the limit of the YAML conventions | yes |
| 1, 4, 6, 11, 12, 13, 15 to 19, 21 to 24 | judgement, a header text, or a host behaviour | no |

A run on this repository found 1 error (`WF-20`: the `run:` of
`publish-wiki-pages.yml` has six lines), 11 warnings (`WF-5`: eleven jobs have no
`name`) and two shell scripts that `shfmt` 3.14.1 would change
(`tools/code-metrics.sh`, `tools/quality-checks.sh`); `shellcheck` found nothing.
The pinned `shfmt` (3.11.0.2) may format differently; the trial (task 6) reads
it. The licences, read from the sources on 2026-10-29: PyYAML 6.0.3 MIT,
`shellcheck-py` and `shfmt-py` (the Python packages that carry the binaries) MIT,
ShellCheck GPL-3.0 and shfmt BSD-3-Clause. The tools are run as separate
programs and nothing of them is copied into a repository, so the copyleft of
ShellCheck is not touched.

Options:

1. **A reusable workflow that each repository calls.** A caller file per
   repository, and a release that can only trust the repositories that call it.
2. **A scoped workflow with a fixed set of checks.** Nothing to add; the status
   exists in every repository, so the release can require it.
3. **`actionlint` instead of the own checks.** A complete linter for GitHub
   Actions, but a host-only context such as `gitea.*` needs its configuration
   (`QC-WF-001` criterion 6), and it checks syntax and types, not the criteria
   of the checklist (pinning, permissions, line limit); it was not run for this
   decision.
4. **The offline tests of this repository in every repository.** They test this
   repository's tools and mean nothing elsewhere.

## Decision

The validation is the scoped workflow `.gitea/scoped_workflows/validate.yml`,
named `Validate` with one job `validate`, which runs in every repository and
checks the workflow files and the tracked shell scripts with the script
`tools/validate_repo.py`.

The rules that follow from it:

- **The checks** are the criteria of the table above plus `shellcheck` and
  `shfmt -d` on every tracked `*.sh`. The workflow files are the `*.yml` and
  `*.yaml` files directly in `.gitea/workflows`, `.gitea/scoped_workflows` and
  `.github/workflows`. A file that is not valid YAML is a `WF-1` error.
- **What blocks:** every finding is an error, except `WF-5`, which is a warning.
  An error, or a tool that finds problems, fails the run.
- **The tools** are pinned in the script and installed with `pip` into a virtual
  environment: PyYAML 6.0.3, `shellcheck-py` 0.10.0.1 and `shfmt-py` 3.11.0.2.
  They are moved only in a release of this repository. `shfmt` reads the
  `.editorconfig` of the repository.
- **The status name** is `Validate / validate (<event>)`, where the event is
  `pull_request` or `push`. [MIL-017] task 1 reads the exact string the instance
  produces; [MIL-018] requires the one the push produces on the default branch.
- **Silencing:** `# validate-ignore: WF-8` on the line of a finding, or
  `# validate-ignore-file: WF-5` anywhere in a file; for shell the usual
  `# shellcheck disable=` and the `.editorconfig`. Only `WF-<n>` ids are read, so a reason may follow on the same line. The guide documents them.
- **Nothing to check:** a repository with no workflow file and no shell script
  ends green and prints "nothing to validate".
- The workflow has `permissions: contents: read` and no secret. It runs on a
  pull request, on a push to the default branch and manually, and the script is
  a file of this repository fetched at the current major tag ([ADR-0005]).
- The validation of this repository (`validate-workflows.yml`) stays; it is a
  different check with a different name.

## Consequences

**Positive:**

- Every repository gets the same status without a file, so the release of
  [MIL-018] can require it anywhere.
- A finding names the file, the line and the criterion of the checklist.
- A hand-written subset of the checklist is small, readable and tested offline.

**Negative:**

- The script reads YAML structure, not meaning: it cannot see that a `run:`
  hides a script behind `eval`, and it is not a replacement for `actionlint`.
- Every repository with a workflow of six lines in a `run:` or an unpinned action
  now fails until it is fixed or silenced; the trial counts them.
- The tools are fetched from PyPI at run time (about ten seconds), so a run fails
  as `[tool]` when it is not reachable.
- Two sets of rules to keep in step: the checklist and the script.

## Affected Artifacts

- [MIL-017] — the milestone this decision belongs to; tasks 3 to 7 follow it.
- [MIL-018] — requires the status name decided here.
- [ADR-0005] — the script is a file, tools are pinned, failures have categories.
- [ADR-0015] — the same delivery: a scoped workflow that acts without a caller.

---

[MIL-017]: ../milestones/mil-017-scoped-validation-workflow.md
[MIL-018]: ../milestones/mil-018-scoped-release-workflow.md
[ADR-0005]: ./adr-0005-quality-check-contract.md
[ADR-0015]: ./adr-0015-semgrep-scoped-workflow.md
