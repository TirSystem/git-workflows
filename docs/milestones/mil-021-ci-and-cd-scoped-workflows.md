# MIL-021: CI and CD as two scoped workflows, with a credential scan first

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-021 |
| CrossReference | [BC-001], [US-001], [MIL-016], [MIL-017], [MIL-018], [MIL-019], [MIL-020], [ADR-0015], [ADR-0016], [ADR-0017], [ADR-0018], [RC-112] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-19 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; reviewed (RC-112), accepted by the author in chat on 2026-11-19 as stand-in for S01, not independent | pending |

---

## Purpose

Decide that the six scoped workflows become two, `CI` and `CD`, and that a credential scan is the
first job of `CI`. Today a repository shows six unrelated runs for one push (`validate`, `opengrep`,
`release`, `sync-milestones`, `publish-wiki-pages`, `sync-github-metadata`). Nothing shows which
one needs which: `release.py` waits for `Validate / validate (push)` by polling its status, and a
failure in one run does not stop the others. One `CI` run with a job graph (credential scan, then
validation, scan and release check side by side) and one `CD` run (release, milestones, wiki,
metadata) shows the order in Actions and stops the whole pipeline when a credential is found.
This amends the file layout chosen in ADR-0015 to ADR-0018. It renames every status check, so
it is a breaking change and a major release, 4.0.0, with a migration of the branch rules.

## Deliverable

