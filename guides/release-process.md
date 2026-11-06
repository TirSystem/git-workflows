# Release process

For the maintainers of this repository: how a change to the shared workflows
is validated, versioned and announced, and how consumers pin a version. The
decisions are in ADR-0006; this guide is the checklist. It is not published
on the wiki.

Steps 5 and 6 are done by the **Release** workflow, a scoped workflow
(`.gitea/scoped_workflows/release.yml`, `tools/release.py`, ADR-0017) that starts
when the changelog of any repository of the organization changes on the default
branch, and by hand to retry; the manual commands below are the fallback. It replaces the workflow `.gitea/workflows/release.yml`, which
released this repository only and is removed.

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
2. **Check the commit.** The validation run (`Validate / validate (push)`,
   ADR-0016) on the exact commit of the default branch to be released is green;
   do not release from a red or unchecked commit. A repository without that
   status cannot be released until the Validate workflow has run there.
3. **Write the changelog entry** in `CHANGELOG.md`: move the items of
   `[Unreleased]` under `## [x.y.z] - date` in the groups Breaking, Added,
   Changed and Fixed. A change that touches credentials, tokens or permissions
   says so. Check it with
   `python tools/changelog.py check --version x.y.z`; a Breaking entry needs a
   new major version, and a new major version needs a Breaking entry.
4. **Get the approval** of S01 for the release, in the pull request that adds
   the changelog entry.
   A pull request that changes the changelog runs **Release** as a check that
   writes nothing and needs no secret: it runs `changelog.py check`, so a
   changelog that cannot be cut into a release fails before the merge. Its
   status is `Release / release (pull_request)`; mark it required in the
   branch protection of the default branch. A repository without
   `CHANGELOG.md` ends green.
5. **Merge the changelog; the Release workflow does the rest.** Merging the
   pull request of step 4 is the release: **Release** starts on the push to the
   default branch that changes `CHANGELOG.md`, with no form. The version is the
   newest numbered entry of `CHANGELOG.md`, so the entry cut in step 3 is what is
   released. If the tag of that entry exists already, there is nothing to release
   and the run ends green, so an edit of the changelog that adds no entry is safe.
   On a push the validation run of step 2 starts at the same time, so the
   workflow waits for it, up to ten minutes (`RELEASE_VALIDATION_WAIT_SECONDS`). It
   refuses (`[validation]`) a status `Validate / validate (push)` that is red, or
   still pending or missing after the wait, and a changelog without a released
   entry; a push whose commit is no longer the tip of the default branch (read
   from the API, not assumed to be `main`) is skipped, because the newer commit
   has its own run. It ends as `[configuration]` and names the secret when
   `TOKEN_FOR_GITEA_RELEASE` is missing. All of this is checked before anything is
   written. It then creates the tag `vMAJOR.MINOR.PATCH` with the release page,
   whose text is the changelog entry (`python tools/changelog.py notes x.y.z`),
   and, from version 1.0.0, moves `vMAJOR` to the commit when this is the highest
   version of its major. The page on Gitea is the only destination (ADR-0007);
   nothing is attached to it. The workflow writes with the organization secret
   `TOKEN_FOR_GITEA_RELEASE` (scope `write:repository`, a dedicated user) and has
   no fallback to the token of the run; see [credentials.md](credentials.md). Runs
   queue in the group `release` and none is cancelled.

   To retry a release that failed, start **Release** by hand on the default branch
   in the Actions tab; it has no form and releases the newest entry.

   By hand, the same steps are:
   ```bash
   git tag -a v1.2.0 -m "v1.2.0" <commit>
   git push origin v1.2.0
   git tag -f v1 <commit> && git push -f origin v1
   ```
   and create the release page with the notes of the changelog entry.
6. **Verify.** One repository pinned to the previous exact tag still runs the
   same code; one repository on the major tag receives the release.

## Changelog formats and the major tag

The workflow reads both heading formats of a changelog:
`## [1.2.0] - 2026-10-21` and `## 0.18.0 (2026-10-28)`; the unreleased heading
is `## Unreleased` or `## [Unreleased]`.

The major tag `vN` exists from version 1.0.0 only: a `0.x` release makes none.
It moves only for the highest version of its major, so a patch of an older
major never moves it. Exact tags are never moved.

## How consumers pin

| Pin | Receives | Use when |
| --- | --- | --- |
| `@v1.2.0` | nothing new, ever | a pipeline must not change |
| `@v1` | compatible releases only | the default for a project |
| `@main` | everything, unreleased | never; only this repository's own tests |

Reusable workflows are pinned in the `uses:` line of the caller. The scoped
workflows (sync, publish wiki, OpenGrep, Validate and Release) are delivered from `main` by the instance
and cannot be pinned by a consumer; they fetch their scripts at the major tag
once `v1` exists.

## Undoing a faulty release

1. Move the major tag back to the previous exact tag:
   `git tag -f v1 v1.1.0 && git push -f origin v1`.
2. Fix forward on `main` and release a patch version.
3. Do not delete or move an exact tag; consumers may have pinned it.
