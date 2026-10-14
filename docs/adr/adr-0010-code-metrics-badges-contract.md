# ADR-0010: Contract of the code metrics and coverage badges workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0010 |
| CrossReference | [MIL-010], [UC-008], [US-001], [ADR-0005], [ADR-0006] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | Accepted | Jens Tirsvad Nielsen | AI as stand-in for S01 | The report reaches the workflow as an artifact of the caller's run (input `coverage-artifact`), because a called workflow runs in its own job; reviewed (RC-073) | [0dc5132] |
| 2026-10-14 | Proposed | Jens Tirsvad Nielsen | S01 | Amendment: the default `tools-ref` is the current major tag (MIL-011) | [eaa0e30] |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

MIL-010 adds a reusable workflow that shows the size of a repository's code
and its test coverage as badges (UC-008, US-001.18 to US-001.20). ADR-0005
defines the contract of the quality-check workflow: inputs with working
defaults, a pinned version per tool, a failure that names the cause, and a
script file of this repository, fetched at `tools-ref`, that the workflow runs.
Decisions the user took in chat on 2026-10-14 bound this one: the counter is a
Python script of this repository with no dependency outside the standard
library, the delivery is a reusable workflow, the badges are committed to a
`badges` branch, there are three badges (code files, lines of code, coverage),
and the coverage report is read in the Cobertura XML format.

Options for the counter:

1. **Wrap `cloc`, `tokei` or `scc`.** Many languages, mature rules, but a tool
   to install and pin on every run and a download from outside the instance.
2. **A Python script of this repository.** No install, fully tested offline,
   and the rules are ours; fewer languages and simple scanning rules.

Options for the delivery of the badges: a run artifact (disappears and has no
stable URL), a file on the default branch (a commit per change on the branch
that protects the code), or a dedicated branch (stable raw URL, no effect on
the default branch).

Facts: the job of a reusable workflow runs on `ubuntu-latest` with `python3`
3.12; a push made with the token of a run does not start another run; a
workflow checks the shared scripts out into the workspace (`shared-scripts`),
so the counter must not count them.

## Decision

A reusable workflow `code-metrics.yml` runs three script files of this
repository, fetched at its input `tools-ref` (default `v1`): `tools/count_loc.py`
counts the code, `tools/badges.py` reads the coverage report and writes the
badges, and `tools/code-metrics.sh` validates the inputs, calls both and
publishes the badge files to the `badges` branch of the calling repository
with the token of the run (`contents: write`, no other permission).

The rules that follow from it:

- **Code file.** A file under `working-directory` whose extension is in the
  language table below, that is not excluded, and that contains no NUL byte
  (it is text; it is read as UTF-8 and invalid bytes are replaced). Its
  language comes from the extension. A file with a code extension but no
  line is still a code file.
- **Languages and comments (first version).**

  | Language | Extensions | Line comment | Block comment |
  | --- | --- | --- | --- |
  | Python | `.py` | `#` | none |
  | Shell | `.sh`, `.bash` | `#` at the start of a word | none |
  | PowerShell | `.ps1`, `.psm1` | `#` | `<#` ... `#>` |
  | C | `.c`, `.h` | `//` | `/*` ... `*/` |
  | C++ | `.cc`, `.cpp`, `.cxx`, `.hh`, `.hpp` | `//` | `/*` ... `*/` |
  | C# | `.cs` | `//` | `/*` ... `*/` |
  | Java | `.java` | `//` | `/*` ... `*/` |
  | JavaScript | `.js`, `.mjs`, `.jsx` | `//` | `/*` ... `*/` |
  | TypeScript | `.ts`, `.tsx` | `//` | `/*` ... `*/` |
  | Go | `.go` | `//` | `/*` ... `*/` |
  | Rust | `.rs` | `//` | `/*` ... `*/` |
  | SQL | `.sql` | `--` | `/*` ... `*/` |

  Markup, data and configuration files (Markdown, YAML, JSON, XML, HTML,
  CSS) are not code files. A language is added by a minor release.
