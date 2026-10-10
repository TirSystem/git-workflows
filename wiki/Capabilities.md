<!-- Generated from README.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`README.md`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/README.md). Changes made here are overwritten the next time the wiki is published.

English | [Dansk](Capabilities.da) | [Bahasa Melayu](Capabilities.ms)

## Capabilities

Rows that say Implemented or Guides written exist today. The rest is planned and tracked in the [Project Plan](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/docs/project-plan.md), which also describes each use case.

| Capability | Status |
| --- | --- |
| Synchronize repository metadata (Gitea to GitHub mirror) | Implemented in `.gitea/scoped_workflows/`, with offline tests and a validation workflow |
| Configure and validate workflow credentials | Implemented for the sync workflow: preflight checks both tokens before any change ([guide](Credentials)) |
| Onboard a repository, manage runners, diagnose failures | Guides written ([onboarding](Onboarding), [troubleshooting](Troubleshooting)); scoped delivery to other repositories not yet verified; brief use cases open (MIL-002) |
| Publish a repository wiki from `wiki/` (opt-in, delivered to every organization) | Implemented in `.gitea/scoped_workflows/publish-wiki.yml`, with offline tests; the pilot in a second repository is pending (MIL-006) |
| Shared quality checks (Python and shell) | Implemented as the reusable workflow `.gitea/workflows/quality-checks.yml`, with offline tests and a trial in a second organization; adoption in RepoFoundry is in review ([guide](QualityChecks)) |
| Versioned release and publishing | Release process, changelog and upgrade guide defined; the first release `v1.0.0` and the release workflow are pending (MIL-004) ([guide](Upgrading)) |

### Sync GitHub metadata

Syncs the Gitea repository description and topics to the GitHub push mirror.

#### Cron

Daily at 03:17 UTC (`17 3 * * *`), plus every push to `main` and manual `workflow_dispatch`.

#### Workflow

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
