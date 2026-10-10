<!-- translation of Troubleshooting.md, source sha256 e8a34cbe7e93 -->

> Dette er en oversættelse af [`Troubleshooting`](Troubleshooting). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Troubleshooting) | Dansk | [Bahasa Melayu](Troubleshooting.ms)

# Fejlfinding af en mislykket kørsel

Åbn kørslen i Gitea (Actions) og læs de sidste linjer i det trin, der fejler. Hver fejl fra synkroniseringsscriptet skrives som

```
ERROR: [<category>] <message>
```

Kategorien fortæller, hvor du skal kigge. En fejl uden for scriptet (jobbet starter aldrig eller stopper før trinnet) er et **runner**-problem.

| Kategori | Betydning | Første ting at kontrollere |
| --- | --- | --- |
| `configuration` | En secret eller en repository-indstilling mangler eller er forkert udformet | Secretnavne og format, opsætning af push-spejl |
| `credentials` | En tjeneste afviste tokenet (HTTP 401) | Token er udløbet, tilbagekaldt eller forkert indtastet |
| `permissions` | Tokenet er gyldigt, men har ikke tilladelse (HTTP 403, eller ingen GitHub-administrationsadgang) | Token-scopes og repository-adgang |
| `api` | En anden HTTP-fejl, eller tjenesten kunne ikke nås | Tjenestens status, runnerens netværk |
| runner | Ingen `ERROR:`-linje; kørslen venter, eller jobbet fejler før scriptet | Runner online, label, værktøjer |

## Meddelelser og løsninger

| Meddelelse (begyndelsen) | Kategori | Årsag og løsning |
| --- | --- | --- |
| `PAT_FOR_GITHUB is missing or empty.` | configuration | Tilføj secreten |
| `TOKEN_FOR_GITEA is missing or empty.` | configuration | Tilføj secreten |
| `Could not determine the Gitea source repository.` | configuration | Kørslen har intet repositorynavn; meld det som en defekt |
| `Expected at most one GitHub push mirror ... found N` | configuration | Behold ét GitHub push-spejl |
| `TOKEN_FOR_GITEA_WIKI is missing or empty.` | configuration | Kun wiki-publicering: repositoryet har meldt sig til med `wiki/.publish`, men dets organisation har ingen sådan secret; gem den (se [credentials.md](Credentials.da)) |
| `wiki/.publish may only be empty or contain the word 'prune'.` | configuration | Kun wiki-publicering: lad markøren være tom, eller skriv kun ordet `prune` i den |
| `... HTTP 403 ...` ved publicering af wikien | permissions | Kun wiki-publicering: tokenet skal have `write:repository` og skriveadgang til dette repository |
| `The wiki is not enabled on <repo>` | configuration | Kun wiki-publicering: aktivér wikien i repositoryets indstillinger |
| `The wiki source directory ... has no Markdown pages` | configuration | Kun wiki-publicering: `wiki/` er tom eller mangler; intet blev ændret |
| `Could not determine the GitHub owner and repository ...` | configuration | Spejlets adresse skal se ud som `https://github.com/<owner>/<repo>.git` |
| `Gitea API request failed with HTTP 401` | credentials | Opret et nyt Gitea-token, og opdatér `TOKEN_FOR_GITEA` |
| `GitHub API request failed with HTTP 401` | credentials | Opret et nyt GitHub-token, og opdatér `PAT_FOR_GITHUB`; værdien skal kun være tokenet (intet navn, ingen anførselstegn eller JSON) |
| `... HTTP 403 ...` (Gitea) | permissions | Tokenet skal have `read:repository`, og dets bruger skal være administrator af repositoryet |
| `... HTTP 403 ...` (GitHub) | permissions | Tokenet skal have Administration read and write på spejl-repositoryet |
| `The GitHub token cannot administer <repo>` | permissions | Som ovenfor; tokenet kan læse repositoryet, men ikke redigere det |
| `... HTTP 404 ...` | configuration | Repositoryet blev ikke fundet, eller tokenet kan ikke se det; kontroller spejlets adresse og tokenets adgang til repositoryet |
| `... HTTP 5xx ...` | api | Problem hos tjenesten; kør igen senere |
| `... API is unreachable ...` | api | Netværks-, DNS- eller proxyproblem på runneren |

## Ikke en fejl

`No GitHub push mirror configured for <repo>; nothing to sync.` Kørslen lykkes. Ikke alle Gitea-repositories har et GitHub-spejl, så det er forventet for dem. Hvis repositoryet skal have et, så tilføj det i repositoryets indstillinger.

`WARNING: Gitea returned an invalid push mirror list; GitHub metadata was not synced.` Kørslen lykkes, men intet blev synkroniseret. Kontroller, at Gitea-versionen understøtter push mirror-API'et, og kør igen.

`No wiki/.publish marker in <owner>/<repo>; wiki publishing is not enabled for this repository.` Kørslen af Publish wiki lykkes og skriver intet. Repositoryet har ikke meldt sig til; tilføj `wiki/.publish`, hvis det skal publicere.

`<n> page(s) are in the wiki but not in wiki/ and were kept; put the word 'prune' in wiki/.publish to delete them.` Kørslen lykkes. Sider, der kun findes i wikien, lades i fred, medmindre markøren indeholder `prune`.

## Runner-problemer

Se afsnittet [Runners](Onboarding.da#runners). Kort sagt: hvis kørslen bliver stående som `waiting`, har ingen online runner labelen; hvis jobbet fejler før scriptet, mangler runner-imaget et værktøj.

## Ny kørsel

Brug **Run workflow** (`workflow_dispatch`), når årsagen er rettet. Synkroniseringen kan trygt gentages: den overskriver GitHub-beskrivelsen og -emnerne med værdierne fra Gitea.
