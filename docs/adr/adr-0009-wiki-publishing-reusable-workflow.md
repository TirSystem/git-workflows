# ADR-0009: Wiki publishing as a reusable workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0009 |
| CrossReference | [MIL-008], [ADR-0003], [ADR-0004], [ADR-0005], [ADR-0006] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-13 | Accepted | Jens Tirsvad Nielsen | S01 | Review findings fixed (RC-063): the product owner's language is spelled out, the security consequence is named, and the secret passing is recorded as verified | [8c2c52e] |
| 2026-10-14 | Proposed | Jens Tirsvad Nielsen | S01 | Amendment: the default `tools-ref` is the current major tag (MIL-011) | [eaa0e30] |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

[ADR-0004] chose a scoped workflow to publish wikis: Gitea runs it in every
repository of an organisation, and a marker file `wiki/.publish` is the opt-in.
That avoids a copy of the workflow, but it runs where nobody asked for it and
needs a safety gate for that reason; its trigger path (`wiki/**`) and the
version of the script (`v1`) are fixed centrally. The framework now prescribes
the wiki in `docs/wiki/` with English and the product owner's language as a
minimum, and
repositories need to say where their wiki is.

Options:

1. **Keep the scoped workflow and read both folders.** No file in consumers,
   but the central trigger lists every location and the gate stays.
2. **A reusable workflow (`workflow_call`) that each repository calls.** One
   source in this repository, called as `uses: ...@v1` the way
   `quality-checks` and `release` already are ([ADR-0005], [ADR-0006]). The
   caller sets its own trigger paths and the folder.

## Decision

Wiki publishing is the reusable workflow `publish-wiki-pages.yml`, called by
each repository that wants a published wiki; the caller file is the opt-in and
`docs/wiki/` is the default folder. The scoped `publish-wiki.yml` and the
`wiki/.publish` marker are deprecated and stay until every publishing repository
has a caller; they are then removed in a later major release.

The rules that follow from it:

- Inputs: `wiki_dir` (default `docs/wiki`), `prune` (default `false`) and
  `tools-ref` (default `v1`). The secret `TOKEN_FOR_GITEA_WIKI` is declared and
  passed by the caller; there is no fallback to another token.
- With the reusable workflow the marker is not read: the script treats the
  `prune` input as the setting, and a missing folder is a configuration error
  rather than a skip, because the caller asked for it.
- The script, the page-title rules, the empty-folder protection and the error
  categories of [ADR-0004] and [ADR-0003] are unchanged.

## Consequences

**Positive:**

- A repository states its own folder and trigger paths, so the wiki can move
  to `docs/wiki/` one repository at a time.
- Opting in is a file in the repository, reviewed in a pull request, and a
  repository without a caller is never written to.
- Security: the token is passed explicitly by the caller and is never
  inherited or taken from a fallback, so a repository that does not pass it
  cannot write a wiki.
- One call convention for every shared workflow of this repository.

**Negative:**

- Every publishing repository needs a caller file, and the removal of the
  scoped workflow stops publishing in any repository that still relies on the
  marker; the list of those repositories is taken before the removal.
- Eight repositories still publish through the scoped workflow (checked on
  2026-10-13), so it is deprecated and not removed here; removing it is a
  breaking change under [ADR-0006] and belongs to a follow-up milestone with
  their migrations.
- The owner chose a patch release (1.2.2) for this change although a new
  workflow is a minor one under [ADR-0006]; the changelog states the deviation.
- Anyone who can change the caller file of a repository can change the folder
  and `prune`, and so what the token deletes in that repository's wiki; this is
  the same exposure as the marker had, and it is reviewed through the pull
  request that changes the caller.
- Passing a declared secret through `workflow_call`, and a local `uses:` call,
  were verified on this Gitea instance by run 316 of this repository on
  2026-10-13.

## Affected Artifacts

- [MIL-008] — the plan this decision belongs to.
- [ADR-0004] — its scoped delivery and marker parts are replaced once the
  scoped workflow is removed; its token and safety rules stand.


## Amendment (MIL-011)

The default of the input `tools-ref` in the wiki publishing contract is the current major tag, defined once in the file
`MAJOR_TAG` of this repository (`v2` from release 2.1.1), and no longer `v1`. A default must
name a tag that holds the script the workflow runs; a test checks it. Callers at `@v1` are
not affected: the `v1` tag keeps the `v1` workflow files.

---

[MIL-008]: ../milestones/mil-008-wiki-reusable-workflow.md
[ADR-0003]: ./adr-0003-wiki-publish-token.md
[ADR-0004]: ./adr-0004-shared-wiki-publishing-opt-in.md
[ADR-0006]: ./adr-0006-release-process-and-version-pinning.md
[ADR-0005]: ./adr-0005-quality-check-contract.md
[01b9c29]: https://git.tirsystem.com/TirSystem/github-action/commit/01b9c2972b4317bcc590540010aea0eaf7f30014
[8c2c52e]: https://git.tirsystem.com/TirSystem/github-action/commit/8c2c52ebd2a27e4d0edb4008c31c002718d280fb
[eaa0e30]: https://git.tirsystem.com/TirSystem/github-action/commit/eaa0e30beaa097dfeb1c07c814a71d02a6987060
