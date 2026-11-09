# ADR-0015: Static security scan with OpenGrep as a scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0015 |
| CrossReference | [MIL-016], [ADR-0005], [ADR-0013], [RC-110] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version: OpenGrep instead of Semgrep, on the owner's instruction in chat; reviewed (RC-098), accepted by the author in chat as stand-in for S01, not independent | [d4901e0] |
| 2026-11-09 | Proposed | Jens Tirsvad Nielsen | S01 | Amendment (MIL-016 task 8): the script passes only the rule files of the languages the repository has, because a run on the runner took more than 5 minutes; reviewed (RC-110), prepared by the AI in supervised mode | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

GitHub offers CodeQL and Code Quality; the Gitea instance has no counterpart
and no SARIF upload. Objective O8 of the Business Case asks that security
findings are shown to the author of a pull request, for free and in every
repository. [MIL-016] was written for Semgrep Community Edition. The owner
asked for [OpenGrep](https://github.com/opengrep/opengrep), a fork of Semgrep
CE, instead. Task 2 of the milestone ran both on this repository on 2026-10-29,
to read the facts instead of recalling them:

| Fact | Semgrep CE 1.182.1 | OpenGrep 1.33.0 |
| --- | --- | --- |
| Licence of the engine | LGPL-2.1-or-later | LGPL-2.1 |
| Install | `pip install`, 77 seconds in a container | one executable `opengrep_manylinux_x86` (46 MB) from the GitHub release, signed (`.sig`, `.cert`); no pip, no account |
| Rules | `p/default` (330 rules) from the registry at `semgrep.dev`, under the Semgrep Rules License v1.0 (internal business use only, no distribution) | no registry; the repository `opengrep/opengrep-rules`, a fork of `semgrep-rules` made in December 2024, last commit 2025-01-26, under LGPL-2.1 with the Commons Clause (no selling of the software); its README says the rules are for "research, testing & benchmarking" |
| Telemetry | `--metrics=off` | no `--metrics` option in `opengrep scan --help`; traffic not captured |
| Scan of this repository | 612 files in 99 seconds, 31 findings | 243 files (only git-tracked files) in 66 seconds with 12 rule directories, 111 findings (3 `ERROR`, 10 `WARNING`, 98 `INFO`), 5 parse errors |
| Findings here | 1 `ERROR` (in the untracked `.env`), 30 `WARNING` | 3 `ERROR` in `tools/` (two `dangerous-subprocess-use-audit`, one `use-defused-xml`), 10 `WARNING`; the `INFO` are shell rules firing on code samples in Markdown |
| Exit code | `--error` exits 1 for a finding of any severity | the severity is in the JSON report of both |
| Outbound hosts | PyPI, `semgrep.dev` | `github.com` (binary and rules); not captured, to be recorded in the trial (task 7) |

Pointing `--config` at the whole rules checkout fails with
`InvalidRuleSchemaError` (it holds non-rule YAML), so the rule directories are
named one by one.

**Amendment of 2026-11-09 (MIL-016 task 8).** The first runs on the runner of
the instance were slow. The scan step of a repository with 81 tracked files was
still running after 5 minutes 28 seconds (the install step took 4 seconds),
which breaks criterion 1 of [MIL-016] (a run ends in at most 5 minutes). The
same scan took 23 seconds on a developer machine with 20 cores, and 2 minutes
39 seconds with one job. The time is set by the number of rules (about 1,700 in
the twelve directories) and the cores of the runner, not by the repository.
Excluding `docs/` with a `.semgrepignore` was measured and changed nothing (no
finding there; 24.9 seconds against 25.5). Choosing whole rule directories by
the languages present saved about 15 percent, because `csharp`, `go`, `java` and
`javascript` each hold a few rules with `languages: [generic]`, which apply to
any file. Options for the amendment:

1. **Keep all rules.** The run stays slow on a runner with few cores.
2. **Skip whole rule directories** of languages the repository does not have.
   Safe, but it skipped only `c`, `typescript` and `terraform` here.
3. **Skip rule files** whose languages the repository does not have, and keep
   every rule that is generic, of an unknown language or unreadable.
4. **Fewer rule directories for every repository.** A smaller scan for all,
   decided by the organisation, with a loss of coverage.

Options:

1. **A reusable workflow that each repository calls.** A caller file per
   repository for a check that has no setting a repository decides.
2. **A scoped workflow with OpenGrep.** Nothing to add; no registry, no account
   and no vendor service; the engine and the rules are open source and can be
   pinned to a release and a commit.
3. **A scoped workflow with Semgrep CE.** A newer, maintained rule set from the
   registry, but under a licence that allows internal use only, and the engine
   by a vendor that offers the paid product beside it.
4. **CodeQL.** The CLI licence limits its use to open-source code and research.

## Decision

The static security scan is the scoped workflow
`.gitea/scoped_workflows/opengrep.yml`, which runs OpenGrep in every
repository with a pinned release and a pinned checkout of its rules.

The rules that follow from it:

- The settings are fixed: OpenGrep `v1.33.0`, the Linux x86_64 executable
  checked against a pinned sha256, and the rules of `opengrep/opengrep-rules` at
  the pinned commit `f1d2b562b414783763fd02a6ed2736eaed622efa`, fetched with
  `git` at run time and never stored in a repository. The rule directories are
  `python`, `bash`, `c`, `csharp`, `yaml`, `generic`, `dockerfile`, `javascript`,
  `typescript`, `terraform`, `go` and `java`. Version, hash, commit and
  directories are constants of `tools/opengrep_scan.py`, moved only in a release
  of this repository; a repository cannot choose others. Of these directories
  the script passes only the rule files that apply (option 3 of the amendment of
  2026-11-09): a rule file is kept when any of its languages has a file in the
  repository, or when its language is `generic`, `regex`, `none`, not in the
  script's table of file extensions, or cannot be read; the `generic` directory
  is used whole. The kept files are copied to a work directory under the OpenGrep
  home, which is passed as `--config`, and the script prints the kept and skipped
  counts per directory and adds them to the job summary. Other platforms than
  Linux x86_64 fail as `[configuration]`.
- The script reads the JSON report. A finding of severity `ERROR` fails the run;
  `WARNING` and `INFO` are printed as warnings and notices with file and line
  and do not fail it. A download whose hash differs, a failed rules fetch, an
  exit code other than 0 or an unreadable report fails as `[tool]`.
- A repository where OpenGrep scans no file ends green and says "nothing to
  scan". Only git-tracked files are scanned.
- The workflow has `permissions: contents: read` and no secret. It runs on a
  pull request, on a push to `main` and manually.
- Findings are shown in the log, the annotations and the job summary. Gitea has
  no SARIF upload and the workflow does not comment on the pull request.
- A finding is silenced where it is: `# nosemgrep: <rule-id>` on the line (the
  syntax OpenGrep keeps), or a `.semgrepignore` file for paths. The guide
  documents both.
- The script is a file of this repository, fetched at the current major tag
  ([ADR-0005]), and prints `::error::[category] message` for a failure, with the
  categories `configuration`, `tool` and `finding`.
- A rule file is never dropped on a doubt: a language the script does not know,
  a missing `languages:` or an unreadable file keeps the rule. Measured with
  OpenGrep 1.33.1 and the pinned rules, the findings equal those of all twelve
  directories on this repository (34) and on a second one (12), and the run takes
  18.5 and 14.8 seconds instead of 25.5 and 23.2; with one job the second
  repository takes 1 minute 15 seconds instead of 2 minutes 39.
- The licence of the rules allows internal use and forbids selling the software;
  the scan is the organisation's own quality check, which S01 confirms when
  accepting this record.

## Consequences

**Positive:**

- Every repository gets a security scan with no file added, no account and no
  vendor registry; the engine and the rules are open source and pinned, so a run
  is reproducible.
- A finding names the rule, file and line in the log of the pull request.
- The scan reads tracked files only, so an untracked secret file is not read.

**Negative:**

- The rules are a fork from December 2024 and the repository has had no commit
  since January 2025; new weaknesses are not covered, and the rules are noisy on
  documents (98 `INFO` findings here). A newer rule set needs a new decision, or
  rules written by the organisation.
- On this repository the check would fail on 3 `ERROR` findings until they are
  fixed or silenced in the trial (task 7).
- `github.com` must be reachable at run time (binary and rules), and a scan
  costs about two minutes of runner time per push and pull request in every
  repository.
- The filter reads the structure of the rule files (a top-level `rules:` and
  `languages:`) and keeps a table of file extensions; moving the rules commit
  needs the comparison of findings to be repeated, and a language missing from
  the table keeps its rules, which costs time but never coverage.
- The community rules report patterns, not proven vulnerabilities; false
  positives are silenced by hand, per repository.
- The README of the rules says they are for research, testing and benchmarking,
  and the project is young; a change of the project or of the licence needs a new
  decision.

## Affected Artifacts

- [MIL-016] — the milestone this decision belongs to; its text still says
  Semgrep and is changed once S01 accepts the change of tool.
- [ADR-0005] — the script is a file, the tool is pinned, failures have categories.
- [ADR-0013] — the same delivery: a scoped workflow that acts without a caller.

---

[MIL-016]: ../milestones/mil-016-semgrep-scoped-workflow.md
[ADR-0005]: ./adr-0005-quality-check-contract.md
[ADR-0013]: ./adr-0013-wiki-publishing-scoped-workflow.md
[RC-110]: ../sqa/reviews/rc-110-adr-0015-rule-selection.md
[d4901e0]: https://git.tirsystem.com/TirSystem/git-workflows/commit/d4901e026d9fdf0c3a9fb86f46a59bf1f73dc53b
