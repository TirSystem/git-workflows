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

Everything below is what the first release, `1.0.0`, will contain. Until it is
tagged the workflows are delivered from `main` and are not pinned.

### Added

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
