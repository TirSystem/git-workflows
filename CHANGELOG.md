# Changelog

All notable changes to the shared workflows of this repository. The format and
the version rules are those of the release process (`guides/release-process.md`,
ADR-0006): one version for the whole repository, tags `vMAJOR.MINOR.PATCH`
and a moving major tag `vMAJOR`.

Each release lists its changes in these groups, in this order:

- **Breaking**: a renamed or removed workflow, input, secret name or output; a
  raised default tool version or changed default that can turn a green
  consumer red; a changed meaning of pass or fail. A release with a Breaking
  entry has a new major version.
- **Added**: a new optional input, workflow or capability.
- **Changed**: a change with no visible effect for existing callers.
- **Fixed**: a fix.

`python tools/changelog.py check` verifies the file, and
`python tools/changelog.py notes <version>` prints the text of a release page.

## [Unreleased]

## [2.1.0] - 2026-10-14

### Added

- The reusable workflow `code-metrics.yml` (ADR-0010, MIL-010). It counts the
  code files and the lines of code (without comment and blank lines) of a
  repository, reads a Cobertura XML coverage report that the caller uploads as an
  artifact, and commits three SVG badges (code files, lines of code, coverage) to
  a `badges` branch. It needs `contents: write` and no secret; the inputs are
  `working-directory`, `exclude`, `coverage-report`, `coverage-artifact`,
  `coverage-warn`, `coverage-good`, `badges-branch` and `tools-ref`. See
  `guides/code-metrics.md`.

## [2.0.0] - 2026-10-14

### Breaking

- The scoped workflow `publish-wiki.yml` and the `wiki/.publish` marker are
  removed (ADR-0009, MIL-009). A repository publishes its wiki by calling the
  reusable workflow `publish-wiki-pages.yml`; one that still has the marker no
  longer publishes. The seven repositories that used the scoped workflow on
  2026-10-13 have a caller (checked on 2026-10-14). A repository that has
  `wiki/.publish` moves `wiki/` to `docs/wiki/`, copies
  `templates/ci/publish-wiki.yml` of the SQA and QC framework (0.7.0 or later)
  to `.gitea/workflows/publish-wiki.yml` and removes the marker.
- `tools/publish_wiki.py` requires `WIKI_PRUNE` (`true` or `false`) and no longer
  reads a marker; `WIKI_DIR` defaults to `docs/wiki`.

### Changed

- The README, the onboarding, troubleshooting and upgrading guides and the
  wiki pages (English, Danish, Bahasa Malaysia) no longer describe the scoped
  workflow or the marker.
- ADR-0004 is `Superseded by ADR-0009`.
- Callers of `quality-checks.yml`, `quality-checks-cpp.yml`,
  `quality-checks-csharp.yml`, `release.yml` and `publish-wiki-pages.yml` need no
  change; `v1` stays at 1.2.2 and `v2` is the new moving major tag.

## [1.2.2] - 2026-10-13

### Added

- Reusable workflow `publish-wiki-pages.yml` (ADR-0009): publishes the Markdown
  pages of a folder to the wiki of the calling repository. The call is the
  opt-in and no `wiki/.publish` marker is read. Inputs: `wiki_dir` (default
  `docs/wiki`), `prune` (`"true"` deletes wiki pages that are not in the folder,
  default `"false"`) and `tools-ref` (default `v1`); the secret
  `TOKEN_FOR_GITEA_WIKI` is declared by the workflow and passed by the caller,
  with no fallback to another token. A missing folder is a configuration error,
  and an empty folder never deletes pages. A caller template is
  `templates/ci/publish-wiki.yml` of the SQA and QC framework.
- Environment variable `WIKI_PRUNE` of `tools/publish_wiki.py`: when it is set the
  marker is not read. Without it the script behaves as before, so the scoped
  workflow is unchanged.

### Changed

- The scoped workflow `publish-wiki.yml` is deprecated. It still publishes the
  eight repositories that have `wiki/.publish` (checked on 2026-10-13) and is not
  removed in this release; it is removed, with their migration, in a later major
  release.
- The wiki of this repository moves from `wiki/` to `docs/wiki/` and is published
  through the new workflow by `publish-own-wiki.yml`. `tools/build_wiki.py`
  writes to `docs/wiki/`. No change for callers of the other workflows.
- The onboarding, credentials and troubleshooting guides and their wiki pages
  (English, Danish, Bahasa Malaysia) describe the caller, `docs/wiki/`, the
  `prune` and `wiki_dir` inputs and the two new error messages.
- Release type: this is a patch release by the owner's decision (S01, MIL-008),
  although ADR-0006 classes a new workflow as minor. Nothing is removed or
  renamed, so no caller breaks.

## [1.2.1] - 2026-10-13

### Changed