`.gitea/scoped_workflows/ci.yml` (jobs `secret-scan`, then `validate`, `opengrep` and
`release-check` in parallel, each needing only `secret-scan`) and `.gitea/scoped_workflows/cd.yml`
(a `changes` job, then `release`, `sync-milestones`, `publish-wiki` and `sync-metadata`, each only
when its paths changed or on the schedule or a manual start, and only after the `CI` of the same
commit is green); the six old scoped files removed; `tools/secret_scan.py` with offline tests (a
pinned Gitleaks release, its SHA-256 checked, values redacted, a baseline file); a new ADR
(ADR-0019) that supersedes the file layout of ADR-0015 to ADR-0018; a migration of the required
checks in every repository, with `guides/repository-settings.md` and `guides/upgrading.md`; the
guides, the adoption rules, the README, the wiki pages in three languages and the changelog; the
user stories; and release 4.0.0 made by merging the changelog.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | `secret-scan` is the first job of `CI` and every other job of `CI` needs it | A test repository with a planted fake credential shows the run red, the other jobs skipped and the finding named by file and line; a clean repository shows all jobs green | A job of `CI` starts before the scan ends, or a planted credential does not stop the run |
| 2 | No credential value, token or secret reaches a log or an argument, and nothing leaves the instance | The log of the planted case shows the rule, file and line with the value redacted; the scan uses no GitHub token, no GitHub API and no registry at run time | A value is printed, a token is passed, or a call goes outside the instance |
| 3 | The scan reads what a change adds: the commits of a pull request, the commits of a push, and the whole history only on a manual start; accepted findings are kept in a baseline file of the repository | Tests and a run show each range, and a baseline entry silences exactly its finding | An old accepted finding fails every run, or a new finding is silenced |
| 4 | `validate`, `opengrep` and `release-check` run side by side after the scan, and one failing job does not hide the result of another | A run with one red job shows the other two finished with their own result | A job is skipped because a sibling failed |
| 5 | `CD` runs only on a push to the default branch, the daily schedule or a manual start; each job runs only for its own paths (`CHANGELOG.md`, `docs/milestones/**` and `docs/sqa/reviews/**`, `docs/wiki/**`) or on the schedule or a manual start | Runs in a test repository for four different pushes start only the matching jobs, the others show as skipped | A job runs for a push that does not concern it |
| 6 | `CD` starts only after the `CI` of the same commit is green and refuses when it is red or does not appear within the limit; the decision (polling, `workflow_run` or one file) is in the ADR | One test per outcome (green, red, timeout) passes | A release or a publish runs from an unchecked commit |
| 7 | The manual starts still work: each `CD` job can be run by hand, `sync-milestones` keeps its preview mode, and a failed release can be run again | Manual runs of each job in a test repository | A job has no manual start |
| 8 | The old status names are gone and the new ones are documented as `CI / <job> (<event>)` and `CD / <job> (push)` | A search of the guides, the README, the wiki and `guides/repository-settings.md` finds no old name except in the migration table | An old name is still given as the one to require |
| 9 | Before the scan blocks anything, a report-only scan of every repository of the organisations counts the findings; each repository with findings has a fix, a rotated credential or a baseline entry | The count is in the milestone and the release notes, and no repository is blocked by a finding at the release | A repository is blocked by a finding nobody knew about |
| 10 | The branch rules of every repository require the new check names, rolled out in an order that never leaves a repository with a required check that cannot run | A dry run lists every repository with its old and new patterns, and the real run, after the user's go-ahead, is read back | A pull request cannot be merged because its required check does not exist |
| 11 | The offline tests pass, `python tools/build_wiki.py --check` is clean and `validate.yml` is green; the scoped validation accepts the new files (exact action tags, timeouts, permissions, formatting) | All succeed | A test fails or a page is stale |
| 12 | 4.0.0 is released by merging its changelog, the tag `v4` exists, `v3` is not moved, and callers that stay on `v3` keep working until they move | The tag, the release page and the major tag are read back through the API | A release is made by hand or `v3` changes |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-016 | The OpenGrep scan that becomes a job of `CI` |
| MIL-017 | The validation that becomes a job of `CI` |
| MIL-018 | The release workflow and `release.py` that become a job of `CD` |
| MIL-019 | The milestone publishing that becomes a job of `CD` |
| MIL-020 | The release on a changelog change and its wait for the validation of the same commit, which this milestone replaces with a defined order |
| ADR-0015 to ADR-0018 | The decisions on the file layout that the new ADR supersedes |
| Business Case objectives O4 and O8 | Versioned shared workflows (O4) and a free security scan as a scoped workflow (O8); a credential scan is a new objective, O9, added by task 1 |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O4 (shared quality-check and release workflows, versioned) | [BC-001] |
| O8 (free static security scan as a scoped workflow) | [BC-001] |
| O9 (a leaked credential stops the pipeline), added by task 1 | [BC-001] |
| A pull request is checked for credentials before anything else | [US-001] |
| The pipeline shows its order as CI and CD | [US-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-12-11 — proposed by the author; the Business Case sets no deadline. Three weeks, because
the change renames every required check in every repository and must be tried in test
repositories and in a report-only scan first. S01 confirms or moves the date.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Add objective O9 to the Business Case | A credential committed to any repository stops the pipeline before the other checks run; this is a new objective, not a part of O8 (which finds insecure code patterns in a pull request). Add it with its scope item and risk (false positives blocking work, a finding in old history) and have it reviewed. | No | [BC-001] |
| 2 | Write the user stories | Stories for a credential found before anything else, for the pipeline shown as CI and CD, and for a push that concerns only some jobs, in `docs/user-stories.md`, with their review record. | No | [US-001] |
| 3 | Find out how the instance loads and orders scoped workflows | Test in a scratch repository, before any design: whether `needs` and a job `if` work in a scoped workflow, whether `workflow_run` is supported, which status names a job gets, whether the scoped files are read live from the default branch of this repository (then a merge changes every repository at once and the switch-over must be staged), and how a skipped job is shown. The result decides the order of `CD` after `CI` in the ADR. | No | |
| 4 | Decide the layout (ADR-0019) | Record the two files, the job order, the names of the status checks, how `CD` waits for `CI` of the same commit (polling, `workflow_run` or one file), how `CD` decides by path which job runs, the manual starts, and the switch-over order. It supersedes the file layout of ADR-0015 to ADR-0018 and says what stays of each. | No | |
| 5 | Write the credential scan script and its tests | `tools/secret_scan.py` downloads a pinned Gitleaks release, checks its SHA-256, scans the commits a change adds (a pull request range, a push range, the whole history only on a manual start), redacts every value, reads a baseline file of the repository and prints rule, file and line. The proposed step uses `gitleaks-action` with a GitHub token (`PAT_FOR_GITHUB`); that action is made for GitHub, calls the GitHub API with the token and, as far as known, needs a licence key for organisations there, so it is not used: a Gitea runner has no use for the token, and a GitHub token must not be passed to it. The open source binary needs neither. Offline tests with a planted fake credential, a clean tree, a baseline entry and a redaction check. | No | |
| 6 | Run a report-only scan of every repository | Use the script of task 5 on every repository of the four organisations without failing anything, and list the repositories with findings and what each finding is (rule and file, no value). Decide per finding: fix, rotate the credential, or a baseline entry. The count is part of this milestone's evidence. | No | |
| 7 | Write the scoped CI workflow | `ci.yml` with the triggers `pull_request`, `push` to the default branch and a manual start; the job `secret-scan` first, then `validate`, `opengrep` and `release-check` in parallel, each needing only `secret-scan`; exact action tags, a timeout and the least permissions on every job (QC-WF-001). | No | |
| 8 | Write the scoped CD workflow | `cd.yml` with a `changes` job that reads the paths of the push, then `release`, `sync-milestones`, `publish-wiki` and `sync-metadata` each when its paths changed or on the schedule or a manual start, and only after the `CI` of the same commit is green by the way the ADR chose; the manual inputs of the old workflows kept (milestone preview, a retried release). | No | |
| 9 | Remove the six old scoped files and update the tests | Remove `validate.yml`, `opengrep.yml`, `release.yml`, `sync-milestones.yml`, `publish-wiki-pages.yml` and `sync-github-metadata.yml` once the new files are verified, in the order task 4 sets; update the offline tests and the scripts that name a status check (`release.py` no longer polls if the ADR chose a different wait). | No | |
| 10 | Try it in test repositories | Run `CI` and `CD` in three scratch repositories (one with Python, one with a wiki folder and milestones, one with a planted credential) and read every outcome of criteria 1, 4, 5 and 7 back from the host. | No | |
| 11 | Migrate the required checks | A script that lists every repository with its branch rules, shows the old and new patterns as a dry run, and, after the user's go-ahead, changes them in an order that never requires a check that cannot run; update `guides/repository-settings.md` and add the old-to-new table to `guides/upgrading.md`. | No | |
| 12 | Describe the new pipeline | The guides, `guides/adoption-rules.md`, the README (workflow table and count), the wiki pages in three languages and the changelog entry for 4.0.0 with a Breaking section that names the renamed checks. | No | |
| 13 | Release 4.0.0 by merging | Merge the changelog of this milestone and read the tag, the page and the major tag `v4` back; check that `v3` did not move and that a repository still on `v3` works. | No | |

---

[BC-001]: ../business-case.md
[US-001]: ../user-stories.md
[MIL-016]: ./mil-016-semgrep-scoped-workflow.md
[MIL-017]: ./mil-017-scoped-validation-workflow.md
[MIL-018]: ./mil-018-scoped-release-workflow.md
[MIL-019]: ./mil-019-scoped-milestone-sync.md
[MIL-020]: ./mil-020-release-on-changelog-change.md
[ADR-0015]: ../adr/adr-0015-semgrep-scoped-workflow.md
[ADR-0016]: ../adr/adr-0016-scoped-validation-workflow.md
[ADR-0017]: ../adr/adr-0017-scoped-release-workflow.md
[ADR-0018]: ../adr/adr-0018-scoped-milestone-sync.md
[RC-112]: ../sqa/reviews/rc-112-mil-021-pp-001.md
