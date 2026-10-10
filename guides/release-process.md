# Release process

For the maintainers of this repository: how a change to the shared workflows
is validated, versioned and announced, and how consumers pin a version. The
decisions are in ADR-0006; this guide is the checklist. It is not published
on the wiki.

Until the release workflow exists (MIL-004 task 5) the steps are done by hand.

## What a version is

| Item | Rule |
| --- | --- |
| Unit | The whole repository: the workflows, their scripts and the guides |
| Version tag | `vMAJOR.MINOR.PATCH`, for example `v1.2.0`; never deleted or moved |
| Major tag | `vMAJOR`, for example `v1`; points to the latest compatible release |
| First release | `v1.0.0` |
| Breaking (new major) | A renamed or removed workflow, input, secret name or output; a raised default tool version or a changed default that can turn a green consumer red; a changed meaning of pass or fail |
| Minor | A new optional input, workflow or capability; nothing changes for existing callers |
| Patch | A fix, or documentation and tests, with no visible change for consumers |

## Checklist for a release

1. **Decide the version** from the table above, looking at every merged change
   since the last tag.
2. **Check the commit.** The validation run (`validate-workflows`) on the exact
   commit of `main` to be released is green; do not release from a red or
   unchecked commit.
3. **Write the changelog entry** in `CHANGELOG.md`: move the items of
   `[Unreleased]` under `## [x.y.z] - date` in the groups Breaking, Added,
   Changed and Fixed. A change that touches credentials, tokens or permissions
   says so. Check it with
   `python tools/changelog.py check --version x.y.z`; a Breaking entry needs a
   new major version, and a new major version needs a Breaking entry.
4. **Get the approval** of S01 for the release, in the pull request that adds
   the changelog entry.
5. **Tag.** Create `vMAJOR.MINOR.PATCH` on the approved commit, then move
   `vMAJOR` to it:
   ```bash
   git tag -a v1.2.0 -m "v1.2.0" <commit>
   git push origin v1.2.0
   git tag -f v1 <commit> && git push -f origin v1
   ```
6. **Announce.** Create the release page for the tag with the text of
   `python tools/changelog.py notes x.y.z`, and say whether consumers must act.
   The release page of this repository on Gitea is the only destination
   (ADR-0007); nothing is attached to it.
7. **Verify.** One repository pinned to the previous exact tag still runs the
   same code; one repository on the major tag receives the release.

## How consumers pin

| Pin | Receives | Use when |
| --- | --- | --- |
| `@v1.2.0` | nothing new, ever | a pipeline must not change |
| `@v1` | compatible releases only | the default for a project |
| `@main` | everything, unreleased | never; only this repository's own tests |

Reusable workflows are pinned in the `uses:` line of the caller. The scoped
workflows (sync and publish wiki) are delivered from `main` by the instance
and cannot be pinned by a consumer; they fetch their scripts at the major tag
once `v1` exists.

## Undoing a faulty release

1. Move the major tag back to the previous exact tag:
   `git tag -f v1 v1.1.0 && git push -f origin v1`.
2. Fix forward on `main` and release a patch version.
3. Do not delete or move an exact tag; consumers may have pinned it.
