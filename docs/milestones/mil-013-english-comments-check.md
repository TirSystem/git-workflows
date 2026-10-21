# MIL-013: Source code comments are in English

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-013 |
| CrossReference | [BC-001], [US-001], [MIL-004], [MIL-010], [MIL-011], [ADR-0005], [ADR-0006], [ADR-0010], [ADR-0012] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version; reviewed (RC-083), accepted by the author in chat as stand-in for S01 with target date 2026-11-20 | [e35b1c5] |
| 2026-10-21 | Accepted | Jens Tirsvad Nielsen | S01 | Added the results of tasks 1 to 8, 10 and 13 and the three defects found in the trial; reviewed (RC-085), accepted by the author in chat as stand-in for S01 | pending |

---

## Purpose

Decide whether a pull request can be stopped automatically when a comment in its source code is not written in English, and the author told why.

TirSystem code is read by people who speak Danish, Bahasa Malaysia and English, so the comments of source code are in English only (the shared language of the repositories, and the register the project's coding conventions already ask for). Today nothing enforces it: a Danish or Malay comment is found, if at all, by a human reviewer. This milestone adds a check that finds them on the pull request, fails the check run so the pull request is blocked, and writes a message to the author with the file, the line and the reason.

The hard part is the detection, not the workflow. A comment is short, full of identifiers, and often a few words; Danish and Malay words are often close to English ones or are names. The first task therefore decides the method on a measured corpus and records it in an ADR; the rest follows from it.

## Deliverable

Release `2.3.0` of this repository ([ADR-0006]: a new capability is a minor release) with a reusable workflow `english-comments.yml` that other repositories call with `uses:`, its script files under `tools/` (comment extraction, detection, reporting), a guide, a README section, wiki pages in English, Danish and Bahasa Malaysia, a changelog entry under `Added`, and offline tests. An ADR for the detection method and its error rate. The workflow runs on the pull requests of this repository too. A review record. In the other repositories, in their own pull requests: the rule in the `coding-conventions` skill of `TirSystem/sqa-qc-framework`, and a proposed criterion for the checklist repository.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The detection method is chosen on a corpus recorded in the repository: at least 40 comments each in Danish and in Bahasa Malaysia, at least 40 in other languages (German, Swedish, Norwegian, French), and at least 200 English comments, among them comments with identifiers, paths and abbreviations. The ADR gives recall and false positives per language | Recall at least 90 % for Danish and Malay, and at most 1 false positive per 200 English comments | A lower rate, or no corpus |
| 2 | The check reads comments and docstrings, not code or string values, in every language of [ADR-0010], and a comment line holding only identifiers, URLs, numbers or code is not judged | Fixtures for each language pass | A string value or a code-only comment is reported |
| 3 | The workflow checks the files a pull request changes (all tracked files when asked), reports each finding as `file:line`, the language found and the text, and fails the run when there is one | A pull request with one Danish comment fails; one without passes | The run passes with a finding, or fails without one |
| 4 | An author can mark an exception on the line (a quotation, a name) and list allowed words in a file of the repository; both are logged | The marked line is not reported | No way to mark an exception |
| 5 | On failure the workflow writes one comment on the pull request that mentions the author and lists the findings; a re-run updates that comment instead of adding another, and a passing run marks it resolved | Verified on a throwaway pull request, with the Gitea mention reaching the author | Two comments, no mention, or a comment on a passing run |
| 6 | The comment is written with a token that holds the smallest scope that works; it is a CI secret and appears in no log, and no source text is sent to a service outside the instance | A search of the run logs for the token finds none; the detector needs no network | A token in a log, or an external call |
| 7 | The failing check blocks the merge: the workflow's check is listed as required, and a pull request with a finding cannot be merged. Setting branch protection is the repository owner's action; this milestone documents it and verifies it with the owner | Verified with S01 or S03 on a throwaway branch | The pull request can still be merged |
| 8 | This repository calls the workflow on its own pull requests, and passes | The caller run is green on `main` | Not called, or red |
| 9 | The guide, README and wiki pages (English, Danish, Bahasa Malaysia) describe the workflow at `@v2`, and the changelog has an `Added` entry; the release is a minor (`2.3.0`), `v2` moves to it and `v1` is not touched | Released | Another level, or `v1` moved |
| 10 | The framework rule and the checklist criterion are open as pull requests of their own repositories after release 2.3.0 | Both open | Missing |
| 11 | Reviewed | A review record (`RC-*`) for this milestone, the workflow, the scripts, the tests and the guides, each with a verdict of Go | An instance without a record |

## Dependencies

| Depends on | Reason |
| --- | --- |
| [MIL-010] | The code counter that already tells comment lines from code lines for the languages of [ADR-0010]; the extractor builds on its scanner |
| [MIL-004] | The release process and the Release workflow that publish `2.3.0` |
| [MIL-011] | `MAJOR_TAG` and the `tools-ref` default that a new reusable workflow must follow |
| [ADR-0005] | The contract of a shared check: inputs with working defaults, pinned tools, a script file, a failure that names the cause |
| An organization secret with a Gitea token that may comment on pull requests (S03) | Criterion 5; created by the operator, never recorded in this repository |
| Branch protection of the repositories that adopt the check (S01 or S03) | Criterion 7; changing it is the owner's decision, not made by the workflow |
| `TirSystem/sqa-qc-framework` and `TirSystem/SQA-QC-Checklists` | Task 12 changes them in their own pull requests, after the release |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| Business Case objective O7: a shared workflow that checks that the comments in source code are written in English, blocks the pull request when they are not, and tells the author | [BC-001] |
| User stories | [US-001] (no new story: the tasks below are technical; the check is used by the authors of pull requests) |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-11-20 (Friday), proposed: two weeks from 2026-11-09, after [MIL-012] (2026-11-06) so that the two milestones do not compete for the one runner and the one reviewer. The Business Case sets no deadline. S01 confirmed the date when accepting this milestone, in chat on 2026-10-19.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Build the corpus | Collect and label the comments of criterion 1 in `tests/fixtures/` (real comments from the TirSystem repositories where they exist, written ones otherwise), with the language of each. English comments come from this repository and others that are known to be English. Record the source of each part. | No | |
| 2 | Choose the detection method (ADR) | Compare at least two methods on the corpus: a rule-based one (letters outside English, word lists for Danish and Malay) and a language-identification library restricted to the candidate languages, run offline. Measure recall and false positives per language, the install size and the time on a repository of 1 000 files. Write the ADR with the numbers and the choice. | No | [ADR-0005] |
| 3 | Extract comments | Add a script that returns the text, file and line of every comment and docstring for the languages of [ADR-0010], reusing the scanner of `tools/count_loc.py` (it classifies lines today but does not return the text). Skip string values, code and comment lines that hold only identifiers, URLs, numbers or code. | No | [MIL-010] |
| 4 | Detect the language | Implement the method of task 2 as a script with a fixed interface (comment in, language and confidence out), the exception marker on the line and the allowed-words file of criterion 4. | No | |
| 5 | Report and tell the author | A script that prints each finding as `::error file=...,line=...` and `file:line`, fails the run, and writes or updates one pull request comment that mentions the author, through the Gitea API with the smallest token scope; a passing run marks the comment resolved. A fake API in the tests. | No | |
| 6 | Write the reusable workflow | `english-comments.yml` with `workflow_call`, inputs with working defaults (changed files only, languages, allowed-words file, exclude), a pinned `tools-ref` that follows `MAJOR_TAG`, the token as a secret, and explicit job permissions. The `run:` lines only call the script files. | No | [ADR-0005] |
| 7 | Offline tests | Tests for the extractor, the detector against the corpus (the rates of criterion 1 as a test that fails below them), the reporting against the fake API, and the workflow definition; the coverage limit of `tools/` holds. | No | |
| 8 | Trial on the instance | On a throwaway pull request with one Danish comment, one Malay comment and one marked exception: record the failing run, the comment with the mention, the update on a re-run and the green run after the fix. Search the logs for the token. | No | |
| 9 | Block the merge | With S01 or S03, mark the check as required for `main` of this repository and show that a pull request with a finding cannot be merged. Document the setting for other repositories. This task changes branch protection, so it is done by the owner, not by the AI. | No | |
| 10 | Guides, README and wiki | Guide, README section, and wiki pages in English, Danish and Bahasa Malaysia, following [MIL-005]; the sidebar. | No | [MIL-005] |
| 11 | Call it in this repository, then release | A caller workflow for the pull requests of this repository; the changelog entry; the Release workflow (dry run first); check that `v2` points at `v2.3.0` and `v1` is unchanged. | No | [ADR-0006] |
| 12 | The rule in the framework and the checklists | In `TirSystem/sqa-qc-framework`, add the English-comments rule to the `coding-conventions` skill and the call of the workflow to its CI template; in `TirSystem/SQA-QC-Checklists`, propose a criterion. Each in its own pull request, after release 2.3.0. | No | |
| 13 | Add MIL-013 to the Business Case and the Project Plan | Objective O7, the scope item and a success criterion in [BC-001]; the schedule row, Gantt bar, scope entry, dependency and a plan risk (false positives on short comments) in [PP-001]; the traceability rows. | No | |
| 14 | Review | Record `RC-*` for this milestone, the workflow, the scripts, the tests and the guides, each with a verdict. | No | |


## Verification results

**Tasks 1 to 7, 10 and 13** were done on 2026-10-19 to 2026-10-21 and merged in pull request 211 (and 196 for task 13): the corpus (300 English, 45 Danish, 45 Malay, 48 other), [ADR-0012] (`Proposed`, not yet reviewed), the extractor and detector, the report script, the reusable workflow `english-comments.yml`, 673 offline tests with 98 % coverage of `tools/`, and the guide, README and wiki in three languages. The detector flags 0 of 300 English comments, 44 of 45 Danish and 41 of 45 Malay comments and all 48 of the others; the Danish and Malay comments were written for the test and not checked by a native reader.

**Task 8 (trial on the instance)** was run on 2026-10-21 with the throwaway branch `verify-english-comments` and its pull request 213 (closed, not merged). The sample file holds an English comment, a Danish comment directly under it, a Malay comment, and a Danish comment marked `english-comments: ignore`.

| Run | What was called | Result |
| --- | --- | --- |
| 433 (id 2478), first call at `@main` | the workflow of pull request 211 | Fetched the shared scripts, installed `langid` and `numpy` on the runner, found only the Malay comment (line 9, `id` 0.66); the Danish line next to the English one was **missed** (defect 1). The step "Tell the author" was **skipped**, so no comment was written (defect 2). The run failed. |
| 435 and 437 (ids 2480, 2482), a debug workflow | the contexts of a called workflow | `gitea.event_name` is `workflow_call`; `gitea.event.pull_request.number` (213), the author login and `gitea.base_ref` (`main`) are set. The conditions `always()`, `always() && ...pull_request.number != ''`, `... && ...pull_request.number`, `... && ...pull_request` and `... && gitea.base_ref != ''` ran the step; `gitea.event_name == 'pull_request'` and `github.event_name == 'pull_request'` did not. |
| 440 (id 2485), the fix branch | `english-comments.yml@mil-013-judge-each-line` | Both the Danish line (6, `da` 1.0) and the Malay line (9) were found, the marked line was not reported, the run failed, and the Actions bot (`gitea-actions`) wrote **one** comment (id 8715) that mentions `@Tirsvad` and lists the two findings. |
| 443 (id 2488) | the same, with another Danish comment | "Updated the comment of the check": still one comment (id 8715), with the new text. |
| 445 (id 2490) | both comments rewritten in English | The run passed, the failing step was skipped, and the comment was marked resolved (a "passes" text, no mention). |
| 447 (id 2492) | a Malay comment again | The comment updated; its link `.../actions/runs/2492` equals the `html_url` of the run (defect 3 fixed: the first version linked the run number 440). |

The three defects are fixed in pull request 212 (open at the time of writing): (1) a block of several lines is judged line by line first (at least four words, probability 0.7), then as a whole; (2) the author step asks for `gitea.event.pull_request.number != ''` instead of the event name; (3) the comment links the run by its id. Each has a test.

**Secrets:** the four `english-comments` jobs of runs 440, 443, 445 and 447 were searched for `token <20 or more characters>`, `basic <base64>`, `bearer` and for the value of the token used from this machine; nothing was found. `REPORT_TOKEN` is printed as `***` and the clone header as `AUTHORIZATION: basic ***`. The detector made no network call; the only calls were to the Gitea API of the instance.

**Not shown by the trial:** a call at `@main` of the corrected workflow (it follows the merge of pull request 212); a pull request from a fork (read-only token); a custom `REPORT_TOKEN` secret; the check as a required status that blocks the merge (task 9); and the call of the workflow by this repository (task 11). Tasks 9, 11, 12 and 14 are open.

---

[BC-001]: ../business-case.md
[US-001]: ../user-stories.md
[MIL-004]: ./mil-004-versioned-release.md
[MIL-005]: ./mil-005-wiki-and-translations.md
[MIL-010]: ./mil-010-code-metrics-badges.md
[MIL-011]: ./mil-011-code-metrics-default-tools-ref.md
[MIL-012]: ./mil-012-vpn-actions-for-deployment.md
[MIL-013]: ./mil-013-english-comments-check.md
[ADR-0005]: ../adr/adr-0005-quality-check-contract.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
[ADR-0010]: ../adr/adr-0010-code-metrics-badges-contract.md
[PP-001]: ../project-plan.md
[RC-083]: ../sqa/reviews/rc-083-mil-013-plan.md
[RC-084]: ../sqa/reviews/rc-084-bc-001-o7.md
[RC-085]: ../sqa/reviews/rc-085-mil-013-results.md
[ADR-0012]: ../adr/adr-0012-english-comment-detection.md
[e35b1c5]: https://git.tirsystem.com/TirSystem/github-action/commit/e35b1c56748a50430503f5518602469f93262357
