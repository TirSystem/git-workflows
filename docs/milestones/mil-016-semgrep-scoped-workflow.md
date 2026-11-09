# MIL-016: Static security scan with OpenGrep as a scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-016 |
| CrossReference | [BC-001], [MIL-013], [MIL-014], [ADR-0005], [ADR-0015], [RC-089], [RC-090], [RC-099], [RC-111] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-09 | Deprecated | Jens Tirsvad Nielsen | S01 | New task 8, scan only the rule directories of the languages a repository has, because a run on a runner takes more than 5 minutes (criterion 1) with a scan of about 25 s on a developer machine; Release is now task 9; reviewed (RC-109), accepted by the author in chat on 2026-11-09 as stand-in for S01, not independent | [bc0157e] |
| 2026-11-09 | Accepted | Jens Tirsvad Nielsen | S01 | Records the run time on the runner after task 8 (scan step 3 min 18 s and 3 min 5 s in two runs of release 3.3.2, 4 min 21 s with the old script, one repository); reviewed (RC-111), accepted by the author in chat on 2026-11-09 as stand-in for S01, not independent | [59347d5] |

---

## Purpose

Decide whether the repositories of the TirSystem organizations get a free static
security scan, in the place where GitHub offers CodeQL and GitHub Code Quality.
The scan is OpenGrep, a fork of Semgrep Community Edition, installed as a
single executable on the runner and run with a pinned checkout of its rules and no
login, as a **scoped** workflow: the instance
runs it in every repository, so nothing is added to a repository. The decision
supports objective O8 of the Business Case (security findings are shown to the
author of a pull request), which S01 accepted on 2026-10-28.

## Deliverable

