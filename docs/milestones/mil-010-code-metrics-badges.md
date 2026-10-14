# MIL-010: Code metrics and coverage badges

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-010 |
| CrossReference | [BC-001], [US-001], [MIL-003], [MIL-004], [ADR-0005], [ADR-0006] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | Accepted | Jens Tirsvad Nielsen | AI as stand-in for S01 | Initial version; reviewed (RC-068) | pending |

---

## Purpose

Decide whether a repository can show, as SVG badges, how many code files and
how many lines of code (without comment and blank lines) it holds and how
much of that code its tests cover, produced by one shared workflow of this
repository, without a service outside the instance.

## Deliverable

A reusable workflow `code-metrics.yml` with a script file of this repository
behind it, which counts the code files and the lines of code, reads the
coverage report the caller supplies, writes the badges "code files", "lines
of code" and "coverage" as SVG files and commits them to a `badges` branch of
the calling repository. It comes with a documented set of inputs, a guide and
wiki pages in English, Danish and Bahasa Malaysia, a use in at least one other
repository, and a release that makes it available at the major tag. The
existing workflows keep their names and contracts.

Decisions taken by the user in chat on 2026-10-14, which the contract of task 2
records and does not reopen:

- The counter is a Python script of this repository with no dependency outside
  the standard library (not `cloc`, `tokei` or `scc`).
- The delivery is a reusable workflow (`workflow_call`), as the quality-check
  workflows are.
- The badges are committed to a `badges` branch, so a README can link to
  them; they are not only a run artifact.
- Three badges: code files, lines of code and coverage. A badge per language
  is optional and is decided in the ADR of task 2.
- The coverage report is read in the Cobertura XML format, which `coverage.py`,
  `gcovr` and `coverlet` all write; the counter does not run tests itself, so a
  caller that wants a coverage badge runs its tests first and passes the path
  of the report.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | A job on the runner of the instance can push a commit to a `badges` branch of its own repository with the token the run provides, and the SVG renders as an image in a README on the instance and on the GitHub mirror, verified and recorded | Both render | The push needs a token with more than the contents of its own repository, or the image does not render |
| 2 | The contract (what a code file is, what a comment and a blank line are for each language, excluded paths, generated and vendored files, the coverage report format, the badge colours and text) is decided in an ADR | ADR accepted | Open |
| 3 | The counter gives the hand-counted numbers (files, code, comment, blank) for a fixture of each supported language, including a block comment, a trailing comment, a comment marker inside a string and a file with no final newline | Equal for every fixture | Any difference |
| 4 | The coverage reader gives the percentage of the fixture reports, and a missing or malformed report is a failure that names the file, never a badge showing 0% | Verified | A bad report produces a badge |
| 5 | The badges are valid SVG, carry a title and a text alternative, have a fixed width per text, and are byte-identical for the same input | Verified | Not valid or not stable |
| 6 | The workflow commits nothing when no badge changed, does not start itself again from its own push, and asks for the least permission that writes to its own repository | Verified in a run | A loop, or a wider permission |
| 7 | One other repository runs the workflow and its README shows the three badges, with a seeded change that moves the coverage badge to another colour | Shown | Does not run or does not change |
| 8 | The workflow embeds no script: it runs a file of this repository, and the offline tests exercise the file | Count of embedded scripts is 0 | Embedded script remains |
| 9 | A release (a minor version) makes it available, and the changelog, the README workflow table and the wiki name it | Released | Unreleased |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-003 | The reusable workflow mechanism, the `tools-ref` input and the guide for reading results |
| MIL-004 | The release process and the release workflow publish the result |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O5 (added to the Business Case in the same change as this milestone) | [BC-001] |
| New stories of task 1, to be written in US-001 | [US-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2027-01-30 — it follows the last decision of the plan, 2027-01-16, with two
weeks from 2027-01-18; proposed by the AI and accepted by the user in chat on
2026-10-14, recorded by the AI as stand-in for S05 (ADR-0002). The Business
Case sets no deadline.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Write the use case and stories for the metrics badges | Add a use case "Show code metrics and coverage badges" for the software engineer, add it to the use case diagram, and add stories to US-001: the badges appear after a push, a coverage report that is missing or malformed fails with the file named, and nothing is committed when the numbers are unchanged. Each story has a pass and a fail acceptance criterion. Review them with the checklists of the `artifact` skill. | Yes | US-001 |
| 2 | Decide the contract | Write an ADR with the definitions the counter needs (code file, comment, blank line, per language), the default includes and excludes, the languages of the first version, the Cobertura XML coverage input, the badge texts and colour thresholds, the inputs of the workflow, the name and content of the `badges` branch, and what a pass, a failure and a run without files mean, in the style of ADR-0005. Record the decisions of the Deliverable. | No | |
| 3 | Verify the delivery on the instance | On a throwaway branch, run a job that commits an SVG to a `badges` branch with the token of the run, then check that the raw URL serves it as an image on the instance, that a README shows it, and that it also shows on the GitHub mirror. Record the result in this milestone like MIL-007 task 2, together with the permission that was needed. | No | |
| 4 | Implement the counter | Add `tools/count_loc.py` and tests with a fixture per language under `tests/`: file and line counts split into code, comment and blank, an exclude list, and a machine-readable result on standard output. Standard library only, as the rules of the repository for tools say. | No | |
| 5 | Implement the coverage reader and the badge renderer | Add the reader of the Cobertura XML report and the SVG renderer, with the failure cases of Go/No-Go criterion 4 and a stable output (criterion 5), each with offline tests. | No | |
| 6 | Implement the workflow | Add the reusable workflow `code-metrics.yml` and its script file, which calls the counter, the reader and the renderer and commits to the `badges` branch as the contract of task 2 says, with least-privilege permissions and offline tests as `quality-checks.yml` has. | No | |
| 7 | Write the guides and the wiki pages | A guide in `guides/` with the call, the inputs, how to produce a coverage report for Python, C++ and C#, and the Markdown line that shows the badges; the wiki pages in `docs/wiki` in English, Danish and Bahasa Malaysia; the README table and diagram and the wiki Home workflow list (a test requires every workflow to be listed). | No | |
| 8 | Adopt the workflow in one other repository | Onboard a real repository, or a throwaway one when none fits, show the badges in its README and verify a seeded change that moves the coverage badge. Fix the gaps in the guide that appear. | No | |
| 9 | Release | Add the changelog entry (a new workflow is a minor change, ADR-0006) and run the Release workflow; record the results in this milestone and review it. | No | |

---

[BC-001]: ../business-case.md
[US-001]: ../user-stories.md
[MIL-003]: ./mil-003-quality-checks.md
[MIL-004]: ./mil-004-versioned-release.md
[ADR-0005]: ../adr/adr-0005-quality-check-contract.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
