# Review Record: MIL-013 results of tasks 1 to 8, 10 and 13 (MIL-013)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-085 |
| CrossReference | [MIL-013], [QC-MIL-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-21 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted by the author in chat as stand-in for S01 | pending |

---

## Artifact Under Review

- Instance reviewed: [MIL-013]
- Checklist used: [QC-MIL-001]
- Scope: delta re-review of the milestone after [RC-083]: the new `## Verification results` section (the results of the merged work, the trial on the instance and its three defects, the search of the logs), and the added `[ADR-0012]` in the CrossReference. Criteria 1 to 6 are re-read; none of the milestone's own text for them changed. [ADR-0012] is **not** reviewed here: it stays `Proposed` and needs a review against its own checklist
- Language and domain: n/a (technical type)
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, asked in chat on 2026-10-21 for the acceptance and stands in for S01; the AI prepared the evidence)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | Unchanged: release 2.3.0 with the workflow, scripts, guide, wiki, tests, ADR and the two pull requests in the other repositories. The results do not claim any of it is released. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Unchanged, eleven criteria. The results bear on criterion 1 (corpus rates, met on the corpus, with the limits of an AI-written corpus said), 3 (a pull request with a Danish comment fails, one without passes: met in runs 440 and 445), 4 (an exception can be marked: met, the marked line was not reported), 5 (one comment that mentions the author, updated, resolved: met when the fix branch is called) and 6 (no token in a log: met for the four jobs searched; the detector made no network call). Criteria 7 to 11 are not claimed. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged; [ADR-0012] is added to the CrossReference and exists. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | Unchanged: objective O7 and success criterion 7 of [BC-001] ([RC-084]). |
| 5 | Milestone owner and approving reviewer are identified | Pass | Unchanged: owner S05, approving reviewer S01. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | Unchanged: 2026-11-20. Open tasks 9, 11, 12 and 14 and the merge of pull request 212 are before it; task 9 needs the owner. |

## Results check

| # | Claim in the results | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | The first call at `@main` found only the Malay comment and skipped the author step | Pass | Read from the log of job 2761 of run 433 (id 2478): one finding at `trial/sample.py:9`, and the step list shows "Tell the author" skipped. |
| 2 | In a called workflow `gitea.event_name` is `workflow_call` | Pass | Printed by the debug workflow in runs 435 and 437: `event_name=workflow_call number=213 author=Tirsvad base_ref=main`; the steps with the event-name conditions are listed as skipped, the others as success. |
| 3 | The fix branch finds both comments, writes one comment, updates it, resolves it | Pass | Runs 440, 443 and 445 read from the API: the comment list of pull request 213 held one comment (id 8715) after each run; its text after run 445 was the "passes" text without a mention. |
| 4 | The run link equals the run's address | Pass | The link in the comment after run 447 is `https://git.tirsystem.com/TirSystem/github-action/actions/runs/2492`, the `html_url` of run 447. |
| 5 | No credential in the logs | Pass | A search of four job logs; the only lines matching were `REPORT_TOKEN: ***`. The search patterns cannot find a short or oddly formed secret, which the result says by naming the patterns. |
| 6 | The open items are listed honestly | Pass | The result names what the trial did not show: a corrected call at `@main`, a fork pull request, a custom token, the required check, and the call by this repository. |

## Overall Verdict

Go - the results recorded are accurate and claim no more than the evidence shows. The author confirmed the acceptance in chat on 2026-10-21 as stand-in for S01; this is not an independent review.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Review [ADR-0012] against its checklist and accept or change it; it is `Proposed` | S01 | Before task 11 (release 2.3.0) |
| Review and merge pull request 212 (the three defects); call the corrected workflow at `@main` once more | S01 | 2026-11-06 |
| Task 9: decide which repositories mark the check as required and set it | S01 | 2026-11-13 |
| Confirm this record by S01 when an independent reading is possible | S01 | 2026-11-09 |

---

[MIL-013]: ../../milestones/mil-013-english-comments-check.md
[BC-001]: ../../business-case.md
[ADR-0012]: ../../adr/adr-0012-english-comment-detection.md
[RC-083]: ./rc-083-mil-013-plan.md
[RC-084]: ./rc-084-bc-001-o7.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
