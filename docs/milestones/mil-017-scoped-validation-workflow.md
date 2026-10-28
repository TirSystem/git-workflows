# MIL-017: Validate every repository with a scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-017 |
| CrossReference | [BC-001], [MIL-014], [MIL-016], [ADR-0005], [ADR-0013], [RC-091], [US-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; reviewed (RC-091), accepted by the author in chat on 2026-10-29 as stand-in for S01, not independent | [1690cf7] |

---

## Purpose

Decide whether every repository of the TirSystem organizations gets the same
small validation check, as a **scoped** workflow: the instance runs it in each
repository, so nothing is added to a repository, and the commit of any
repository carries one status with one name. The check is the smallest one that
makes sense everywhere: the workflow files and the shell scripts of the
repository. The validation of this repository (`validate-workflows.yml`, its own
tests and coverage) stays as it is; it is a different check with a different
name. The decision exists so that the release workflow of MIL-018 can require a
green validation in any repository and not only in this one.

## Deliverable

The scoped workflow `.gitea/scoped_workflows/validate.yml` and its script
`tools/validate_repo.py`, with offline tests; an ADR (the checks, what blocks,
the pinned tools, the name of the status); the guide `guides/validate.md`, the
row in `guides/adoption-rules.md`, the README section, the wiki pages in three
languages and the changelog entry; a trial on this repository and three others
with the findings counted; and a minor release.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The workflow runs in a repository with no caller file | A run in this repository and one in a test repository without `.gitea/` both finish | It needs a file in the repository |
| 2 | The workflow files are checked: valid YAML and the `QC-WF-001` criteria that the ADR of task 2 lists by number as decidable by a script | A test repository with one planted violation per listed criterion fails and names the file, the line and the criterion number; a clean one passes; a criterion that is not listed is not checked and the guide says so | A listed violation passes, or a clean file fails |
| 3 | The shell scripts are checked with `shellcheck` and `shfmt` at pinned versions | A planted error in a `*.sh` file fails and names it; a repository without shell scripts skips the step | Either result is wrong |
| 4 | A repository with nothing to check ends green and says so | A run in a repository of text files only passes with the line "nothing to validate" | It fails |
| 5 | The check reads files only and changes nothing | The workflow has `permissions: contents: read` and no secret | A write permission or a secret appears |
| 6 | The status has a fixed name that another workflow can read | The commit status API of a test repository lists `Validate / validate (push)` as `success` or `failure` for a pull request and for a push to the default branch | The name differs between runs or repositories |
| 7 | A finding can be silenced where it is, and the way is documented | `# shellcheck disable=` and the documented ignore of a workflow criterion work in a test and are in the guide | There is no way, or it is undocumented |
| 8 | The trial on this repository and three others (one Python, one C#, one C++) is recorded | Findings and false positives counted per repository, with the decision on what blocks | A repository is missing from the record |
| 9 | The offline tests pass and `python tools/build_wiki.py --check` is clean | Both succeed | A test fails or a page is stale |
| 10 | The release is published with a changelog entry that names the new workflow and its status name | Tag and release page read back through the API | No entry, or a moved major tag |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-014 | Its task 2 verifies that a scoped workflow fires on a pull request and a push and reaches the repositories of the organizations; this milestone uses the same delivery |
| MIL-016 | Its release comes first, so this release is the next minor |
| ADR-0005 | The contract of the shared workflows: a script is a file, tools are pinned, failures are categorised |
| Business Case objective O4 | Shared quality-check and release workflows; S01 confirms that a scoped workflow serves it, as MIL-014 did for the wiki |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O4 (shared quality-check and release workflows, versioned) | [BC-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-12-18 — proposed by the author; the Business Case sets no deadline. The window (2026-12-14 to 2026-12-18) follows MIL-016 (2026-12-11). S01 confirms the date when accepting the plan.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Verify the delivery of a scoped workflow and the status name | In a test repository start a scoped workflow on a pull request and on a push to the default branch and read the commit status API: record the exact `context` string the instance gives (workflow name, job name and event) and whether it is the same in every repository. This fixes the name that MIL-018 reads. | No | [MIL-014] |
| 2 | Decide the contract (ADR) | Write the ADR: which `QC-WF-001` criteria the script decides, which tools and versions (`shellcheck`, `shfmt`, a YAML parser), what blocks and what only warns, the name of the status, how a finding is silenced and what a repository with nothing to check gets. Read the tool licences from their sources. | No | [ADR-0005] |
| 3 | Write the script and tests | `tools/validate_repo.py` that finds the workflow files and the shell scripts of a checked-out repository, runs the checks of the ADR, prints one line per finding with file, line and criterion, and returns the exit code; offline tests with fixtures for the pass, the fail and the nothing-to-validate cases. | No | |
| 4 | Write the scoped workflow | `.gitea/scoped_workflows/validate.yml`: on a pull request, a push to the default branch and manually; read-only permissions; installs the pinned tools; runs the script fetched from this repository at the major tag; ends green with a message when there is nothing to check. | No | |
| 5 | Document it | `guides/validate.md`, the row in `guides/adoption-rules.md`, the README section and table (the count of workflows), the wiki pages in three languages, the changelog entry. | No | |
| 6 | Run the trial | Run it on this repository and three others (one Python, one C#, one C++); count the findings and the false positives for each, silence the false positives the way the guide says, and record the decision on what blocks in this milestone. | No | |
| 7 | Release | Release as the next minor (Added) through the release workflow; the moving major tag moves with it. | No | |

---

[BC-001]: ../business-case.md
[US-001]: ../user-stories.md
[MIL-014]: ./mil-014-wiki-publishing-scoped-again.md
[MIL-016]: ./mil-016-semgrep-scoped-workflow.md
[ADR-0005]: ../adr/adr-0005-quality-check-contract.md
[ADR-0013]: ../adr/adr-0013-wiki-publishing-scoped-workflow.md
[RC-091]: ../sqa/reviews/rc-091-mil-017.md
[1690cf7]: https://git.tirsystem.com/TirSystem/git-workflows/commit/1690cf749c4ffb5e0a0174fe50fceb060b6e3f1c