The scoped workflow `.gitea/scoped_workflows/opengrep.yml` and its script under
`tools/`, with offline tests; ADR-0015 (rule set, what blocks, version pin,
telemetry, licence of the rules); the guide `guides/opengrep.md`, the row in
`guides/adoption-rules.md`, the README section, the wiki pages in three
languages and the changelog entry; a trial on this repository and three others
with the findings and the false positives counted; and a minor release.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | OpenGrep installs and runs on a runner of the instance without a login, and finishes in time | A run on this repository prints `opengrep --version` of the pinned version, checks the sha256 of the executable, lists the outbound hosts it used (none carrying source code) and ends in at most 5 minutes | It needs a token, an account or outbound access that is not allowed, or it takes longer |
| 2 | The rules are community rules, and their licence permits the use | ADR-0015 names the rule set (for example `p/default`) and quotes the licence of the rules and of the engine, read from the sources | The licence forbids the use, or it was not read |
| 3 | A finding of the blocking severity fails the run, others are shown and do not | A test repository with one planted `ERROR` finding fails; one with only `WARNING` findings passes and lists them | Either result is wrong |
| 4 | A repository with no files OpenGrep scans is skipped, not failed | A run in a repository of text files only ends green and says so | It fails |
| 5 | The scan reads files only and changes nothing; the token of the run is not needed | The workflow has `permissions: contents: read` and no secret | A write permission or a secret appears |
| 6 | A false positive can be silenced in the repository, and the way is documented | `.semgrepignore` and `# nosemgrep` work in a test and are in the guide | There is no way, or it is undocumented |
| 7 | The trial on this repository and three others (one Python, one C#, one C++) is recorded | Findings and false positives counted per repository, with the decision on the blocking severity | A repository is missing from the record |
| 8 | The offline tests pass and `python tools/build_wiki.py --check` is clean | Both succeed | A test fails or a page is stale |
| 9 | The adoption row exists and names a condition that is checkable from the repository | The row is in `guides/adoption-rules.md`, linked from the guide and the README | It is missing |
| 10 | The release is published with a changelog entry that names the new workflow and its rule | Tag and release page read back through the API | No entry, or a moved major tag |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-014 | Its task 2 verifies that a scoped workflow fires on a pull request and push, and that it reaches repositories of the organizations; this milestone uses the same delivery |
| MIL-013 | Release 2.3.0 comes first, so this release is the next minor |
| ADR-0005 | The contract of the shared workflows: a script is a file, tools are pinned, failures are categorised |
| Business Case objective O8 | The objective the milestone traces to; it is in the Business Case since 2026-10-28 (task 1 is done) |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| O8 (security findings are shown to the author of a pull request) | [BC-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-12-11 — proposed by the author; the Business Case sets no deadline. The window (2026-11-30 to 2026-12-11) follows MIL-014 (2026-11-27). S01 confirms the date when accepting the plan.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Add objective O8 to the Business Case | Write the objective (security findings from a free static scan are shown to the author of a pull request) and the matching scope item, review it against the Business Case checklist and write the record, as MIL-013 did for O7. The AI does not change the Business Case without S01's acceptance. | No | [BC-001] |
| 2 | Verify OpenGrep on a runner | Done on a developer machine on 2026-10-29 (see ADR-0015). Still to do on a runner of the instance: download the pinned executable, fetch the pinned rules, scan this repository; record the time, the outbound hosts it needs (checked with a capture) and that the runner is Linux x86_64. | No | |
| 3 | Decide the contract (ADR-0015) | Write the ADR: the rule set, the blocking severity, the pinned version and how it is moved, that metrics are off, the licence of the engine and of the rules (read from the sources, not recalled), how findings are shown (log and job summary; Gitea has no SARIF upload), and what a repository does to silence a finding. | No | |
| 4 | Write the script and tests | `tools/opengrep_scan.py` that installs the pinned executable and rules, runs OpenGrep with the settings of the ADR, prints the findings and returns the exit code; offline tests with a fake of the `opengrep` command for the pass, the fail and the skip cases. | No | |
| 5 | Write the scoped workflow | `.gitea/scoped_workflows/opengrep.yml`: on a pull request, a push to `main` and manually; read-only permissions; installs the pinned version; runs the script fetched from this repository at the major tag; skips a repository with nothing to scan. | No | |
| 6 | Document it | `guides/opengrep.md`, the row in `guides/adoption-rules.md`, the README section and table (the count of workflows), the wiki pages in three languages, the changelog entry. | No | |
| 7 | Run the trial | Scan this repository and three others (one Python, one C#, one C++); count the findings and the false positives for each, silence the false positives the way the guide says, and record the decision on the blocking severity in this milestone. | No | |
| 8 | Scan only the rule directories of the languages present | `tools/opengrep_scan.py` loads all twelve rule directories in every repository, so the run time is set by the rules and the cores of the runner, not by the repository: a run on a runner took more than 5 minutes (criterion 1), and 25 s on a developer machine with 20 cores. Choose the directories from the files of the repository being scanned, read from the `languages:` field of the rules; skip a directory only when no file of its languages exists, keep `generic` always, and run a directory whose languages are unknown. Print the directories chosen. Amend ADR-0015. Test that the findings of the full set and of the chosen set are equal on this repository and three others, one with C and C++. Result, 2026-11-09, on this repository: the scan step of `opengrep.yml` took 4 min 21 s with the old script (run 4628, 3.3.0) and 3 min 18 s and 3 min 5 s with the new one (runs 4644 and 4652, release 3.3.2), so criterion 1 (at most 5 minutes) is met with a margin of about 1 min 40 s. Release 3.3.1 scanned its own copy of the rules and failed every scan; 3.3.2 excludes it (CHANGELOG). Two runs on one repository; repositories with more languages load more rule files and are not measured. | No | [ADR-0015], [RC-111] |
| 9 | Release | Release through the release workflow as the next minor (Added); the moving major tag moves with it. | No | |

---

[BC-001]: ../business-case.md
[MIL-013]: ./mil-013-english-comments-check.md
[MIL-014]: ./mil-014-wiki-publishing-scoped-again.md
[ADR-0005]: ../adr/adr-0005-quality-check-contract.md
[ADR-0015]: ../adr/adr-0015-semgrep-scoped-workflow.md
[RC-089]: ../sqa/reviews/rc-089-bc-001-o8.md
[RC-090]: ../sqa/reviews/rc-090-mil-016.md
[RC-099]: ../sqa/reviews/rc-099-opengrep-bc-o8-mil-016.md
[RC-111]: ../sqa/reviews/rc-111-mil-016-run-time.md
[bc0157e]: https://git.tirsystem.com/TirSystem/git-workflows/commit/bc0157ea2a017fe8a9377e8266dfda2878467865
[e9b782d]: https://git.tirsystem.com/TirSystem/git-workflows/commit/e9b782dc0bc3984c66629047e00012024fd6ff93
[59347d5]: https://git.tirsystem.com/TirSystem/git-workflows/commit/59347d5f35fd33b9560c2d817276f9c0401a8bc4
