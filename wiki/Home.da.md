<!-- translation of Home.md, source sha256 eedaeddbea3e -->

> Dette er en oversættelse af [`Home`](Home). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Home) | Dansk | [Bahasa Melayu](Home.ms)

# TirSystem GitHub Actions

En samling af genbrugelige Gitea Actions-workflows til DevOps-professionelle og softwareudviklere, der arbejder på TirSystem-projekter.


## Oversigt

Dette repository er den centrale samling af genbrugelig automatisering til TirSystems repositories. Det primære repository ligger på `git.tirsystem.com` (Gitea) og spejles med push til GitHub.

Det indeholder i øjeblikket Gitea-workflowet [`sync-github-metadata.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/scoped_workflows/sync-github-metadata.yml), som kopierer repositoryets beskrivelse og emner (topics) fra Gitea til GitHub-spejlet ved hvert push til `main`, ved manuel kørsel og dagligt kl. 03:17 UTC.


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
python -m pytest -q tests
```

De samme kontroller kører ved hver pull request og hvert push til `main` gennem [`validate-workflows.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/validate-workflows.yml). De parser alle workflows som YAML, kontrollerer at ingen indlejrer Python, kompilerer scripts i `tools/`, kræver eksplicitte jobtilladelser og tester parsing af credentials, parsing af push-spejlets adresse og synkroniserings- og publiceringsforløbene mod et falsk API.

Efter en ændring af synkroniseringsworkflowet skal du også starte **Sync GitHub mirror metadata** manuelt i Gitea og sammenligne beskrivelsen og emnerne på GitHub-spejlet.
