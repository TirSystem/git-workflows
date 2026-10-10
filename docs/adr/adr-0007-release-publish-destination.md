# ADR-0007: Publish destination and token scope of a release

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0007 |
| CrossReference | [MIL-004], [UC-006], [ADR-0006] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version (RC-047) | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

ADR-0006 decides that this repository is released as a whole with a version
tag and a release page generated from `CHANGELOG.md`. Task 4 of MIL-004 asks
where a release is published and which permission publishing needs, before the
release workflow (task 5) is written.

Facts that shape the decision:

- This repository contains workflows, scripts and guides. Nothing is compiled
  or packaged: a consumer receives a release by referencing the tag
  (`uses: ...@v1`), not by downloading a file.
- The Gitea instance (1.27.3) offers, through its REST API, creation of tags
  and of releases, deletion of a tag, and attachments on a release.
- The repository is mirrored to GitHub, but the shared workflows are called
  from Gitea runners of four organizations, so consumers read the Gitea copy.
- Creating a release and moving the major tag are the two sensitive writes of
  the release process (ADR-0006).

Options for the destination:

1. **The release page of this repository** (tag plus notes from the changelog).
2. **A package in the Gitea package registry** (for example a generic package
   holding an archive of the repository).
3. **A release page on the GitHub mirror** in addition to option 1.
4. **Tags only**, without a release page.

Options for the permission:

a. **The token the job receives for its own run**, limited to this repository.
b. **A dedicated secret** with a personal access token that may write to this
   repository only.
c. **The existing `TOKEN_FOR_GITEA`** of the organization.

## Decision

A release is published as the release page of `TirSystem/github-action` on
Gitea, created from the changelog entry for the tag, with no package and no
attachments, and the release workflow publishes it with the token its own run
receives (options 1 and a). If that token proves unable to create the tag or
to move the major tag, the fallback is a dedicated secret
`TOKEN_FOR_GITEA_RELEASE` that may write to this repository only (option b).
`TOKEN_FOR_GITEA` is not used for releases.

The rules that follow from it:

- **What is published:** the tag `vMAJOR.MINOR.PATCH`, the major tag, and one
  release page whose body is the output of
  `python tools/changelog.py notes x.y.z`.
- **Permission needed:** write access to the contents of this repository
  (create a tag, create and edit a release, delete and recreate the major
  tag), nothing else. It needs no access to other repositories, to the wiki or
  to organization settings.
- **The GitHub mirror** receives the tags through its normal mirroring and has
  no release page of its own; the changelog file is the same on both.
- **A package registry is reconsidered** only if a release ever contains a
  built file that consumers download.

## Consequences

**Positive:**

- One place, the release page, shows what changed and whether to act, next to
  the tag consumers pin.
- No new secret is stored while the job token is enough, and the permission is
  limited to one repository and the lifetime of one run.
- Nothing to build, sign or version besides the tag.

**Negative:**

- The job token may not be allowed to move a tag where tag protection is set;
  this is not verified until the release workflow of task 5 runs, and the
  fallback needs a secret that someone must create and rotate.
- Consumers on GitHub see tags but no release page.
- Without attachments a consumer cannot download a release as a file; the tag
  is the only form.

## Affected Artifacts

- [MIL-004] — decides criterion 4 of its Go/No-Go table and unlocks task 5.
- [UC-006] — "the release page for the tag is created from the changelog
  entry" states where.
- [ADR-0006] — whose release steps this publishes.

---

[MIL-004]: ../milestones/mil-004-versioned-release.md
[UC-006]: ../uc-006/uc.md
[ADR-0006]: ./adr-0006-release-process-and-version-pinning.md
