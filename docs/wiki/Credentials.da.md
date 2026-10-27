<!-- translation of Credentials.md, source sha256 8b4275aaa089 -->

> Dette er en oversættelse af [`Credentials`](Credentials). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Credentials) | Dansk | [Bahasa Melayu](Credentials.ms)

# Workflow-credentials

Synkroniseringsworkflowet bruger to secrets. Giv hver af dem de mindste rettigheder, der virker, gem den kun som en Gitea-secret, og skift den, når en person med adgang forlader teamet.

| Secret | Indhold | Bruges til |
| --- | --- | --- |
| `TOKEN_FOR_GITEA` | Gitea-tokenet, intet andet | At læse repositoryet (beskrivelse, emner) og dets push-spejle |
| `PAT_FOR_GITHUB` | GitHub-tokenet, intet andet | At ændre beskrivelse og emner på GitHub-spejlet |

## Mindste rettigheder

Disse blev kontrolleret den 2026-10-10 mod Gitea-kildekoden (rutedefinitionerne i `routers/api/v1/api.go`, `main`-grenen) og GitHub-siden "Permissions required for fine-grained personal access tokens" for hvert API-kald, workflows foretager. S01 godkendte dem som stedfortræder for S05 (ADR-0002) den 2026-10-10. De er **ikke afprøvet på denne instans med et token, der kun har disse rettigheder**; kontrollerne i slutningen af dette afsnit er måden at gøre det på.

**Gitea-token** (et personal access token for en bruger, ikke en deploy key; deploy keys virker ikke til REST API'et):

- scope `read:repository`: hver `/repos/...`-rute kræver repository-scopet, og kaldene nedenfor læser kun
- brugeren skal være administrator af repositoryet: `push_mirrors`-rutene kræver repository-administration ud over token-scopet

Kald, der foretages: `GET /repos/{owner}/{repo}` og `GET /repos/{owner}/{repo}/push_mirrors`.

**GitHub-token** (fine-grained personal access token):

- Resource owner: ejeren af spejl-repositoryet
- Repository access: kun spejl-repositoryet
- Repository permission: **Administration: Read and write** (ingen andre tilladelser); den kræves til `PATCH /repos/{owner}/{repo}` og `PUT /repos/{owner}/{repo}/topics`. `Metadata: Read` tilføjes automatisk og dækker `GET /repos/{owner}/{repo}`.
- Angiv en udløbsdato

Kald, der foretages: `GET /repos/{owner}/{repo}`, `PATCH /repos/{owner}/{repo}` (beskrivelse) og `PUT /repos/{owner}/{repo}/topics`.

**Gitea-token til wikien** (se "Secret til publicering af wiki" nedenfor): scope `write:repository`, fordi skrivning af en side (`POST`, `PATCH`, `DELETE` under `/repos/{owner}/{repo}/wiki`) kræver repository-scopet med skriveadgang, og brugeren skal have skriveadgang til repositoryets wiki. Oplistning og læsning af sider kræver kun læse-scopet.

**Afprøvning af rettighederne på instansen (valgfrit)**

1. I brugerens Gitea-indstillinger viser det token, der er gemt som `TOKEN_FOR_GITEA`, kun `read:repository`, brugeren er administrator af repositoryet, og en kørsel slutter stadig med `Preflight passed`.
2. GitHub-tokenet viser kun spejl-repositoryet og `Administration: Read and write` (plus den automatiske `Metadata: Read`), og en kørsel slutter med `Preflight passed` og `Synced description and topics`.
3. Et midlertidigt token, der mangler én af disse rettigheder, får kørslen til at fejle med `[permissions]` (eller HTTP 403 for Gitea) og navngive kategorien uden at udskrive tokenet.

Format for `PAT_FOR_GITHUB`: kun token-strengen (fx `github_pat_...`) som almindelig tekst. Workflowet tjekker kun, at den ikke er tom; GitHub afviser en forkert værdi (HTTP 401).

## Hvad workflowet kontrollerer, før det ændrer noget

Workflowet kører en forhåndskontrol (preflight) og skriver intet til GitHub, medmindre den består:

1. Begge secrets findes og har den forventede form.
2. Gitea accepterer tokenet, og repositoryet er synligt med det.
3. Højst ét GitHub push-spejl er konfigureret. Hvis der ingen er, slutter kørslen med succes uden at synkronisere, og GitHub-secreten bliver ikke læst.
4. GitHub accepterer tokenet for spejl-repositoryet **og** tokenet melder, at det har administrationsadgang.

Ved succes står der i loggen `Preflight passed: Gitea and GitHub accepted the credentials.` Fejl begynder med en kategori som `[credentials]` eller `[permissions]`; se [troubleshooting.md](Troubleshooting.da). Ingen secret-værdi bliver nogensinde udskrevet.

## Secret til publicering af wiki

Workflowet **Publish wiki pages** kopierer `docs/wiki/` til Gitea-wikien i et repository, der har en `docs/wiki/`-mappe (se [onboarding.md](Onboarding.da)). Det bruger sin egen secret, så synkroniseringstokenet forbliver skrivebeskyttet.

| Secret | Indhold | Bruges til |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_WIKI` | Gitea-tokenet, intet andet | At skrive wikisiderne for de repositories i en organisation, der har en `docs/wiki/`-mappe |

- Gem den som en secret i organisationen for hvert repository, der publicerer. Der er ingen reserve til `TOKEN_FOR_GITEA`: et repository med en `docs/wiki/`-mappe og uden secreten fejler med en konfigurationsfejl, og et repository uden mappen behøver den ikke.
- Tokenet skal have scope `write:repository`, og dets bruger skal have skriveadgang til repositories. Gitea har intet scope kun til wikien, så opret tokenet til en dedikeret bruger. S05 godkender scopet, og S03 gemmer secreten.
- Kald, der foretages: `GET /repos/{owner}/{repo}`, `GET /repos/{owner}/{repo}/wiki/pages`, `GET`, `POST` og `PATCH /repos/{owner}/{repo}/wiki/...` og, for en side, der ikke længere findes i `docs/wiki/`, `DELETE /repos/{owner}/{repo}/wiki/page/{name}` (kun når sletning er slået til, hvilket det scoped workflow ikke gør).
- Wikien skal være aktiveret i repositoryets indstillinger. Workflowet nægter at køre, hvis den ikke er det.
- Sider, der findes i `docs/wiki/`, overskrives altid fra den, så en ændring i Gitea's weboverflade går tabt ved næste publicering. Sider, der kun findes i wikien, beholdes.

## Udskiftning af et token

1. Opret det nye token med de rettigheder, der er nævnt ovenfor.
2. Erstat secret-værdien i repositoryets eller organisationens indstillinger.
3. Kør workflowet manuelt, og vent på `Preflight passed`.
4. Tilbagekald det gamle token.
