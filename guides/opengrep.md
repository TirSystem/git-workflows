# Static security scan with OpenGrep

How a software engineer reads and handles the result of the scoped workflow
`opengrep.yml`. It scans the repository with OpenGrep and its community rules,
without an account, and shows the findings on the pull request. It changes no
file and has no secret. Its decision is ADR-0015 in this repository; when a
repository uses it is set out in the
[adoption rules](adoption-rules.md#opengrep).

## Nothing to add

The workflow is scoped: the instance runs it in every repository of the
organization, on a pull request, on a push to `main` and by hand. A repository
adds no file. OpenGrep v1.33.0 is one executable (`opengrep_manylinux_x86`),
downloaded from the GitHub release and checked against a pinned sha256; there is
no `pip` and no account. Only Linux x86_64 runners are supported. OpenGrep has
no registry and no metrics option. The rules are the repository
`opengrep/opengrep-rules`, pinned to one commit and fetched with git at run
time: the directories `python`, `bash`, `c`, `csharp`, `yaml`, `generic`,
`dockerfile`, `javascript`, `typescript`, `terraform`, `go` and `java`. The only
outbound host is `github.com`, and only git-tracked files are scanned. No source
code leaves the runner.

## What fails the run

| Severity | In the log | Fails the run |
| --- | --- | --- |
| `ERROR` | `::error file=...,line=...::[finding] rule-id: message` | Yes |
| `WARNING` | `::warning file=...,line=...::` | No |
| `INFO` | `::notice file=...,line=...::` | No |

The job summary lists up to 50 findings with the rule and the place. A
repository where no tracked file is scanned ends green and prints "nothing to
scan". A failure of the tool itself is `[tool]`: the download failed, the hash
did not match, the rules could not be fetched, or the report cannot be read; run
it again before looking for a finding.

## Silencing a finding

A false positive is silenced where it is, and the reason belongs in the pull
request:

- On the line: `# nosemgrep: rule-id` (the comment form of the language), with
  the rule id exactly as the log prints it (the id starts with the path of the
  rules checkout, so copy it from the CI log, not from a local run). OpenGrep
  keeps the Semgrep comment syntax; checked on 2026-10-29: the id silences that
  rule only, and `# nosemgrep` without an id silences every rule on the line.
- For paths: a `.semgrepignore` file at the root of the repository, with the
  patterns of a `.gitignore`, for generated code, vendored code and fixtures.

A finding that is real is fixed, not silenced. The rules are old (the last
commit is from January 2025) and noisy on documentation, where the shell rules
fire on code samples in Markdown; expect to silence false positives per
repository.

## A trial on this repository

A trial run took about 66 seconds and scanned 243 files. It gave 111 findings:
3 `ERROR` in `tools/` (two `dangerous-subprocess-use-audit` and one
`use-defused-xml`), 10 `WARNING` and 98 `INFO`, mostly shell rules on code
samples in Markdown. Five files had parse errors, which do not fail the run. On
this repository the check would therefore fail until those three findings are
fixed or silenced.

## Mark the check as required

Setting the check as required in the branch protection is what blocks the merge
on an `ERROR` finding. It is a branch protection setting, so the repository
owner does it. Warnings never block.

## The licence

OpenGrep is LGPL-2.1. The rules repository is under LGPL-2.1 with the Commons
Clause, which forbids selling the software as a service for a fee, and its
README says the rules are intended for research, testing and benchmarking. The
workflow fetches them at run time and never stores them in a repository. Use for
a service, or a change of that licence, needs a new decision.
