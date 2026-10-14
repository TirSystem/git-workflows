# Review Record: MIL-011 fix of the tools-ref defaults

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-078 |
| CrossReference | [MIL-011], [RC-077] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | Proposed | Jens Tirsvad Nielsen | AI as stand-in for S01 | Initial version: Go for tasks 2 to 5, criteria 6 to 8 open until the release | [a6892c3] |

---

## Artifact Under Review

- Instance reviewed: the deliverables of tasks 2 to 5 of [MIL-011], branch `mil-011-fix` at `eaa0e30` (the five workflows, `MAJOR_TAG`, `tests/test_tools_ref.py` and the three changed tests, the guides, README and wiki pages in three languages, the amended ADR-0005, ADR-0008, ADR-0009 and ADR-0010, the changelog)
- Checklist used: the eight Go/No-Go criteria of [MIL-011]; for the workflow files and the tests, the review is the pass of the repository's own test suite and the validation workflow
- Scope: full review of the deliverables before the release (task 6); the milestone itself was reviewed in [RC-076] and [RC-077]
- Language and domain: n/a (technical deliverables)
- Mode: autonomous, not independent (the reviewer is `AI as stand-in for S01`)

## Checklist Results

Go/No-Go criteria of [MIL-011]:

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | The defect is reproduced before the fix | Pass | Run 1499 (job 1638): `bash: shared-scripts/tools/code-metrics.sh: No such file or directory`, exit code 127; a call at `@v1` creates no run. Recorded in [MIL-011], "Verification results". |
| 2 | Every default `tools-ref` names a tag that holds the script | Pass | Listed per workflow in [MIL-011]. After the fix all five name `v2` (`MAJOR_TAG`), and the script of each is in `v2`; `test_default_tools_ref_is_the_current_major_and_holds_the_script` checks the tag with `git cat-file`. |
| 3 | The default is derived and a test fails on a seeded wrong default | Pass | `MAJOR_TAG` is the one definition, and a test ties it to the highest major of the changelog. With `default: "v1"` seeded in `code-metrics.yml` three tests failed ("default tools-ref is 'v1', the current major is 'v2'"); restored, 13 passed. The full suite passes: 540 tests. |
| 4 | No guide, comment, README or wiki page tells a caller to use `@v1` for `code-metrics.yml` | Pass | `grep -rn 'code-metrics.yml@v1' guides README.md docs/wiki .gitea` finds 0; no `default: "v1"` is left in `.gitea/workflows`. The accepted ADRs keep their original text and have an amendment; the body of ADR-0010 still reads "default `v1`" above the amendment, which is how amendments are read. |
| 5 | A call with the documented defaults runs on the instance and commits the badges | Pass | Run 1509 (job 1649) of the throwaway branch `verify-code-metrics-defaults`: the workflow at `@mil-011-fix`, `tools-ref` resolved to `v2` (scripts fetched at `16faffa`), "Validate", "Count" and "Publish the badges" succeeded, branch `badges-verify` has the commit `041d991` "Update code metrics badges [skip ci]", and the raw SVG answers `200 image/svg+xml`. Only `badges-branch` was set, to keep the verification away from `badges`. |
| 6 | The release is a patch (2.1.1); `v2` moves to it, `v1` is untouched | Open | Not released: task 6. Re-scored in the record after the release. |
| 7 | The framework `Badges` page no longer tells a caller to set `tools-ref` | Open | Task 7, after the release. |
| 8 | Reviewed | Open | This record covers criteria 1 to 5; the record after the release closes 6 to 8. |

## Overall Verdict

Go for the deliverables of tasks 2 to 5: criteria 1 to 5 pass on the evidence above. Criteria 6 to 8 are open only because the steps that satisfy them (the release and the framework page) come after this review; nothing in the deliverables is missing. The AI accepts the record as stand-in for S01 in autonomous mode; there is no independent reader and the decision stays open to challenge in the run summary.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Release 2.1.1 and re-score criteria 6 and 8 | S05 | 2026-10-23 |
| Remove the `tools-ref` workaround from the framework `Badges` page and re-score criterion 7 | S05 | 2026-10-23 |
| Delete the throwaway branch `verify-code-metrics-defaults` after the results are merged | S05 | 2026-10-23 |

---

[MIL-011]: ../../milestones/mil-011-code-metrics-default-tools-ref.md
[RC-076]: ./rc-076-mil-011-plan.md
[RC-077]: ./rc-077-mil-011-task-1-results.md
[a6892c3]: https://git.tirsystem.com/TirSystem/github-action/commit/a6892c372aca9f2e12826a4c3b260290a0656ecb
