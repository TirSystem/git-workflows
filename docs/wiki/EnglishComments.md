<!-- Generated from guides/english-comments.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`guides/english-comments.md`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/guides/english-comments.md). Changes made here are overwritten the next time the wiki is published.

English | [Dansk](EnglishComments.da) | [Bahasa Melayu](EnglishComments.ms)

# Keeping source code comments in English

How a software engineer calls the shared workflow that checks that the comments
and docstrings of a pull request are written in English. The workflow fails the
run when one is not, and writes one comment on the pull request that mentions
the author. It changes no file and sends no source text outside the instance.
Its decision is ADR-0012 in this repository.

## Calling the workflow

```yaml
name: English comments

on:
  pull_request:

jobs:
  english-comments:
    uses: TirSystem/github-action/.gitea/workflows/english-comments.yml@v2
    with:
      exclude: "docs/generated/**"
      allowed-words-file: .english-comments-allowed-words
```

| Input | Default | Meaning |
| --- | --- | --- |
| `scope` | `changed` | `changed` checks the comments on the lines the pull request adds; `all` checks every tracked file |
| `exclude` | | Comma list of file name or path patterns that are not checked (`*` and `**` are wildcards) |
| `allowed-words-file` | | A file of the repository with words that are never judged, one per line, `#` starts a comment |
| `threshold` | `0.6` | The probability, above 0 and at most 1, from which a comment counts as not English |
| `min-words` | `3` | A comment with fewer words is not judged |
| `langid-version`, `numpy-version` | `1.1.6`, `2.1.3` | The pinned packages the detector needs |
| `tools-ref` | the current major | The tag of this repository whose scripts are run; pin it together with the workflow |

The optional secret `REPORT_TOKEN` is a Gitea token that may comment on pull
requests. Without it the workflow uses the token of the run, so the comment is
written by the Actions bot. A pull request from a fork has a read-only token:
the check still fails the run, but no comment is written.

## What is checked

The comments and docstrings of the files of the languages in the code counter
([code metrics](CodeMetrics)): Python, shell, PowerShell, C, C++, C#, Java,
JavaScript, TypeScript, Go, Rust and SQL. Strings and code are not read.
Consecutive comment lines form a block. Each line of a block is judged on its own
(at least four words and a probability of at least 0.7), so an English line cannot
hide a Danish one next to it; when no line is flagged, the block is judged as a whole
(at least `min-words` words and `threshold`), so a sentence cut over short lines is not missed.

Before a block is judged, everything that is not a word is removed: paths, URLs,
options (`--output`), file names, identifiers (`snake_case`, `camelCase`),
numbers, acronyms and constants (`JSON`), a leading label such as `Usage:`, and
the words of the allowed-words file. A block with fewer than `min-words` words
left is not judged, so a short comment passes. Comments that configure a tool
(`noqa`, `type:`, `pragma`, `shellcheck`) are not read.

## When the check fails

The run fails, each finding is shown as an annotation (`::error file=...,line=...`)
and in the log as `file:line: looks Danish (0.93): "the comment"`, and one comment
on the pull request lists them and mentions the author. A new run updates that
comment; when the pull request passes, the comment is marked resolved and no
longer mentions anyone.

Fix it by rewriting the comment in English. For a quotation or a name that is
not English, either put `english-comments: ignore` in the comment (it skips the
whole comment block it is in), or add the word to the allowed-words file.

## Blocking the merge

A failing run does not block a merge by itself. In the branch protection of the
target branch, mark the check as required: run the workflow once on a pull
request and choose its entry in the list of status checks (the exact name is
made from the calling workflow, its job and the event). Setting branch
protection is the repository owner's action; the workflow does not change it.

## How accurate it is

The detector is `langid`, limited to English, Danish, Norwegian, Swedish,
German, French, Malay, Indonesian and Dutch. On the corpus of the repository it
flags none of 300 English comments, 44 of 45 Danish and 41 of 45 Malay comments
and all of the 48 German, Swedish, Norwegian and French ones (ADR-0012). Its
limits:

- a comment of one or two words, or one that is mostly names, is not judged;
- a comment in poor English passes, and a comment that mixes English technical
  terms with few Danish or Malay words can pass;
- the Danish and Malay comments of the corpus were written for the test, not
  collected from real code, so real code will show other misses. Report a miss
  or a false positive with the comment, and it joins the corpus.

## Troubleshooting

| Message | Cause |
| --- | --- |
| `[configuration] give --base` | The workflow was started by an event that is not a pull request with `scope: changed`; call it on `pull_request` or use `scope: all` |
| `[configuration] git diff failed` | The base branch is not in the checkout; the workflow fetches the full history, so check that the pull request has a target branch |
| `[configuration] langid is not installed` | The install step failed; check the pinned versions |
| `[permissions] ... may not comment on pull requests` | The token cannot comment; give `REPORT_TOKEN` write access to issues and pull requests |
| A finding that is not a finding | Add the words to the allowed-words file, or `english-comments: ignore` to the comment |
