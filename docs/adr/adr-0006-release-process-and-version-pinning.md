# ADR-0006: Release process and version pinning

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0006 |
| CrossReference | [MIL-004], [UC-006], [US-001], [ADR-0004], [ADR-0005] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version | pending |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Reviewed (RC-043): SemVer expanded at first use | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

Every consumer of the shared workflows runs this repository's code, and today
that code is whatever `main` holds: the scoped workflows (sync and publish
wiki) are delivered from `main` and fetch their scripts at `ref: main`, and
the reusable quality-check workflow is called as `@main` in the guide. A merge
to `main` therefore changes the pipelines of repositories in four
organizations at their next run, with no version, no changelog and no way to
stay on the previous behaviour. MIL-004 gives releases a version.

Facts that shape the decision:

- A reusable workflow is referenced with `@<ref>` where the ref may be a
  branch or a tag (verified on 2026-10-10), and a tag is not deleted when a
  pull request is merged, unlike the branch the first trial used.
- A **scoped** workflow is delivered by the instance from `main` of this
  repository; a consumer cannot pin it. Only what the workflow fetches (the
  script files) and what a consumer calls explicitly (the reusable workflow)
  can be pinned.
- The repository has a validation run (YAML parse, offline tests, wiki
  freshness) that is green or red per commit, and no release process, no
  changelog and no tags yet.

Options for the unit and the scheme of a version:

1. **One version for the whole repository** with a semantic version (SemVer) tag `vMAJOR.MINOR.PATCH`
   and a moving major tag `vMAJOR`. One changelog, one release page.
2. **One version per workflow** (`quality-checks/v1.2.0`). Precise, but five
   moving parts for one maintainer, and the scripts and guides span several
   workflows.
3. **Date-based tags** (`2026.10.10`). Simple, but they say nothing about
   whether a change is breaking.
4. **No versions; consumers copy the files.** The situation MIL-002 moved away
   from.

Options for how a consumer pins:

a. **Exact tag** (`@v1.2.0`): never changes, never receives fixes.
b. **Moving major tag** (`@v1`): receives compatible releases only.
c. **`@main`**: always the newest, unreviewed by the consumer.

## Decision

The repository is released as a whole with a SemVer tag `vMAJOR.MINOR.PATCH`
and a moving major tag `vMAJOR` that always points to the latest compatible
release, and consumers pin `@vMAJOR` or an exact tag and never `@main`. A
release is created from `main` only when the validation run of that exact
commit is green and `CHANGELOG.md` has an entry for the version that marks
each breaking change, and it is announced by a release page generated from
that entry.

The rules that follow from it:

- **Breaking (new major):** renaming or removing a workflow, an input, a
  secret name or an output; raising a default tool version or changing a
  default so that a previously green consumer can turn red; changing the
  meaning of a pass or a fail (ADR-0005).
- **Minor:** a new optional input, a new workflow or a new capability that
  changes nothing for existing callers. **Patch:** a fix, or a change of
  documentation or tests, with no visible change for consumers.
- **First release:** `v1.0.0`, with `v1` pointing to it.
- **Tags are not deleted or moved,** except that the major tag moves forward
  with each compatible release and may be moved back to the previous exact
  tag when a release proves faulty.
- **Who:** the DevOps Professional (S05) cuts the release and S01 approves it;
  a release that touches credentials, tokens or permissions says so in the
  changelog.
- **Scripts:** once `v1` exists the scoped workflows fetch their scripts at
  `ref: v1` instead of `main`, so that a merge to `main` stops reaching
  consumers until it is released.
- **Not automated yet:** the steps are a checklist in
  `guides/release-process.md`; the release workflow is task 5 of MIL-004.

## Consequences

**Positive:**

- A consumer chooses between "never changes" (`@v1.2.0`) and "compatible
  fixes only" (`@v1`), and a breaking change cannot reach a pipeline that
  pins a major version.
- A merge to `main` no longer reaches consumers of the scripts and the
  reusable workflow until it is released, so a faulty merge costs a revert,
  not an incident in four organizations.
- The changelog gives S02 and S03 one place to see what changed and whether
  credentials or permissions are involved.

**Negative:**

- **A scoped workflow file is still delivered from `main`:** a consumer cannot
  pin it, so a bad merge of `sync-github-metadata.yml` or `publish-wiki.yml`
  still reaches every repository at its next run. Review of `main` is the only
  protection for those two files, and the release process cannot change that.
- Moving the major tag needs permission to force-update a tag, which is a
  second sensitive permission next to merging.
- One version for the whole repository means a fix to one workflow produces a
  release for all, and a consumer of one workflow sees changelog entries that
  concern another.
- Raising a default tool version is treated as breaking, so keeping the
  quality checks current costs a major version each time.

## Affected Artifacts

- [MIL-004] — tasks 2 to 5 (issues #21 to #24) implement the changelog and tag
  convention, the upgrade guide, the publish destination and the release
  workflow on this decision.
- [UC-006] — the use case this process serves.
- [US-001] — stories US-001.11 to US-001.13 state its acceptance criteria.
- [ADR-0005] — its pinned tool versions become defaults that a release moves.
- [ADR-0004] — the scoped publish-wiki workflow is covered by the limitation
  above.

---

[MIL-004]: ../milestones/mil-004-versioned-release.md
[UC-006]: ../uc-006/uc.md
[US-001]: ../user-stories.md
[ADR-0004]: ./adr-0004-shared-wiki-publishing-opt-in.md
[ADR-0005]: ./adr-0005-quality-check-contract.md