- **Line classes.** Every physical line is exactly one of: *blank* (only
  white space, also inside a block comment), *comment* (not blank, and only
  comment text and white space), or *code* (anything else, including a line
  with code and a trailing comment). A comment marker inside a string literal
  is not a comment. String literals are the quoted forms of the language that
  end on the same line, plus the Python triple-quoted string and the backtick
  string of JavaScript, TypeScript and Go, which may span lines; a Python
  docstring is a string and so counts as code.
  Raw-string and verbatim forms that differ from these (Rust `r#"..."#`, C#
  `@"..."` with doubled quotes, C++ raw strings) are scanned as ordinary
  strings and can be mis-counted; this is a stated limit.
- **Excluded by default.** Every directory whose name starts with `.`, and the
  directories `node_modules`, `vendor`, `third_party`, `dist`, `build`, `out`,
  `bin`, `obj`, `target`, `venv`, `__pycache__` and `shared-scripts`
  (the checkout of the shared scripts); symbolic links are not followed. The
  input `exclude` is a comma list of patterns that add to this: a pattern
  without `/` matches a directory or file name anywhere, a pattern with `/`
  matches the path relative to `working-directory` (`*` does not cross `/`).
  The counter does not read `.gitignore` or generated-file markers; a caller
  excludes generated code with `exclude`.
- **Totals.** `files` is the number of code files and `lines` is the sum of
  their code lines (comment and blank lines are not in it); the result also
  holds `comment` and `blank` totals and the same four numbers per language,
  sorted by language name, in `code-metrics.json`.
- **Coverage report.** The input `coverage-report` is the path, relative to
  the repository root, of a Cobertura XML file. The percentage is
  `lines-covered / lines-valid` of the root `coverage` element, shown rounded
  half up to a whole number; when a count is absent, `line-rate` is used.
  A path that does not exist, a file that is not well-formed Cobertura XML,
  and a report with no valid lines are failures with the category
  `[configuration]` that names the file; no coverage badge is written. An
  empty `coverage-report` means no coverage badge and a notice. The workflow
  does not run tests. A called workflow runs in its own job, so it cannot see
  the files of the caller's test job: the caller runs its tests in an earlier
  job, uploads the report as an artifact and gives the artifact's name as the
  input `coverage-artifact`. The workflow then downloads that artifact into
  the directory `coverage-artifact` of its workspace and `coverage-report`
  names the file inside the artifact. Without `coverage-artifact`,
  `coverage-report` is a path in the checkout of the repository (a report the
  repository commits). `coverage-artifact` without `coverage-report` is a
  `[configuration]` failure.
- **Badges.** Three flat SVG files with a label and a value, written to the
  root of the `badges` branch with fixed names: `code-files.svg` (label
  `code files`), `code-lines.svg` (label `lines of code`) and `coverage.svg`
  (label `coverage`); the values are the whole number with `,` between groups
  of three digits and, for coverage, `%`. The value colour of the first two is
  blue `#007ec6`; coverage is red `#e05d44` below the input `coverage-warn`
  (default `60`), yellow `#dfb317` from there to below `coverage-good`
  (default `80`) and green `#44cc11` from `coverage-good`. Each file has
  `role="img"`, a `<title>` and an `aria-label` with the same text, a width
  computed from the number of characters (no font is measured) and no
  timestamp, script or external reference, so the same numbers give the same
  bytes.
- **Publishing.** The `badges` branch holds only the three SVG files and
  `code-metrics.json`; the script creates it as an orphan branch when it does
  not exist. It writes the files, and when none differs from the branch it
  commits nothing and says so; otherwise one commit, message
  `Update code metrics badges [skip ci]`, changes only those files. The
  commit is made with the token of the run, which does not start another run;
  the guide tells a caller to start the workflow on pushes to its default
  branch only.