- The C++ and C# guides and their wiki pages say that `clang-tidy` and `dotnet` print
  absolute paths in the workspace of the runner (found in the adoption check,
  MIL-007 task 7).

## [1.2.0] - 2026-10-13

### Added

- Reusable workflow `quality-checks-cpp.yml` (ADR-0008): `clang-format --dry-run
  -Werror` and `clang-tidy` on the tracked C and C++ files, at exact versions
  (inputs `clang-format-version`, `clang-tidy-version`), with the inputs
  `working-directory`, `std`, `compile-commands-dir` and `tools-ref`. The
  repository needs a `.clang-format`; without a `.clang-tidy` the checks
  `clang-diagnostic-*` and `clang-analyzer-*` run, and every clang-tidy finding
  is an error (`--warnings-as-errors=*`).
- Reusable workflow `quality-checks-csharp.yml` (ADR-0008): `dotnet format
  --verify-no-changes` and `dotnet build -warnaserror` on an exact .NET SDK 10
  or later (input `dotnet-sdk-version`, default `10.0.401`), with the inputs
  `working-directory`, `project` and `tools-ref`.

## [1.1.1] - 2026-10-13

### Changed

- Every job has a `timeout-minutes` (5 to 15), so a hung step no longer holds a
  runner for the host's default limit.
- `actions/checkout` is referenced by the exact tag `v4.2.2` instead of the
  moving tag `v4`. No change for callers.
- The framework pin moves from `v0.5.2` to `v0.6.2`, and the two long `run:`
  blocks of this repository's own `sync-milestones.yml` call
  `framework/scripts/ci-publish-milestones.sh`. No change for callers of the
  shared workflows.
- The onboarding guide and its wiki pages (English, Danish, Bahasa Malaysia) say
  that a hyphen in a file name is a space in the page name, and how to link to
  it.

### Fixed

- `publish-wiki` sends a page title with spaces instead of hyphens. Gitea keeps a
  hyphen in a title literal and stored `Home-da` as `Home-da.-.md`, addressed as
  `Home%2Dda`, so links to `Home-da` led to the page list. A new page is now
  stored as `Home-da.md` and addressed as `Home-da`. Pages already created with
  the old title must be deleted by hand (the publisher does not prune them).

## [1.1.0] - 2026-10-11

### Added

- Input `tools-ref` of `quality-checks.yml` (default `v1`): the tag or branch from
  which the workflow fetches its script `tools/quality-checks.sh`.

### Changed

- `quality-checks.yml` runs the script file `tools/quality-checks.sh` instead of
  embedding about 100 lines of shell; the checks, messages and results are the
  same.

## [1.0.1] - 2026-10-11

### Changed

- Sync GitHub mirror metadata: a repository without a GitHub push mirror still
  succeeds, and the log now ends with the line `Skipped`.
- The scoped workflows fetch their scripts at the tag `v1` instead of `main`,
  so a merge to `main` reaches consumers only when it is released.

## [1.0.0] - 2026-10-10

First release. The reusable workflow can be pinned at `v1` or `v1.0.0`. The
scoped workflows are delivered by the instance from `main` and cannot be pinned.

### Added

- Workflow `release.yml`: started by hand with a version, it releases only the
  tip of `main` whose validation run is green and whose changelog entry exists,
  creates the version tag, the release page and the major tag, and does nothing
  but check until `dry_run` is set to `false`.
- Scoped workflow `sync-github-metadata.yml`: copies the description and topics
  of a Gitea repository to its GitHub push mirror on every push to `main`, by
  hand and daily at 03:17 UTC. A repository without a GitHub mirror is skipped
  successfully.
- A credential preflight before any change, and failure messages that name
  their category (`configuration`, `credentials`, `permissions`, `api`).
- Scoped workflow `publish-wiki.yml`: publishes `wiki/` to the repository wiki
  when a repository has opted in with `wiki/.publish`; the word `prune` in that
  file also deletes pages that are not in `wiki/`.
- Reusable workflow `quality-checks.yml`: `ruff`, `mypy --strict`, `shellcheck`
  and `shfmt` on the tracked Python and shell files, with the inputs
  `languages`, `working-directory` and one pinned version per tool.
- Guides for onboarding a repository, workflow credentials, troubleshooting,
  reading quality-check results and releasing, and the same pages on the wiki in
  English, Danish and Bahasa Malaysia.

### Changed

- The scripts of the scoped workflows are files under `tools/`, fetched by a
  checkout of this repository, instead of Python embedded in the YAML.
- Secrets hold the bare token as clear text: `TOKEN_FOR_GITEA`,
  `PAT_FOR_GITHUB` and `TOKEN_FOR_GITEA_WIKI`. They replace the JSON secret
  `CREDENTIALS_FOR_GITHUB`, which is no longer read.
