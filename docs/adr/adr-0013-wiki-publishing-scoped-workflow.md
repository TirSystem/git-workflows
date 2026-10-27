# ADR-0013: Wiki publishing as a scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0013 |
| CrossReference | [MIL-014], [ADR-0009], [ADR-0004] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; Accepted on a Go review (RC-086); accepted by the author in chat on 2026-10-27 as stand-in for S01, not independent | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

[ADR-0004] published wikis with a scoped workflow and a marker file
`wiki/.publish`. [ADR-0009] replaced it with the reusable workflow
`publish-wiki-pages.yml`, because the marker was an opt-in the workflow had to
guard, and a repository needed to say where its wiki is. Since then the folder
is settled: the framework prescribes the wiki in `docs/wiki/`, and every
publishing repository uses the defaults. Seven repositories carry a caller file
with the same trigger and the same secret, and the only setting a caller adds
to the defaults is `prune`; each caller is a file to keep current when the
workflow changes.

Options:

1. **Keep the reusable workflow.** Explicit opt-in per repository, but a caller
   file per repository that repeats the same trigger and the same secret.
2. **A scoped workflow that runs in every repository and publishes when
   `docs/wiki/` exists.** Nothing to copy or call; the opt-in is the folder
   itself, which is also what the content is.
3. **A scoped workflow with a marker file.** The marker was the thing
   [ADR-0009] removed; the folder says the same thing.

## Decision

Wiki publishing is the scoped workflow `.gitea/scoped_workflows/publish-wiki-pages.yml`,
which runs in every repository and publishes `docs/wiki/` when the folder
exists; the reusable workflow, its inputs and the caller files are removed.

The rules that follow from it:

- The settings are fixed, not inputs: the folder is `docs/wiki`, pruning is off,
  and the script is fetched from this repository at the current major tag.
- The secret `TOKEN_FOR_GITEA_WIKI` is read from the organization secrets of the
  running repository; there is no fallback to another token.
- The workflow runs on a push to `main` that changes `docs/wiki/**`, and
  manually, and ends without doing anything when the folder does not exist.
- Pages that are in the wiki but not in the folder are kept, so a repository
  that needs pruning removes them by hand.
- The script, the page-title rules, the empty-folder protection and the error
  categories of [ADR-0004] and [ADR-0003] are unchanged.

## Consequences

**Positive:**

- Nothing to add to a repository: a folder `docs/wiki/` is the whole opt-in, and
  there is one workflow to maintain instead of one plus seven callers.
- A change to the workflow reaches every repository at once, the way the
  metadata sync does.

**Negative:**

- Security: every repository of an organization that has `docs/wiki/` can write
  its own wiki with the organization token. A repository that must not publish
  has to disable its wiki or not use the folder; before the release a scan names
  the repositories that would start publishing (`027-sandbox` and `028-pomodoro`
  did not in MIL-009).
- A repository cannot choose another folder or prune; the repositories whose
  caller sets `prune: "true"` lose that, and a page deleted from `docs/wiki/`
  then stays in the wiki. One that needs either stays on `@v2` of the reusable
  workflow, which keeps working because the `v2` tag is not moved.
- Removing the reusable workflow is a breaking change under [ADR-0006]: release
  3.0.0. A repository that keeps its caller at `@v3` fails and one that keeps
  both publishes twice, so the callers are removed first (MIL-014 task 5).
- A scoped workflow cannot be pinned by a repository and follows the major tag
  of the script; a faulty script release reaches all repositories until the tag
  is moved back.
- It reverses a decision reached two weeks earlier ([ADR-0009]) and the
  framework template `templates/ci/publish-wiki.yml` is retired with it.

## Affected Artifacts

- [MIL-014] — the plan this decision belongs to.
- [ADR-0009] — its delivery and caller parts are replaced; its token rule and
  the amendment of the `tools-ref` default stand as history for `@v2`.
- [ADR-0004] — its token and safety rules stand; its marker is not restored.

---

[MIL-014]: ../milestones/mil-014-wiki-publishing-scoped-again.md
[ADR-0003]: ./adr-0003-wiki-publish-token.md
[ADR-0004]: ./adr-0004-shared-wiki-publishing-opt-in.md
[ADR-0006]: ./adr-0006-release-process-and-version-pinning.md
[ADR-0009]: ./adr-0009-wiki-publishing-reusable-workflow.md
