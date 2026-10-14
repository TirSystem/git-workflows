# 🚀 TirSystem GitHub Actions

A collection of reusable Gitea Actions workflows for DevOps professionals and software engineers working on TirSystem projects.

## 📚 Table of Contents

- [Overview](#-overview)
- [Workflows](#-workflows)
- [Requirements](#-requirements)
- [Setup](#-setup)
- [Run](#-run)
- [Tests](#-tests)
- [License](#-license)
- [Links](#-links)

## 🧭 Overview

This repository is the central collection of reusable automation for TirSystem repositories. The primary repository lives at `git.tirsystem.com` (Gitea) and is push-mirrored to GitHub.

It contains ten workflows: metadata sync to the GitHub mirror, wiki publishing (called by each repository), shared quality checks for Python and shell, for C and C++ and for C#, code metrics and coverage badges, a release workflow, the publishing of accepted milestones and the repository's own validation. They are listed with their purpose and a diagram under [Workflows](#-workflows).

## 🔧 Workflows

Ten workflows live in this repository. A **scoped** workflow is delivered by the instance to every repository of the TirSystem organizations and needs nothing in the repository; a **reusable** workflow is called by a repository with `uses:`; the others run only here. The diagrams are PlantUML source.

| Workflow | File | Kind | Starts on | Purpose |
| --- | --- | --- | --- | --- |
| Sync GitHub mirror metadata | [`sync-github-metadata.yml`](.gitea/scoped_workflows/sync-github-metadata.yml) | Scoped | push to `main`, manual, daily 03:17 UTC | Copies the description and topics of a Gitea repository to its GitHub push mirror |
| Publish wiki pages | [`publish-wiki-pages.yml`](.gitea/workflows/publish-wiki-pages.yml) | Reusable (`workflow_call`) | a call from another repository | Publishes the pages in `docs/wiki/` (or the folder named by `wiki_dir`) to the wiki of the calling repository |
| Quality checks | [`quality-checks.yml`](.gitea/workflows/quality-checks.yml) | Reusable (`workflow_call`) | a call from another repository | Runs ruff, mypy, shellcheck and shfmt on the tracked files and changes nothing |
| Quality checks C++ | [`quality-checks-cpp.yml`](.gitea/workflows/quality-checks-cpp.yml) | Reusable (`workflow_call`) | a call from another repository | Runs clang-format and clang-tidy at exact versions on the tracked C and C++ files and changes nothing |
| Quality checks C# | [`quality-checks-csharp.yml`](.gitea/workflows/quality-checks-csharp.yml) | Reusable (`workflow_call`) | a call from another repository | Runs `dotnet format` and `dotnet build` on an exact .NET SDK 10 or later and changes nothing |
| Code metrics | [`code-metrics.yml`](.gitea/workflows/code-metrics.yml) | Reusable (`workflow_call`) | a call from another repository | Counts the code files and the lines of code (without comment and blank lines), reads a Cobertura coverage report and commits three SVG badges to a `badges` branch |
| Publish own wiki | [`publish-own-wiki.yml`](.gitea/workflows/publish-own-wiki.yml) | This repository only | push to `main` that changes `docs/wiki/**`, manual | Calls the reusable Publish wiki pages workflow for the wiki of this repository |
| Release | [`release.yml`](.gitea/workflows/release.yml) | This repository only | manual | Creates the version tag, the release page and the major tag after the checks |
| Publish accepted milestones | [`sync-milestones.yml`](.gitea/workflows/sync-milestones.yml) | This repository only | push to `main` that changes `docs/milestones/**` or `docs/sqa/reviews/**`, manual (dry run by default) | Creates or updates the Gitea milestone and issues of every milestone that is Accepted with a Go review |
| Validate workflows | [`validate-workflows.yml`](.gitea/workflows/validate-workflows.yml) | This repository only | pull request, push to `main`, manual | Parses every workflow and runs the offline tests |

### 🔄 Sync GitHub metadata

Syncs the Gitea repository description and topics to the GitHub push mirror.

#### 🕒 Cron

Daily at 03:17 UTC (`17 3 * * *`), plus every push to `main` and manual `workflow_dispatch`.

#### 🔀 Workflow

```plantuml
@startuml
title Sync Gitea repository description and topics to GitHub

autonumber

actor "Push to main,\nmanual trigger, or schedule" as Trigger
participant "Gitea Actions\nsync-github-metadata" as Workflow
participant "Gitea REST API" as Gitea
participant "GitHub REST API" as GitHub

Trigger -> Workflow: Start workflow
activate Workflow

Workflow -> Workflow: Read and validate secrets
note right
TOKEN_FOR_GITEA
PAT_FOR_GITHUB
end note

alt secret validation failed
  Workflow --> Trigger: workflow failed
end


Workflow -> Gitea: GET /repos/{owner}/{repo}
Gitea --> Workflow: Description and topics

Workflow -> Gitea: GET /repos/{owner}/{repo}/push_mirrors
Gitea --> Workflow: Push mirror response

alt mirrors is not a list
    Workflow --> Trigger: Log a warning and succeed\n(GitHub metadata not synced)
else mirrors is a list with no GitHub mirror
    Workflow --> Trigger: Log that there is nothing to sync and succeed
else mirrors is a list
    Workflow -> Workflow: Find GitHub owner and repo from remote_address

    Workflow -> GitHub: PATCH /repos/{owner}/{repo}\n{description}
    GitHub --> Workflow: Repository updated

    Workflow -> GitHub: PUT /repos/{owner}/{repo}/topics\n{names}
    GitHub --> Workflow: Topics updated

    Workflow --> Trigger: Sync completed
else Gitea API denies access
    Gitea --> Workflow: HTTP 403 Forbidden
    Workflow --> Trigger: Workflow fails
else GitHub API denies access
    GitHub --> Workflow: HTTP error
    Workflow --> Trigger: Workflow fails
end
deactivate Workflow
@enduml
```

### ✅ Quality checks

A reusable workflow for Python and shell, called with `uses: TirSystem/github-action/.gitea/workflows/quality-checks.yml@v1` (see the [guide](guides/quality-checks.md)).

#### 🔀 Workflow

```plantuml
@startuml
title Shared quality checks (reusable workflow)

autonumber

actor "Calling repository\nuses: ...quality-checks.yml@v1" as Caller
participant "Gitea Actions\nquality-checks" as Workflow
participant "PyPI" as PyPI

Caller -> Workflow: workflow_call with languages,\nworking-directory and tool versions
activate Workflow

Workflow -> Workflow: Validate the inputs
alt languages or working-directory is invalid
  Workflow --> Caller: Fail with [configuration]
end

Workflow -> Workflow: Check out the calling repository
Workflow -> PyPI: Install the pinned tools in a virtual environment\n(ruff, mypy, shellcheck-py, shfmt-py as selected)
PyPI --> Workflow: Tools installed

loop for each selected language
  Workflow -> Workflow: List tracked files
  alt no files of that language
    Workflow -> Workflow: Notice: nothing was checked
  else
    Workflow -> Workflow: Run every tool and record PASS or FAIL
  end
end

alt any tool failed
  Workflow --> Caller: Fail and list the failed tools
else
  Workflow --> Caller: All selected checks passed
end
deactivate Workflow
@enduml
```

### 🧱 Quality checks C++

A reusable workflow for C and C++, called with `uses: TirSystem/github-action/.gitea/workflows/quality-checks-cpp.yml@v1` (ADR-0008). The repository needs a `.clang-format`; a `.clang-tidy` and a compile database are optional.

#### 🔀 Workflow

```plantuml
@startuml
title Shared quality checks for C and C++ (reusable workflow)

autonumber

actor "Calling repository\nuses: ...quality-checks-cpp.yml@v1" as Caller
participant "Gitea Actions\nquality-checks-cpp" as Workflow
participant "PyPI" as PyPI

Caller -> Workflow: workflow_call with working-directory, std,\ncompile-commands-dir and tool versions
activate Workflow

Workflow -> Workflow: Check out the caller and the shared script
Workflow -> Workflow: Validate the inputs
alt an input is invalid or a version is not exact
  Workflow --> Caller: Fail with [configuration]
end

Workflow -> PyPI: Install clang-format and clang-tidy at the exact versions
PyPI --> Workflow: Tools installed

alt no C or C++ file is tracked
  Workflow --> Caller: Notice: nothing was checked, pass
else no .clang-format, or compile-commands-dir\nwithout compile_commands.json
  Workflow --> Caller: Fail with [configuration]
else
  Workflow -> Workflow: clang-format --dry-run -Werror on all files
  Workflow -> Workflow: clang-tidy on the C++ files (-std=std)\nand on the C files (or with the compile database)
  alt any tool failed
    Workflow --> Caller: Fail with tool, file and line in the log
  else
    Workflow --> Caller: All selected checks passed
  end
end
deactivate Workflow
@enduml
```

### 🟣 Quality checks C#

A reusable workflow for C#, called with `uses: TirSystem/github-action/.gitea/workflows/quality-checks-csharp.yml@v1` (ADR-0008). It installs the exact .NET SDK given by `dotnet-sdk-version` (10 or later) and needs the network for the package restore.

#### 🔀 Workflow

```plantuml
@startuml
title Shared quality checks for C# (reusable workflow)

autonumber

actor "Calling repository\nuses: ...quality-checks-csharp.yml@v1" as Caller
participant "Gitea Actions\nquality-checks-csharp" as Workflow
participant "dot.net\n(dotnet-install.sh)" as DotNet

Caller -> Workflow: workflow_call with working-directory,\nproject and dotnet-sdk-version
activate Workflow

Workflow -> Workflow: Check out the caller and the shared script
Workflow -> Workflow: Validate the inputs
alt an input is invalid or the SDK is not an exact\nstable version 10 or later
  Workflow --> Caller: Fail with [configuration]
end

Workflow -> DotNet: Install the exact .NET SDK version
DotNet --> Workflow: SDK installed

alt no C# file is tracked
  Workflow --> Caller: Notice: nothing was checked, pass
else no solution or project, or several without the project input
  Workflow --> Caller: Fail with [configuration] that names them
else
  Workflow -> Workflow: dotnet format --verify-no-changes
  Workflow -> Workflow: dotnet build -warnaserror\n(package restore needs the network)
  alt any tool failed
    Workflow --> Caller: Fail with tool, file and line in the log
  else
    Workflow --> Caller: All selected checks passed
  end
end
deactivate Workflow
@enduml
```

### 🏅 Code metrics

A reusable workflow that counts the code files and the lines of code (without comment and blank lines) of a repository and publishes them, with the test coverage, as three SVG badges on a `badges` branch, called with `uses: TirSystem/github-action/.gitea/workflows/code-metrics.yml@v1` (ADR-0010). It needs `contents: write` and runs no test: an earlier job of the caller produces a Cobertura XML coverage report and uploads it as an artifact ([guide](guides/code-metrics.md)).

#### 🔀 Workflow

```plantuml
@startuml
title Code metrics and coverage badges (reusable workflow)

autonumber

actor "Calling repository\nuses: ...code-metrics.yml@v1" as Caller
participant "Gitea Actions\ncode-metrics" as Workflow
participant "Branch badges\nof the caller" as Branch

Caller -> Workflow: workflow_call with working-directory, exclude,\ncoverage-report and thresholds
activate Workflow

Workflow -> Workflow: Check out the caller and the shared scripts
Workflow -> Workflow: Validate the inputs
alt an input is invalid
  Workflow --> Caller: Fail with [configuration]
end

Workflow -> Workflow: Download the coverage artifact (when given)
Workflow -> Workflow: Count code files and lines of code
alt a coverage report is given but missing or malformed
  Workflow --> Caller: Fail with [configuration] that names the file
else
  Workflow -> Workflow: Write code-files.svg, code-lines.svg\nand coverage.svg
end

Workflow -> Branch: Compare with the files of the branch
alt no badge changed
  Workflow --> Caller: Notice: nothing to commit, pass
else
  Workflow -> Branch: One commit with [skip ci]
  Workflow --> Caller: Badges published
end
deactivate Workflow
@enduml
```

### 🏷️ Release

Started by hand by a maintainer; with `dry_run` `true` (the default) it only checks (see the [release process](guides/release-process.md)).

#### 🔀 Workflow

```plantuml
@startuml
title Release this repository

autonumber

actor "Maintainer\n(workflow_dispatch: version, dry_run)" as Trigger
participant "Gitea Actions\nrelease" as Workflow
participant "Gitea REST API" as Gitea

Trigger -> Workflow: Start with version and dry_run
activate Workflow

Workflow -> Workflow: Check the version and read CHANGELOG.md
alt version malformed or no changelog entry
  Workflow --> Trigger: Fail with [validation] or [configuration]
end

Workflow -> Gitea: GET branch main and status of the commit
Gitea --> Workflow: Tip of main and the validation run
alt commit is not the tip of main,\nor the validation run is not green
  Workflow --> Trigger: Fail with [validation]\n(no tag is created)
end

Workflow -> Gitea: GET tags
Gitea --> Workflow: Existing tags
alt tag vMAJOR.MINOR.PATCH exists
  Workflow --> Trigger: Fail with [validation]\n(tags are never moved)
end

alt dry_run is true (default)
  Workflow --> Trigger: Log what would be created and stop
else
  Workflow -> Gitea: POST release (creates the version tag,\nbody is the changelog entry)
  opt this is the highest version of its major
    Workflow -> Gitea: Delete and recreate the major tag vMAJOR
  end
  Workflow --> Trigger: Released
end
deactivate Workflow
@enduml
```

### 📖 Publish wiki pages

A reusable workflow (ADR-0009). A repository calls it from its own workflow, so the call is the opt-in and no marker file is needed. It publishes the Markdown pages of `wiki_dir` (default `docs/wiki`) to the wiki of the calling repository, and deletes pages that are not in the folder only when `prune` is `true`.

```yaml
on:
  push:
    branches: [ main ]
    paths: [ "docs/wiki/**" ]
jobs:
  wiki:
    uses: TirSystem/github-action/.gitea/workflows/publish-wiki-pages.yml@v1
    secrets:
      TOKEN_FOR_GITEA_WIKI: ${{ secrets.TOKEN_FOR_GITEA_WIKI }}
```

#### 🔀 Workflow

```plantuml
@startuml
title Publish docs/wiki to the wiki of the calling repository

autonumber

actor "Calling repository\nuses: ...publish-wiki-pages.yml@v1" as Caller
participant "Gitea Actions\npublish-wiki-pages" as Workflow
participant "shared-scripts\n(tools/publish_wiki.py at tools-ref)" as Script
participant "Gitea wiki API" as Wiki

Caller -> Workflow: Call with wiki_dir, prune and the secret
activate Workflow
Workflow -> Script: Check out the repository and the script, run it
activate Script

alt wiki_dir does not exist, or has no Markdown pages
  Script --> Workflow: Fail with [configuration]\n(an empty folder never deletes pages)
else
  Script -> Script: Read prune and TOKEN_FOR_GITEA_WIKI
  Script -> Wiki: GET repository (preflight)
  Wiki --> Script: Wiki is enabled, token accepted
  Script -> Wiki: GET pages
  Wiki --> Script: Existing pages
  Script -> Wiki: Create new pages, update changed pages
  opt prune is true
    Script -> Wiki: Delete pages that are not in wiki_dir
  end
  Script --> Workflow: Log created, updated and deleted counts
end
deactivate Script
Workflow --> Caller: Workflow result
deactivate Workflow
@enduml
```

### 📖 Publish own wiki

The wiki of this repository is `docs/wiki/`. This workflow calls the reusable workflow above by its local path, with `prune` set to `true` so the wiki always equals the folder and `tools-ref` set to `main` so that the script of the same commit runs. It is the caller that a project copies from the framework's `templates/ci/publish-wiki.yml`.

#### 🔀 Workflow

```plantuml
@startuml
title Publish the wiki of this repository (docs/wiki)

autonumber

actor "Push to main that changes docs/wiki/**,\nor manual trigger" as Trigger
participant "Gitea Actions\npublish-own-wiki" as Caller
participant "Gitea Actions\npublish-wiki-pages\n(called by its local path)" as Workflow
participant "Gitea wiki API" as Wiki

Trigger -> Caller: Start workflow
activate Caller
Caller -> Workflow: Call with wiki_dir docs/wiki, prune true,\ntools-ref main and TOKEN_FOR_GITEA_WIKI
activate Workflow
Workflow -> Wiki: Create, update and delete pages\nso the wiki equals docs/wiki
Wiki --> Workflow: Done
Workflow --> Caller: Workflow result
deactivate Workflow
Caller --> Trigger: Workflow result
deactivate Caller
@enduml
```

### 📌 Publish accepted milestones

Standing authorization to publish: on a push to `main` that changes the milestones or their reviews, every milestone whose latest Version History row is Accepted and whose latest review is a Go is created or updated on Gitea with its tasks as issues. Nothing is closed or deleted. A manual run is a dry run unless `dry_run` is switched off. It uses the secret `TOKEN_FOR_GITEA` and the `--accepted-only` rule of the mounted framework (v0.5.0 or later).

#### 🔀 Workflow

```plantuml
@startuml
title Publish accepted milestones (this repository)

autonumber

actor "Push to main that changes\ndocs/milestones/** or docs/sqa/reviews/**,\nor manual trigger" as Trigger
participant "Gitea Actions\nsync-milestones" as Workflow
participant "framework/scripts/\nsync-project.sh" as Script
participant "Gitea REST API" as Gitea

Trigger -> Workflow: Start workflow
activate Workflow
Workflow -> Workflow: Check out the project and the framework\nsubmodules over HTTPS with TOKEN_FOR_GITEA
Workflow -> Script: --accepted-only (dry run)\nor --accepted-only --apply
activate Script

loop for each docs/milestones/mil-*.md
  alt latest Version History row is not Accepted,\nor the latest review record is not a Go
    Script -> Script: Skip with the reason on stderr
  else
    alt dry run
      Script -> Script: Print the plan, no network call
    else
      Script -> Gitea: Create or update the Milestone\nand one Issue per task row
      Gitea --> Script: Milestone and issue numbers
    end
  end
end

note right of Script
Nothing is closed or deleted.
Each real run edits the issues
of every accepted milestone.
end note
Script --> Workflow: Done, or "nothing to publish"
deactivate Script
Workflow --> Trigger: Workflow result
deactivate Workflow
@enduml
```

### 🧪 Validate workflows

The repository's own validation: the offline tests that gate every pull request.

#### 🔀 Workflow

```plantuml
@startuml
title Validate workflows (this repository's own checks)

autonumber

actor "Pull request,\npush to main, or manual trigger" as Trigger
participant "Gitea Actions\nvalidate-workflows" as Workflow

Trigger -> Workflow: Start workflow
activate Workflow
Workflow -> Workflow: Check out the repository
Workflow -> Workflow: Create a virtual environment and\ninstall tests/requirements.txt
Workflow -> Workflow: Run pytest on tests/ under coverage (offline, no secrets):\nworkflows parse as YAML, no embedded Python,\nscripts compile, wiki pages and translations are current,\nsync, publish and release flows against a fake API

alt a test fails
  Workflow --> Trigger: Workflow fails (the pull request is not ready)
else
  Workflow --> Trigger: Workflow succeeds
end
deactivate Workflow
@enduml
```

## 📋 Requirements

- A Gitea instance with Actions enabled and a runner providing `ubuntu-latest` with `python3`
- A configured GitHub push mirror on the Gitea repository (at most one; repositories without a mirror are skipped successfully)
- Repository secrets:
  - `TOKEN_FOR_GITEA`: Gitea API token (the token only, no JSON)
  - `PAT_FOR_GITHUB`: a GitHub personal access token allowed to edit the mirror repository (the token only, no JSON)
  - `TOKEN_FOR_GITEA_WIKI` (only for repositories that publish a wiki, see the [onboarding guide](guides/onboarding.md)): a Gitea token that can write the wiki, stored as a secret of the repository's organization; there is no fallback to `TOKEN_FOR_GITEA`

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

The workflow files and the scripts in `tools/` are validated by offline tests that need no network access and no secrets:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r tests/requirements.txt
python -m coverage run -m pytest -q tests
python -m coverage report
```

The same checks run on every pull request and push to `main` through [`validate-workflows.yml`](.gitea/workflows/validate-workflows.yml). They parse every workflow as YAML, check that none embeds Python, compile the scripts in `tools/`, require explicit job permissions, and test credential parsing, push mirror address parsing and the sync and publish flows against a fake API. The run fails when the line and branch coverage of `tools/` falls below 95% (`.coveragerc`).

After a change to the sync workflow, also trigger **Sync GitHub mirror metadata** manually in Gitea and compare the description and topics on the GitHub mirror.

## 🟢 Capabilities

Rows that say Implemented or Guides written exist today. The rest is planned and tracked in the [Project Plan](docs/project-plan.md), which also describes each use case.

| Capability | Status |
| --- | --- |
| Synchronize repository metadata (Gitea to GitHub mirror) | Implemented in `.gitea/scoped_workflows/`, with offline tests and a validation workflow |
| Configure and validate workflow credentials | Implemented for the sync workflow: preflight checks both tokens before any change ([guide](guides/credentials.md)) |
| Onboard a repository, manage runners, diagnose failures | Guides written ([onboarding](guides/onboarding.md), [troubleshooting](guides/troubleshooting.md)); scoped delivery to the repositories of all four organizations verified (MIL-002) |
| Publish a repository wiki from `docs/wiki/` through a called workflow | Implemented as the reusable workflow `.gitea/workflows/publish-wiki-pages.yml`, with offline tests; called by every repository that publishes a wiki, and this repository's own wiki is in `docs/wiki/` (MIL-008, MIL-009) |
| Shared quality checks (Python and shell) | Implemented as the reusable workflow `.gitea/workflows/quality-checks.yml`, with offline tests and a trial in a second organization; adopted in RepoFoundry ([guide](guides/quality-checks.md)) |
| Shared quality checks (C and C++, C#) | Implemented as the reusable workflows `.gitea/workflows/quality-checks-cpp.yml` and `.gitea/workflows/quality-checks-csharp.yml` with exact tool versions and offline tests; not yet used in another repository (MIL-007) ([C and C++ guide](guides/quality-checks-cpp.md), [C# guide](guides/quality-checks-csharp.md)) |
| Code metrics and coverage badges | Implemented as the reusable workflow `.gitea/workflows/code-metrics.yml` with a counter, a Cobertura reader, an SVG renderer and offline tests; tried in a throwaway repository, not yet used in a project repository (MIL-010) ([guide](guides/code-metrics.md)) |
| Versioned release and publishing | Release process, changelog and upgrade guide defined; the release workflow exists and `v1.0.0` is released (MIL-004) ([guide](guides/upgrading.md)) |

## 📄 License

Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See [LICENSE](LICENSE).

## 🔗 Links

- [Repository](https://git.tirsystem.com/TirSystem/github-action)
- [Documentation](https://git.tirsystem.com/TirSystem/github-action#readme)
- [Issue tracker](https://git.tirsystem.com/TirSystem/github-action/issues)
