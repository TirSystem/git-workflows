<!-- Generated from guides/upgrading.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`guides/upgrading.md`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/guides/upgrading.md). Changes made here are overwritten the next time the wiki is published.

English | [Dansk](Upgrading.da) | [Bahasa Melayu](Upgrading.ms)

# Upgrading to a new version of the shared workflows

How a software engineer adopts a new release of the shared workflows safely:
read the changelog, try the update in one place, and go back if it fails. The
version rules are those of the release process: one version for the whole
repository, tags `vMAJOR.MINOR.PATCH` and a moving major tag `vMAJOR`.

## Which version you follow

| In your `uses:` line | You receive | When to use it |
| --- | --- | --- |
| `@v1.2.0` | nothing new, ever | a pipeline that must not change |
| `@v1` | compatible releases only (minor and patch) | the default for a project |
| `@main` | everything, unreleased | never; only for this repository's own tests |

A breaking release gets a new major version (`v2`), so a pipeline on `@v1`
never receives it until you change the line yourself.

The quality-checks workflows (`quality-checks.yml`, `quality-checks-cpp.yml` and
`quality-checks-csharp.yml`) and the code-metrics workflow (`code-metrics.yml`)
fetch their scripts at their input `tools-ref`, which defaults to the current major tag (`v2`). To pin one completely, call it at an exact tag and set
`tools-ref` to the same tag; otherwise the script follows the major tag.

The scoped workflow **Sync GitHub mirror metadata** is delivered by the
instance and is not in your `uses:` lines; you cannot pin it, but it fetches its
script at the major tag. Wiki publishing is a reusable workflow you call
(`publish-wiki-pages.yml`); the scoped **Publish wiki** workflow and its
`wiki/.publish` marker were removed in 2.0.0, so a repository that still has the
marker no longer publishes until it calls the reusable workflow (see the
onboarding guide).

## Reading a changelog entry

Open `CHANGELOG.md` of `TirSystem/github-action`, or the release page of the tag.
An entry has up to four groups:

| Group | What it means for you |
| --- | --- |
| Breaking | You must act: a name, an input, a secret or a default changed. A release with this group has a new major version |
| Added | Nothing to do; a new optional input, workflow or capability |
| Changed | Nothing to do; no visible effect for existing callers |
| Fixed | Nothing to do; a fix you receive on `@v1` |

An entry that changes credentials, tokens or permissions says so; check your
secrets before you upgrade.

## Trying an update

1. Change the version in **one** repository, on a branch:
   ```yaml
   jobs:
     quality:
       uses: TirSystem/github-action/.gitea/workflows/quality-checks.yml@v2
   ```
2. Open a pull request and read the run. A failing check shows the tool, the
   file and the message (see the guide for reading quality-check results).
3. For a breaking release, follow the upgrade notes of the changelog entry,
   then repeat.
4. When the pull request is green, make the same change in the other
   repositories.

## Going back

1. Change the line back to the previous exact tag, for example `@v1.2.0`, and
   merge it. Exact tags are never deleted or moved, so this always works.
2. Tell the maintainers which release failed and what you saw, so that the
   major tag can be moved back and a fix released.

## When something is unclear

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| The run says the workflow cannot be found | The tag does not exist, or the path is wrong | Check the tag on the release page and the path `.gitea/workflows/quality-checks.yml` |
| A green pipeline turned red after a release on `@v1` | A compatible release should not do this | Pin the previous exact tag and report it as a defect |
| An input is no longer accepted | A breaking release renamed it | Read the Breaking group of the entry |
