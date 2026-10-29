# ADR-0017: Release of any repository as a scoped workflow

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0017 |
| CrossReference | [MIL-018], [MIL-017], [ADR-0006], [ADR-0007], [ADR-0016] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; reviewed (RC-101, Go-with-conditions), accepted by the author in chat as stand-in for S01 with the conditions of RC-101 still open, not independent | [a1c9cbd] |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

`release.yml` releases this repository only. It creates the version tag, the
release page from the changelog entry and the major tag, after it has checked
that the commit is the tip of `main`, that the run `Validate workflows /
validate (push)` is green and that the changelog has an entry ([ADR-0006],
[ADR-0007]). The framework repository makes its tag and page by hand. [ADR-0007]
let the run use its own token and named the secret `TOKEN_FOR_GITEA_RELEASE` as
the fallback if that token could not write tags; the working tree of this
repository has already dropped the fallback from the workflow.

Read from the code and the changelogs of two repositories on 2026-10-29:

| Fact | Where it comes from |
| --- | --- |
| The script has the branch `main` and the status `Validate workflows / validate (push)` as defaults | `tools/release.py` |
| The changelog tool reads `## [1.2.0] - 2026-10-21` only | `tools/changelog.py` |
| The framework repository writes `## 0.18.0 (2026-10-28)` headings and `## Unreleased` | `framework/CHANGELOG.md` (the submodule at v0.18.0) |
| The major tag `vN` is moved for the highest version of a major, including `0.x` | `plan_tags` in `tools/release.py` |
| The calls made: read the branch, the commit status and the tags; create the release page; delete and create the major tag | `tools/release.py` |
| Whether the token of a scoped run can write a tag or a page | not known; [MIL-018] task 1 verifies it, and the decision below does not depend on it |

Options:

1. **Keep a release workflow per repository.** A copy to keep current in each
   repository, and the framework repository still has none.
2. **A scoped workflow with the token of the run.** Nothing to store, but a
   scoped workflow runs in repositories where that token may not write tags,
   and what it can write differs by repository.
3. **A scoped workflow with a dedicated token `TOKEN_FOR_GITEA_RELEASE`, no
   fallback.** One behaviour everywhere; the token is a secret to store and
   rotate.
4. **Release by hand.** What the framework repository does today; the checks are
   not enforced.

## Decision

A repository is released by the scoped workflow
`.gitea/scoped_workflows/release.yml`, started by hand, which writes with the
organization secret `TOKEN_FOR_GITEA_RELEASE` and refuses to run without it.

The rules that follow from it:

- **Inputs:** `version` (`MAJOR.MINOR.PATCH`, no leading `v`) and `dry_run`,
  default `true`: a dry run checks and prints and writes nothing. The group
  `release` queues runs and never cancels one.
- **The secret is required, with no fallback** to the token of the run or to any
  other secret. A run without it ends as `[configuration]` and names the secret.
  It is a Gitea token with the scope `write:repository`, owned by a dedicated
  user, stored as an organization secret by S03 and approved by S05; it is
  rotated on the schedule of the credentials guide. It is read in the
  environment of the one step that runs the script and never appears on a
  command line. The workflow itself has `permissions: contents: read`.
- **The calls** are `GET` of the repository (the default branch), the branch, the
  status of the commit and the tags; `POST` of the release page and of the major
  tag; `DELETE` of the major tag. A test compares them with the guide.
- **The workflow refuses** a commit that is not the tip of the default branch
  (read from the API, not assumed to be `main`), a missing or red status
  `Validate / validate (push)` ([ADR-0016]), a changelog without an entry for
  the version and a tag that exists. Each refusal is `[validation]`.
- **Both changelog formats are read:** `## [1.2.0] - 2026-10-21` and
  `## 0.18.0 (2026-10-28)`; the unreleased heading is `## Unreleased` or `## [Unreleased]`.
- **The major tag** `vN` exists from version 1.0.0 only: a `0.x` release makes
  none. It moves only for the highest version of its major, so a patch of an
  older major never moves it. Exact tags are never moved.
- **The release page is the only destination** ([ADR-0007]); its body is the
  changelog entry.
- The script is a file of this repository, fetched at the current major tag
  ([ADR-0005]).
- `.gitea/workflows/release.yml` is removed; the next release of this
  repository is a new major version, because the removed workflow and the
  required secret are breaking.
- [ADR-0006] (the default branch and the major tag from 1.0) and [ADR-0007] (the
  token is the dedicated secret, not the token of the run) are amended; each
  gets a row that points here.

## Consequences

**Positive:**

- Any repository can be released the same way, with the same checks, and the
  framework repository stops releasing by hand.
- The release is refused when the repository is not green, wherever it is.
- The token is described once, with its scope, owner and rotation.

**Negative:**

- A secret that can write tags and release pages in every repository of an
  organization is a high-value target; a repository's workflow files or a
  collaborator who can start a scoped run can use it. It is limited by being
  organization-scoped per organization and by the dedicated user, and the
  concern is recorded for S01.
- A release in a repository without `Validate / validate (push)` is refused until
  [MIL-017] is released and has run there.
- A breaking change for the callers of the old workflow: a new major version.
- The workflow fetches its script at a major tag, so the script and the
  workflow in `main` must be released together.

## Affected Artifacts

- [MIL-018] — the milestone this decision belongs to.
- [MIL-017] — supplies the status that is required.
- [ADR-0006] — amended: the default branch and the major tag from 1.0.
- [ADR-0007] — amended: the token is the dedicated secret.
- [ADR-0016] — fixes the name of the status.

---

[MIL-018]: ../milestones/mil-018-scoped-release-workflow.md
[MIL-017]: ../milestones/mil-017-scoped-validation-workflow.md
[ADR-0005]: ./adr-0005-quality-check-contract.md
[ADR-0006]: ./adr-0006-release-process-and-version-pinning.md
[ADR-0007]: ./adr-0007-release-publish-destination.md
[ADR-0016]: ./adr-0016-scoped-validation-workflow.md
[a1c9cbd]: https://git.tirsystem.com/TirSystem/git-workflows/commit/a1c9cbd914fa1583f51a8267dd63578e76557eb5
