# Review Record: MIL-012 results of tasks 1, 6 and the review fixes (MIL-012)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-082 |
| CrossReference | [MIL-012], [QC-MIL-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; accepted by the author in chat as stand-in for S01 | [3325bea] |

---

## Artifact Under Review

- Instance reviewed: [MIL-012]
- Checklist used: [QC-MIL-001]
- Scope: delta re-review of the milestone after [RC-080]: the new `## Verification results` section (task 1, task 6, the fixes made after the review of pull request 194), the added `[ADR-0011]` in the CrossReference, and the claims about open tasks. Criteria 1 to 6 are re-read; none of the milestone's own text for them changed. [ADR-0011] is **not** reviewed here: it stays `Proposed` and needs a review against its own checklist
- Language and domain: n/a (technical type)
- Mode: supervised, not independent (the author, Jens Tirsvad Nielsen, asked in chat on 2026-10-19 for the acceptance and stands in for S01; the AI prepared the evidence)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | A concrete deliverable is defined for every gate | Pass | Unchanged: release 2.2.0 with the two actions, guides, wiki pages in three languages, ADR, framework templates pinned. The results section does not claim any of it is delivered; it lists tasks 2 to 5, 7, 8 and 10 to 12 as open. |
| 2 | Explicit Go/No-Go criteria are stated for each gate | Pass | Unchanged, ten criteria. The results bear on two of them. Criterion 1 (a `uses:` of a subfolder action resolves, the form recorded): runs 417 and 418 show both forms resolve at `@main`, and the failure at the deleted branch is explained by the log text "reference not found". Criterion 6 (scripts linted in CI, a seeded error fails): met by `tools/lint-action-scripts.sh` and its tests on the working branch; the pull-request run of the new step is the final evidence. The other eight criteria are not claimed. |
| 3 | Dependencies on other milestones are explicitly mapped | Pass | Unchanged; [ADR-0011] is added to the CrossReference and exists. |
| 4 | Each milestone is traceable to a Business Case objective or KPI | Pass | Unchanged: objective O6 and success criterion 6 of [BC-001], reviewed in [RC-081]. |
| 5 | Milestone owner and approving reviewer are identified | Pass | Unchanged: owner S05, approving reviewer S01. |
| 6 | Milestone has a defined target date consistent with project constraints | Pass | Unchanged: 2026-11-06. The open tasks 2 to 5 need the operator's runner (S03); the milestone states the dependency, and the date is at risk until the runner exists. |

## Results check

| # | Claim in the results | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | Task 1: both forms resolve at `@main` | Pass | Run 418 (`.../actions/runs/2425`): jobs `wg-short`, `wg-full`, `ts-short`, `ts-full` each executed the action's `mask` step and main step and failed with the action's own `[configuration]` error. Read from the job logs through the API. |
| 2 | Run 417 failed because the branch was deleted | Pass | `git ls-remote` showed no `wireguard-vpn-action` head after pull request 194 merged; the log says `Unable to resolve wireguard-vpn-action: reference not found`. |
| 3 | Task 6: lint script, workflow step, pinned tools, seeded-error test | Pass | `tools/lint-action-scripts.sh`; the test file seeds a shellcheck problem and a badly formatted script, shows both fail, and shows the two action scripts pass; the full suite (590 tests) passes locally. Not yet run by the instance's CI. |
| 4 | The ten findings of the review of pull request 194 are answered | Pass | Each has a code change and an offline test (the daemon wait with a delayed stub, `sudo` that resets the environment, a host daemon not taken over, a line break refused, the key file removed on failure, `latest` refused). The wording of the results says they are offline-tested with stubs and that tasks 3 and 4 must show them on a runner. |
| 5 | Open tasks are listed honestly | Pass | Tasks 2, 3, 4, 5, 7, 8, 10, 11 and 12 are named as open, with the reason. |

## Overall Verdict

Go - the results recorded are accurate and claim no more than the evidence shows. The author confirmed the acceptance in chat on 2026-10-19 as stand-in for S01; this is not an independent review.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Review [ADR-0011] against its checklist and accept or change it; it is `Proposed` | S01 | Before task 10 (release 2.2.0) |
| Provide the `vpn` runner, the WireGuard peer and the Tailscale tag with an OAuth client for tasks 3 and 4; the target date 2026-11-06 depends on it | S03 | 2026-10-30 |
| Confirm this record by S01 when an independent reading is possible | S01 | 2026-11-02 |

---

[MIL-012]: ../../milestones/mil-012-vpn-actions-for-deployment.md
[BC-001]: ../../business-case.md
[ADR-0011]: ../../adr/adr-0011-vpn-composite-actions.md
[RC-080]: ./rc-080-mil-012-plan.md
[RC-081]: ./rc-081-bc-001-o6.md
[QC-MIL-001]: ../../../framework/qc/artifacts/qc-milestones-gateways.md
[3325bea]: https://git.tirsystem.com/TirSystem/github-action/commit/3325bea772304b54e8dfffad592b4afadc3ec2b8
