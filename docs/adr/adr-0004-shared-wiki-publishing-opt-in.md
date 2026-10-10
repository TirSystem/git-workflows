# ADR-0004: Opt-in rule and secret handling of the shared wiki publisher

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0004 |
| CrossReference | [MIL-006], [ADR-0003], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version | pending |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Reviewed (RC-018): the `prune` variant added to the evaluated options | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

MIL-006 turns the Publish wiki workflow into a scoped workflow, which Gitea
runs in every repository of every organisation on the instance (verified,
issue #9). The publisher writes to a repository's wiki and removes pages that
are not in `wiki/`. Without a gate, any of the 26 repositories of
`Tirsvad-Udemy-100-days-of-code`, or any other repository, that happens to
have a `wiki/` folder would have its wiki overwritten or emptied by a
workflow it never asked for. The secret is also per organisation, so the
shared workflow must say what happens where it is missing, and
[ADR-0003] let this repository fall back to `TOKEN_FOR_GITEA`.

Options for how a repository opts in:

1. **A marker file `wiki/.publish`** on the default branch. Visible in the
   repository, reviewed in a pull request, and nothing to configure in an
   organisation. It comes in two forms:
   - **(a) the marker alone** makes the wiki equal `wiki/`, so pages that are
     not in the folder are deleted, as in ADR-0003;
   - **(b) the marker plus the word `prune`** in it: without the word the
     workflow only creates and updates pages, and deleting is a second,
     explicit choice.
2. **A repository variable** (for example `PUBLISH_WIKI=true`). Not part of
   the repository content, so it is not reviewed or versioned, and it has to
   be set in the web interface once per repository.
3. **An allow list** in this repository. One place to read, but every
   repository in every organisation has to ask this repository for a change.
4. **Publish whenever `wiki/` exists.** No setup, which is the risk the gate
   is meant to remove.

Option 1(b) is chosen for the reason in the first paragraph: a repository
that adds `wiki/` to a wiki it wrote by hand should not lose that wiki by
opting in.

Options for the secret:

1. **`TOKEN_FOR_GITEA_WIKI` of the organisation only.** The sync token stays
   read-only everywhere.
2. **Fall back to `TOKEN_FOR_GITEA`** as in ADR-0003. A missing wiki secret is
   hidden until a write is refused (HTTP 403).

## Decision

A repository opts in by committing `wiki/.publish` on its default branch; the
file may contain the single word `prune`, which is the only thing that lets the
workflow delete wiki pages that are not in `wiki/`, and without the marker the
workflow ends successfully without any request. The shared workflow uses the
organisation's `TOKEN_FOR_GITEA_WIKI` only, and fails with a configuration
error when a repository has opted in and the secret is missing.

The rules that follow from it:

- Without `prune` the workflow only creates and updates pages.
- An empty `wiki/` (no Markdown page) never deletes anything, with or without
  `prune`.
- A repository that has not opted in is skipped with one log line, so its
  runs stay green.
- This repository commits `wiki/.publish` containing `prune`, because its wiki
  must equal `wiki/` (ADR-0001, ADR-0003).
- The fallback to `TOKEN_FOR_GITEA` of ADR-0003 is removed from the shared
  workflow; the sync token is read-only everywhere.

## Consequences

**Positive:**

- A repository that did not opt in is never written to, and the marker is a
  reviewed change in the repository that wants it.
- Deleting pages is a second, explicit choice, so adopting the workflow in a
  repository with hand-written wiki pages loses nothing.
- A missing wiki secret is reported where it happens, in the repository that
  opted in, and the sync token never gets write access.

**Negative:**

- Each organisation that wants this needs its own `TOKEN_FOR_GITEA_WIKI`; it
  cannot borrow the sync token.
- A repository that opts in without `prune` keeps pages that were removed from
  `wiki/`, so its wiki can drift from the folder until someone adds `prune`.
- Anyone with write access to a repository can opt it in and, with `prune`,
  make the workflow delete its wiki pages; that is the intended scope of write
  access, but it is not a separate approval.
- The change supersedes the fallback part of [ADR-0003], so the credentials
  guide and the wiki pages that mention it need an update (MIL-006 task 5).

## Affected Artifacts

- [MIL-006] — tasks 2, 3 and 4 (issues #57 to #59) implement and pilot this
  decision.
- [ADR-0003] — its fallback to `TOKEN_FOR_GITEA` no longer applies to the
  shared workflow.
- [ADR-0002] — the stand-in rule applies to the review of this ADR.

---

[MIL-006]: ../milestones/mil-006-shared-wiki-publishing.md
[ADR-0003]: ./adr-0003-wiki-publish-token.md
[ADR-0002]: ./adr-0002-s01-approves-as-stand-in.md
