<!-- Generated from guides/code-metrics.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`guides/code-metrics.md`](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/code-metrics.md). Changes made here are overwritten the next time the wiki is published.

English | [Dansk](CodeMetrics.da) | [Bahasa Melayu](CodeMetrics.ms)

# Showing code metrics and coverage badges

How a software engineer calls the shared code-metrics workflow and shows its
three badges (code files, lines of code and coverage) in a README. The workflow
counts the code of the repository, reads a coverage report that the caller
supplies and commits three SVG files to a `badges` branch. It runs no test and
needs no secret. Its contract is ADR-0010 in this repository.

## Calling the workflow

The workflow cannot see the files of your test job, so the tests run in a job of
your own, upload the Cobertura XML report as an artifact, and the metrics job
runs after it:

```yaml
name: Code metrics

on:
  push:
    branches: [ main ]

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4.2.2
      - run: python3 -m pip install pytest pytest-cov && python3 -m pytest --cov --cov-report=xml
      - uses: actions/upload-artifact@v4.6.2
        with:
          name: coverage
          path: coverage.xml

  metrics:
    needs: tests
    permissions:
      contents: write
    uses: TirSystem/git-workflows/.gitea/workflows/code-metrics.yml@v2
    with:
      coverage-artifact: coverage
      coverage-report: coverage.xml
```

| Input | Default | Meaning |
| --- | --- | --- |
| `working-directory` | `.` | Directory, relative to the repository root, whose code is counted |
| `exclude` | empty | Comma list of patterns of files and directories that are not counted, in addition to the defaults; a pattern without `/` matches a name anywhere, a pattern with `/` matches the path below `working-directory` |
| `coverage-report` | empty | Cobertura XML report: the file inside the artifact when `coverage-artifact` is set, otherwise a path in the repository; empty writes no coverage badge |
| `coverage-artifact` | empty | Name of an artifact, uploaded by an earlier job of the same run, that holds the report |
| `coverage-warn` | `60` | Coverage in percent below which the badge is red |
| `coverage-good` | `80` | Coverage in percent from which the badge is green; in between it is yellow |
| `badges-branch` | `badges` | Branch that holds the badge files; it is created when it does not exist |
| `tools-ref` | `v2` | Tag or branch of `TirSystem/git-workflows` from which the scripts in `tools/` are fetched |

Reference the workflow at the major tag (`@v2`) or at an exact tag, never at
`main`. A call at an exact tag is pinned completely only when `tools-ref` names
the same tag. See the upgrade guide. Start the workflow on pushes to your
default branch only: the badge commit carries `[skip ci]` and is made with the
token of the run, which does not start another run, but a trigger on every
branch would write one commit per branch.

## What is counted

- A code file is a text file with the extension of a supported language:
  Python, shell, PowerShell, C, C++, C#, Java, JavaScript, TypeScript, Go, Rust
  and SQL. Markdown, YAML, JSON, XML, HTML and CSS are not code files.
- Every line is exactly one of blank (only white space), comment (only comment
  text) or code (everything else, including a line with code and a trailing
  comment). The badge shows the lines of code only.
- A comment marker inside a string is not a comment, and a Python docstring is a
  string, so it counts as code.
- Directories that start with a dot and `node_modules`, `vendor`, `third_party`,
  `dist`, `build`, `out`, `bin`, `obj`, `target`, `venv`, `__pycache__` and
  `shared-scripts` are not counted. Generated code is excluded with `exclude`.
- Raw and verbatim strings that differ from an ordinary string (Rust `r#"..."#`,
  C# `@"..."`, C++ raw strings) can be counted wrongly. The counts will differ
  a little from other tools; the rules are the same on every run.

## The coverage badge

The report is a Cobertura XML file, which `coverage.py` (`coverage xml`),
`gcovr` (`--cobertura`) and `coverlet` (`cobertura` format) write. The badge
shows `lines-covered` over `lines-valid`, rounded to a whole percent, and its
colour follows the two thresholds. A report that does not exist, is not
well-formed Cobertura XML or has no valid lines fails the run with the file
named; the coverage badge is never written as `0%` for a bad report. Without
`coverage-report` the run passes with a notice and no coverage badge.

## Showing the badges

Add the images to the README with the raw URLs of the branch:

```markdown
![code files](https://git.tirsystem.com/OWNER/REPO/raw/branch/badges/code-files.svg)
![lines of code](https://git.tirsystem.com/OWNER/REPO/raw/branch/badges/code-lines.svg)
![coverage](https://git.tirsystem.com/OWNER/REPO/raw/branch/badges/coverage.svg)
```

On the GitHub mirror use `https://raw.githubusercontent.com/OWNER/REPO/badges/code-files.svg`;
the push mirror copies the branch. The `badges` branch also holds
`code-metrics.json` with the numbers per language. The instance caches a raw
file for up to six hours, so a changed badge can show the old number for a
while there; the mirror caches for five minutes. A private repository does not
show the badges to a reader who is not signed in.

## When the workflow fails

| Message | Cause | Fix |
| --- | --- | --- |
| `[configuration] working-directory must be a relative path inside the repository.` | An absolute path or `..` | Use a path inside the repository |
| `[configuration] coverage-report '<x>' does not exist.` | The report was not produced, or the artifact name or path is wrong | Check the test job and the artifact name; the path is inside the artifact |
| `[configuration] coverage-report '<x>' is not well-formed XML` or `is not a Cobertura report` | The file is another format | Write Cobertura XML (`coverage xml`, `gcovr --cobertura`) |
| `[configuration] coverage-report '<x>' has no valid lines.` | The tests ran no measured code | Check the coverage configuration |
| `[configuration] coverage-artifact '<x>' needs coverage-report` | The artifact is named but not the file in it | Set `coverage-report` |
| `[configuration] coverage-warn ... is above coverage-good` or `is not a number from 0 to 100` | A threshold is invalid | Correct the input |
| `[configuration] badges-branch '<x>' must not be a default branch` or `holds files that are not badge files` | The branch name is `main`, `master` or a branch with other content | Use a branch that holds only the badges |
| `the push to '<x>' failed twice` | Another run wrote the branch at the same time, or the token cannot write | Re-run; check that the job has `contents: write` |
| The download step fails | The artifact does not exist in this run, or the job does not run after the test job | Add `needs:` and check the artifact name |
