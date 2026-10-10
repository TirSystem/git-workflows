<!-- translation of Credentials.md, source sha256 57f66acfdc0a -->

> Dette er en oversættelse af [`Credentials`](Credentials). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Credentials) | Dansk | [Bahasa Melayu](Credentials.ms)

# Workflow-credentials

Synkroniseringsworkflowet bruger to secrets. Giv hver af dem de mindste rettigheder, der virker, gem den kun som en Gitea-secret, og skift den, når en person med adgang forlader teamet.

| Secret | Indhold | Bruges til |
| --- | --- | --- |
| `TOKEN_FOR_GITEA` | Et almindeligt token, en JSON-streng eller JSON med `GITEA_TOKEN` | At læse repositoryet (beskrivelse, emner) og dets push-spejle |
| `CREDENTIALS_FOR_GITHUB` | JSON-objekt med et `GITHUB_PAT`, der ikke er tomt | At ændre beskrivelse og emner på GitHub-spejlet |

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

Format for `CREDENTIALS_FOR_GITHUB`:

```json
{"GITHUB_PAT": "<token>"}
```

## Hvad workflowet kontrollerer, før det ændrer noget

Workflowet kører en forhåndskontrol (preflight) og skriver intet til GitHub, medmindre den består:

1. Begge secrets findes og har den forventede form.
2. Gitea accepterer tokenet, og repositoryet er synligt med det.
3. Højst ét GitHub push-spejl er konfigureret. Hvis der ingen er, slutter kørslen med succes uden at synkronisere, og GitHub-secreten bliver ikke læst.
4. GitHub accepterer tokenet for spejl-repositoryet **og** tokenet melder, at det har administrationsadgang.

Ved succes står der i loggen `Preflight passed: Gitea and GitHub accepted the credentials.` Fejl begynder med en kategori som `[credentials]` eller `[permissions]`; se [troubleshooting.md](Troubleshooting.da). Ingen secret-værdi bliver nogensinde udskrevet.

## Secret til publicering af wiki

Workflowet **Publish wiki** (kun dette repository) kopierer `wiki/` til Gitea-wikien, når en ændring af `wiki/` flettes til `main`. Det bruger `TOKEN_FOR_GITEA_WIKI`, hvis den secret findes, og genbruger ellers `TOKEN_FOR_GITEA`.

| Secret | Indhold | Bruges til |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_WIKI` (valgfri) | Et almindeligt token, en JSON-streng eller JSON med `GITEA_TOKEN` | At skrive wikisiderne for dette repository |

- Det token, der bruges, skal have scope `write:repository`, og dets bruger skal have skriveadgang til dette repository. Gitea har intet scope kun til wikien.
- `TOKEN_FOR_GITEA` er beskrevet ovenfor med kun `read:repository`. Hvis det genbruges til wikien, skal dets scope hæves, hvilket også giver metadatasynkroniseringen skriveadgang. En separat `TOKEN_FOR_GITEA_WIKI` til en dedikeret bruger holder synkroniseringstokenet skrivebeskyttet. S05 beslutter hvilket, og S03 gemmer secreten.
- Kald, der foretages: `GET /repos/{owner}/{repo}`, `GET /repos/{owner}/{repo}/wiki/pages`, `GET`, `POST` og `PATCH /repos/{owner}/{repo}/wiki/...` og, for en side, der ikke længere findes i `wiki/`, `DELETE /repos/{owner}/{repo}/wiki/page/{name}`.
- Wikien skal være aktiveret i repositoryets indstillinger. Workflowet nægter at køre, hvis den ikke er det.
- Wikien er altid lig med `wiki/`: sider, der er redigeret eller tilføjet i Gitea's weboverflade, overskrives eller fjernes ved næste publicering.

## Udskiftning af et token

1. Opret det nye token med de rettigheder, der er nævnt ovenfor.
2. Erstat secret-værdien i repositoryets eller organisationens indstillinger.
3. Kør workflowet manuelt, og vent på `Preflight passed`.
4. Tilbagekald det gamle token.
