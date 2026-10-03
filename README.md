# 🚀 TirSystem GitHub Actions

Global, reusable GitHub Actions and workflows for TirSystem projects.

## 📚 Table of Contents

- [Overview](#-overview)
- [Requirements](#-requirements)
- [Setup](#-setup)
- [Run](#-run)
- [Tests](#-tests)
- [License](#-license)
- [Links](#-links)

## 🧭 Overview

This repository is the central collection of global GitHub Actions used across TirSystem repositories. The primary repository lives at `git.tirsystem.com` (Gitea) and is push-mirrored to GitHub.

It currently contains the Gitea workflow [`sync-github-metadata.yml`](.gitea/workflows/sync-github-metadata.yml), which copies the repository description and topics from Gitea to the GitHub mirror on every push to `main`, on manual dispatch, and daily at 03:17 UTC.

## 📋 Requirements

- A Gitea instance with Actions enabled and a runner providing `ubuntu-latest` with `python3`
- A configured GitHub push mirror on the Gitea repository (exactly one)
- Repository secrets:
  - `TOKEN_FOR_GITEA`: Gitea API token (plain string, or JSON with `GITEA_TOKEN`)
  - `CREDENTIALS_FOR_GITHUB`: JSON object containing `GITHUB_PAT`, a GitHub personal access token allowed to edit the mirror repository

## 🛠️ Setup

No dependencies need to be installed; the workflow uses only the Python standard library.

1. Clone the repository:
   ```bash
   git clone ssh://git@git.tirsystem.com:10022/TirSystem/github-action.git
   ```
2. Add the secrets listed under [Requirements](#-requirements) to the repository settings in Gitea.
3. Configure the GitHub push mirror in the repository settings.

## ▶️ Run

Workflows run automatically on push to `main` and on the daily schedule. To run manually, trigger **Sync GitHub mirror metadata** via `workflow_dispatch` from the Actions tab in Gitea.

## 🧪 Tests

There are no automated tests. Verify changes by running the workflow manually and checking the description and topics on the GitHub mirror.

## 📄 License

Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See [LICENSE](LICENSE).

## 🔗 Links

- [Repository](https://git.tirsystem.com/TirSystem/github-action)
- [Documentation](https://git.tirsystem.com/TirSystem/github-action#readme)
- [Issue tracker](https://git.tirsystem.com/TirSystem/github-action/issues)
