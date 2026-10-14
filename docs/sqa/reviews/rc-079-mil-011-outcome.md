# Review Record: MIL-011 outcome (release 2.1.1)

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-079 |
| CrossReference | [MIL-011], [RC-078] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | Accepted | Jens Tirsvad Nielsen | AI as stand-in for S01 | Initial version; Go; accepted by the AI as stand-in for S01 in autonomous mode, not independent | pending |

---

## Artifact Under Review

- Instance reviewed: the outcome of [MIL-011]: the release `v2.1.1` of this repository (tag on `3023461`, the release page, the moving major tag `v2`) and the framework `Badges` page (`TirSystem/sqa-qc-framework` pull request 57)
- Checklist used: the eight Go/No-Go criteria of [MIL-011]; criteria 1 to 5 were scored in [RC-078] and are not repeated
- Scope: re-score of criteria 6, 7 and 8, after the release
- Language and domain: n/a (technical type)
- Mode: autonomous, not independent (the reviewer is `AI as stand-in for S01`)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 to 5 | See [RC-078] | Pass | Reproduced (run 1499), every default checked, the default derived from `MAJOR_TAG` with a failing seeded test, no `@v1` for `code-metrics.yml`, a run on the instance (run 1509). |
| 6 | The release is a patch (2.1.1); `v2` moves to it, `v1` is untouched | Pass | The Release workflow ran in dry-run mode (run 1524: "Checks passed for v2.1.1 on 3023461 ... would create the release page v2.1.1 and point v2 to it") and then for real (run 1525). `git ls-remote`: `v2.1.1` and `v2` (peeled) are `3023461`; `v1` is `1.2.2` (`9bf0a2b`), unchanged. The release page has the changelog entry as its text. After the release a call at `@v2` with the defaults ran on the instance (run 1526, job 1670): `tools-ref: v2`, the scripts fetched at `3023461`, badges published to `badges-verify`. |
| 7 | The framework `Badges` page no longer tells a caller to set `tools-ref` | Pass | `TirSystem/sqa-qc-framework` pull request 57 is merged and the wiki is published: the three pages have no `tools-ref: v2` line and no bullet about it, call the workflow at `@v2`, and say to use 2.1.1 or later, not 2.1.0. |
| 8 | Reviewed | Pass | [RC-076], [RC-077], [RC-078] and this record, each with a verdict of Go; [MIL-011] and its plan row are `Accepted`. |

## Overall Verdict

Go - all eight criteria pass. The defect is fixed in release 2.1.1: the default `tools-ref` of the five reusable workflows is the current major (`MAJOR_TAG`), a test keeps it so, and a call at `@v2` with the defaults runs. Two things stay as they are and are reported, not decided here: release `2.1.0` still has the defect (a release tag is never moved, ADR-0006) and callers are told to use 2.1.1 or later; and the other four workflows now fetch their scripts from the current major instead of `1.2.2`, which changes no behaviour for a caller at `@v1`. The AI accepts the record as stand-in for S01 in autonomous mode; there is no independent reader and the decision stays open to challenge in the run summary.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Delete the throwaway branch `verify-code-metrics-defaults` when the evidence is no longer needed (a branch deletion is left to a person) | S05 | 2026-10-23 |
| Decide whether the required status check `Sync GitHub mirror metadata / sync-metadata (push)` should stay required on pull requests, where it is only `skipped` and blocks a merge through the API | S05 | 2026-10-30 |

---

[MIL-011]: ../../milestones/mil-011-code-metrics-default-tools-ref.md
[RC-078]: ./rc-078-mil-011-fix.md
[RC-076]: ./rc-076-mil-011-plan.md
[RC-077]: ./rc-077-mil-011-task-1-results.md
