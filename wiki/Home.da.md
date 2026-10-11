<!-- translation of Home.md, source sha256 510b243ec5f2 -->

> Dette er en oversættelse af [`Home`](Home). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Home) | Dansk | [Bahasa Melayu](Home.ms)

# TirSystem GitHub Actions

En samling af genbrugelige Gitea Actions-workflows til DevOps-professionelle og softwareudviklere, der arbejder på TirSystem-projekter.


## Oversigt

Dette repository er den centrale samling af genbrugelig automatisering til TirSystems repositories. Det primære repository ligger på `git.tirsystem.com` (Gitea) og spejles med push til GitHub.

Det indeholder fem workflows: synkronisering af metadata til GitHub-spejlet, publicering af wiki, fælles kvalitetskontrol, et udgivelsesworkflow og repositoryets egen validering. De er listet med formål og diagram under [Workflows](#workflows).


## Workflows

Der er fem workflows i dette repository. Et **scoped** workflow leveres af instansen til alle repositories i TirSystem-organisationerne og kræver intet i repositoryet; et **genbrugeligt** workflow kaldes fra et repository med `uses:`; de øvrige kører kun her. Diagrammerne er PlantUML-kildekode og er på engelsk.

| Workflow | Fil | Type | Starter ved | Formål |
| --- | --- | --- | --- | --- |
| Sync GitHub mirror metadata | [`sync-github-metadata.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/scoped_workflows/sync-github-metadata.yml) | Scoped | push til `main`, manuelt, dagligt kl. 03:17 UTC | Kopierer beskrivelsen og emnerne for et Gitea-repository til dets GitHub push-spejl |
| Publish wiki | [`publish-wiki.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/scoped_workflows/publish-wiki.yml) | Scoped, tilmelding med `wiki/.publish` | push til `main`, der ændrer `wiki/**`, manuelt | Publicerer siderne i `wiki/` til repositoryets wiki |
| Quality checks | [`quality-checks.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/quality-checks.yml) | Genbrugeligt (`workflow_call`) | et kald fra et andet repository | Kører ruff, mypy, shellcheck og shfmt på de sporede filer og ændrer intet |
| Release | [`release.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/release.yml) | Kun dette repository | manuelt | Opretter versionstagget, udgivelsessiden og major-tagget efter kontrollerne |
| Validate workflows | [`validate-workflows.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/validate-workflows.yml) | Kun dette repository | pull request, push til `main`, manuelt | Læser hvert workflow som YAML og kører offline-testene |

### Synkronisering af GitHub-metadata

Synkroniserer Gitea-repositoryets beskrivelse og emner til GitHub push-spejlet.

#### Tidsplan (cron)

Dagligt kl. 03:17 UTC (`17 3 * * *`) samt ved hvert push til `main` og manuel `workflow_dispatch`.

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

### Publicering af wiki

Publicerer `wiki/` til repositoryets wiki, kun i et repository, der har tilmeldt sig med `wiki/.publish`. Ordet `prune` i den fil sletter også sider, som ikke findes i `wiki/`.

#### Workflow

```plantuml
@startuml
title Publish wiki/ to the repository wiki

autonumber

actor "Push to main that changes wiki/**,\nor manual trigger" as Trigger
participant "Gitea Actions\npublish-wiki" as Workflow
participant "shared-scripts\n(tools/publish_wiki.py at v1)" as Script
participant "Gitea wiki API" as Wiki

Trigger -> Workflow: Start workflow
activate Workflow
Workflow -> Script: Check out the repository and the script, run it
activate Script

alt wiki/.publish does not exist
  Script --> Workflow: Log that publishing is not enabled and succeed\n(nothing is written)
else wiki/ has no Markdown pages
  Script --> Workflow: Fail with [configuration]\n(an empty wiki/ never deletes pages)
else
  Script -> Script: Read the marker (empty, or the word prune)\nand TOKEN_FOR_GITEA_WIKI
  Script -> Wiki: GET repository (preflight)
  Wiki --> Script: Wiki is enabled, token accepted
  Script -> Wiki: GET pages
  Wiki --> Script: Existing pages
  Script -> Wiki: Create new pages, update changed pages
  opt marker says prune
    Script -> Wiki: Delete pages that are not in wiki/
  end
  Script --> Workflow: Log created, updated and deleted counts
end
deactivate Script
Workflow --> Trigger: Workflow result
deactivate Workflow
@enduml
```

### Kvalitetskontrol

Et genbrugeligt workflow til Python og shell, kaldt med `uses: TirSystem/github-action/.gitea/workflows/quality-checks.yml@v1` (se [vejledningen](QualityChecksPythonShell)).

#### Workflow

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

### Udgivelse

Startes manuelt af en vedligeholder; med `dry_run` `true` (standard) kontrollerer det kun (se [udgivelsesprocessen](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/guides/release-process.md)).

#### Workflow

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

### Validering af workflows

Repositoryets egen validering: de offline-tests, der er en betingelse for hver pull request.

#### Workflow

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


## Krav

- En Gitea-instans med Actions aktiveret og en runner med labelen `ubuntu-latest` og `python3`
- Et konfigureret GitHub push-spejl på Gitea-repositoryet (højst ét; repositories uden spejl springes over uden fejl)
- Repository-secrets:
  - `TOKEN_FOR_GITEA`: Gitea API-token (kun tokenet, ingen JSON)
  - `PAT_FOR_GITHUB`: et GitHub personal access token, der må redigere spejl-repositoryet (kun tokenet, ingen JSON)
  - `TOKEN_FOR_GITEA_WIKI` (kun for repositories, der publicerer en wiki, se [tilslutningsvejledningen](Onboarding.da)): et Gitea-token, der kan skrive til wikien, gemt som en secret i repositoryets organisation; der er ingen reserve til `TOKEN_FOR_GITEA`


## Opsætning

Der skal ikke installeres afhængigheder; workflowet bruger kun Pythons standardbibliotek.

1. Klon repositoryet:
   ```bash
   git clone ssh://git@git.tirsystem.com:10022/TirSystem/github-action.git
   ```
2. Tilføj de secrets, der er nævnt under [Krav](#krav), til repositoryets indstillinger i Gitea.
3. Konfigurer GitHub push-spejlet i repositoryets indstillinger.


## Kørsel

Workflows kører automatisk ved push til `main` og efter den daglige tidsplan. For at køre manuelt skal du starte **Sync GitHub mirror metadata** via `workflow_dispatch` fra fanen Actions i Gitea.


## Tests

Workflow-filerne og scripts i `tools/` valideres af offline-tests, som hverken kræver netværksadgang eller secrets:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r tests/requirements.txt
python -m coverage run -m pytest -q tests
python -m coverage report
```

De samme kontroller kører ved hver pull request og hvert push til `main` gennem [`validate-workflows.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/validate-workflows.yml). De parser alle workflows som YAML, kontrollerer at ingen indlejrer Python, kompilerer scripts i `tools/`, kræver eksplicitte jobtilladelser og tester parsing af credentials, parsing af push-spejlets adresse og synkroniserings- og publiceringsforløbene mod et falsk API. Kørslen fejler, når linje- og forgreningsdækningen af `tools/` er under 95 % (`.coveragerc`).

Efter en ændring af synkroniseringsworkflowet skal du også starte **Sync GitHub mirror metadata** manuelt i Gitea og sammenligne beskrivelsen og emnerne på GitHub-spejlet.