- **Inputs.** `working-directory` (default `.`), `exclude` (default empty),
  `coverage-report` (default empty), `coverage-artifact` (default empty),
  `coverage-warn` (default `60`),
  `coverage-good` (default `80`), `badges-branch` (default `badges`) and
  `tools-ref` (default `v1`; pin it to the same exact tag as the workflow).
  There is no tool version input: the tools are files of this repository and
  Python 3 of the runner.
- **Pass, fail, empty.** The run passes when the badges were written or were
  already current. It fails with a `[configuration]` message that names the
  input and the value for an input that is invalid (a threshold that is not a
  number from 0 to 100, `coverage-warn` above `coverage-good`, a
  `working-directory` that is not a directory, a branch name that is not a
  valid branch name) and for a coverage report as above. A repository with no
  code file passes with a notice and badges that show `0`.
- **Not in the first version:** a badge per language (the JSON holds the
  numbers), lcov and other report formats, branch or function coverage, and
  counting only tracked files.

## Consequences

**Positive:**

- No tool is installed and nothing is downloaded: a run needs only the
  checkout, Python 3 and the instance, so the counter and the renderer are
  fully testable offline with fixtures.
- The same input gives the same bytes, so an unchanged repository produces no
  commit and the `badges` branch history is the history of the numbers.
- The badges have stable URLs on the instance and on the mirror, and nothing
  on the default branch changes.
- A broken or missing report is a failure that names the file, never a
  misleading `0%`.

**Negative:**

- The counter knows only the listed languages and simple scanning rules; some
  string forms are mis-counted (stated above), and results will differ a
  little from `cloc` or `tokei`.
- The workflow needs `contents: write`, which is more than the
  `contents: read` of the quality checks; a caller that grants less cannot use
  it. The write is limited to the `badges` branch by the script, not by the
  host.
- A caller must run its tests and produce a Cobertura XML report in an
  earlier job and upload it as an artifact; other formats need a conversion
  until a later release adds them. The download needs the artifact service
  of the instance to serve a called workflow, which task 8 of MIL-010
  verifies.
- A fixed set of thresholds and colours; a caller can move the two thresholds
  only.
- Security: the script runs with a token that can write to the repository.
  The files are ours and no code is downloaded (the artifact is a report that
  is parsed as XML with entity declarations refused), but a caller that pins
  `tools-ref` to a moving ref takes later changes of the script; the guide
  says to pin the exact tag. The script writes only the four named files, and
  the branch name input is validated so that it cannot name the default branch
  (`main`, `master`) or a branch of the caller's code.

## Affected Artifacts

- [MIL-010] — decides its criterion 2 and unlocks tasks 4 to 6.
- [UC-008] — the use case this workflow serves.
- [US-001] — US-001.18 to US-001.20 state their acceptance criteria.
- [ADR-0005] — the contract style that this decision follows, unchanged.
- [ADR-0006] — adding a language, or changing a colour or a default, is a
  release under its rules; raising a default threshold is breaking.


## Amendment (MIL-011)

The default of the input `tools-ref` in the code metrics contract is the current major tag, defined once in the file
`MAJOR_TAG` of this repository (`v2` from release 2.1.1), and no longer `v1`. A default must
name a tag that holds the script the workflow runs; a test checks it. Callers at `@v1` are
not affected: the `v1` tag keeps the `v1` workflow files.

---

[MIL-010]: ../milestones/mil-010-code-metrics-badges.md
[UC-008]: ../uc-008/uc.md
[US-001]: ../user-stories.md
[ADR-0005]: ./adr-0005-quality-check-contract.md
[ADR-0006]: ./adr-0006-release-process-and-version-pinning.md
[0dc5132]: https://git.tirsystem.com/TirSystem/github-action/commit/0dc5132a2ea419ba05035ee3594cec63335c240b
[eaa0e30]: https://git.tirsystem.com/TirSystem/github-action/commit/eaa0e30beaa097dfeb1c07c814a71d02a6987060
