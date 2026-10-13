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
