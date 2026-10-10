<!-- Generated from README.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`README.md`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/README.md). Changes made here are overwritten the next time the wiki is published.

English | [Dansk](Home.da) | [Bahasa Melayu](Home.ms)

# TirSystem GitHub Actions

A collection of reusable Gitea Actions workflows for DevOps professionals and software engineers working on TirSystem projects.


## Overview

This repository is the central collection of reusable automation for TirSystem repositories. The primary repository lives at `git.tirsystem.com` (Gitea) and is push-mirrored to GitHub.

It currently contains the Gitea workflow [`sync-github-metadata.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/scoped_workflows/sync-github-metadata.yml), which copies the repository description and topics from Gitea to the GitHub mirror on every push to `main`, on manual dispatch, and daily at 03:17 UTC.


## Requirements

- A Gitea instance with Actions enabled and a runner providing `ubuntu-latest` with `python3`
- A configured GitHub push mirror on the Gitea repository (at most one; repositories without a mirror are skipped successfully)
- Repository secrets:
  - `TOKEN_FOR_GITEA`: Gitea API token (plain string, or JSON with `GITEA_TOKEN`)
  - `CREDENTIALS_FOR_GITHUB`: JSON object containing `GITHUB_PAT`, a GitHub personal access token allowed to edit the mirror repository
  - `TOKEN_FOR_GITEA_WIKI` (optional, only in this repository, for the **Publish wiki** workflow): Gitea token that can write the repository wiki; when it is absent, `TOKEN_FOR_GITEA` is used and needs write access


## Setup

No dependencies need to be installed; the workflow uses only the Python standard library.

1. Clone the repository:
   ```bash
   git clone ssh://git@git.tirsystem.com:10022/TirSystem/github-action.git
   ```
2. Add the secrets listed under [Requirements](#requirements) to the repository settings in Gitea.
3. Configure the GitHub push mirror in the repository settings.


## Run

Workflows run automatically on push to `main` and on the daily schedule. To run manually, trigger **Sync GitHub mirror metadata** via `workflow_dispatch` from the Actions tab in Gitea.


## Tests

The workflow files and the Python embedded in them are validated by offline tests that need no network access and no secrets:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r tests/requirements.txt
python -m pytest -q tests
```

The same checks run on every pull request and push to `main` through [`validate-workflows.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/validate-workflows.yml). They parse every workflow as YAML, compile the embedded Python, require explicit job permissions, and test credential parsing, push mirror address parsing and the sync flow against a fake API.

After a change to the sync workflow, also trigger **Sync GitHub mirror metadata** manually in Gitea and compare the description and topics on the GitHub mirror.
