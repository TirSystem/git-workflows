<!-- translation of Credentials.md, source sha256 2660f2095b78 -->

> Dette er en oversættelse af [`Credentials`](Credentials). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Credentials) | Dansk | [Bahasa Melayu](Credentials.ms)

# Workflow-credentials

Synkroniseringsworkflowet bruger to secrets. Giv hver af dem de mindste rettigheder, der virker, gem den kun som en Gitea-secret, og skift den, når en person med adgang forlader teamet.

| Secret | Indhold | Bruges til |
| --- | --- | --- |
| `TOKEN_FOR_GITEA` | Gitea-tokenet, intet andet | At læse repositoryet (beskrivelse, emner) og dets push-spejle |
| `PAT_FOR_GITHUB` | GitHub-tokenet, intet andet | At ændre beskrivelse og emner på GitHub-spejlet |

## Mindste rettigheder

Disse kommer fra dokumentationen til Gitea og GitHub og fra de API-kald, workflowet foretager. De er **endnu ikke bekræftet med et minimalt token på denne instans**; S05 bør bekræfte dem, når tokens oprettes.

**Gitea-token** (et personal access token for en bruger, ikke en deploy key; deploy keys virker ikke til REST API'et):

- scope `read:repository`
- brugeren skal have lov til at læse repositoryets push-spejle, hvilket Gitea begrænser til repository-administratorer

Kald, der foretages: `GET /repos/{owner}/{repo}` og `GET /repos/{owner}/{repo}/push_mirrors`.

**GitHub-token** (fine-grained personal access token):

- Resource owner: ejeren af spejl-repositoryet
- Repository access: kun spejl-repositoryet
- Repository permission: **Administration: Read and write** (ingen andre tilladelser)
- Angiv en udløbsdato

Kald, der foretages: `GET /repos/{owner}/{repo}`, `PATCH /repos/{owner}/{repo}` (beskrivelse) og `PUT /repos/{owner}/{repo}/topics`.

Format for `PAT_FOR_GITHUB`: kun token-strengen (fx `github_pat_...`) som almindelig tekst. Workflowet tjekker kun, at den ikke er tom; GitHub afviser en forkert værdi (HTTP 401).

## Hvad workflowet kontrollerer, før det ændrer noget

Workflowet kører en forhåndskontrol (preflight) og skriver intet til GitHub, medmindre den består:

1. Begge secrets findes og har den forventede form.
2. Gitea accepterer tokenet, og repositoryet er synligt med det.
3. Højst ét GitHub push-spejl er konfigureret. Hvis der ingen er, slutter kørslen med succes uden at synkronisere, og GitHub-secreten bliver ikke læst.
4. GitHub accepterer tokenet for spejl-repositoryet **og** tokenet melder, at det har administrationsadgang.

Ved succes står der i loggen `Preflight passed: Gitea and GitHub accepted the credentials.` Fejl begynder med en kategori som `[credentials]` eller `[permissions]`; se [troubleshooting.md](Troubleshooting.da). Ingen secret-værdi bliver nogensinde udskrevet.

## Secret til publicering af wiki

Workflowet **Publish wiki** kopierer `wiki/` til Gitea-wikien i et repository, der har meldt sig til med `wiki/.publish` (se [onboarding.md](Onboarding.da)). Det bruger sin egen secret, så synkroniseringstokenet forbliver skrivebeskyttet.

| Secret | Indhold | Bruges til |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_WIKI` | Gitea-tokenet, intet andet | At skrive wikisiderne for de repositories i en organisation, der melder sig til |

- Gem den som en secret i organisationen for hvert repository, der publicerer. Der er ingen reserve til `TOKEN_FOR_GITEA`: et repository, der har meldt sig til og ikke har secreten, fejler med en konfigurationsfejl, og et repository, der ikke har meldt sig til, behøver den ikke.
- Tokenet skal have scope `write:repository`, og dets bruger skal have skriveadgang til repositories. Gitea har intet scope kun til wikien, så opret tokenet til en dedikeret bruger. S05 godkender scopet, og S03 gemmer secreten.
- Kald, der foretages: `GET /repos/{owner}/{repo}`, `GET /repos/{owner}/{repo}/wiki/pages`, `GET`, `POST` og `PATCH /repos/{owner}/{repo}/wiki/...` og, for en side, der ikke længere findes i `wiki/`, `DELETE /repos/{owner}/{repo}/wiki/page/{name}`.
- Wikien skal være aktiveret i repositoryets indstillinger. Workflowet nægter at køre, hvis den ikke er det.
- Sider, der findes i `wiki/`, overskrives altid fra den, så en ændring i Gitea's weboverflade går tabt ved næste publicering. Sider, der kun findes i wikien, fjernes kun, når `wiki/.publish` indeholder ordet `prune`.

## Udskiftning af et token

1. Opret det nye token med de rettigheder, der er nævnt ovenfor.
2. Erstat secret-værdien i repositoryets eller organisationens indstillinger.
3. Kør workflowet manuelt, og vent på `Preflight passed`.
4. Tilbagekald det gamle token.
