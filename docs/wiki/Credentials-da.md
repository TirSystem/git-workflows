<!-- translation of Credentials.md, source sha256 cd3477f88ddc -->

> Dette er en oversættelse af [`Credentials`](Credentials). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Credentials) · **Dansk** · [Bahasa Melayu](Credentials-ms)

# Workflow-credentials

Synkroniseringsworkflowet bruger to secrets. Giv hver af dem de mindste rettigheder, der virker, gem den kun som en Gitea-secret, og skift den, når en person med adgang forlader teamet.

| Secret | Indhold | Bruges til |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_REPO` | Gitea-tokenet, intet andet | At læse repositoryet (beskrivelse, emner) og dets push-spejle |
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

1. I brugerens Gitea-indstillinger viser det token, der er gemt som `TOKEN_FOR_GITEA_REPO`, kun `read:repository`, brugeren er administrator af repositoryet, og en kørsel slutter stadig med `Preflight passed`.
2. GitHub-tokenet viser kun spejl-repositoryet og `Administration: Read and write` (plus den automatiske `Metadata: Read`), og en kørsel slutter med `Preflight passed` og `Synced description and topics`.
3. Et midlertidigt token, der mangler én af disse rettigheder, får kørslen til at fejle med `[permissions]` (eller HTTP 403 for Gitea) og navngive kategorien uden at udskrive tokenet.

Format for `PAT_FOR_GITHUB`: kun token-strengen (fx `github_pat_...`) som almindelig tekst. Workflowet tjekker kun, at den ikke er tom; GitHub afviser en forkert værdi (HTTP 401).

## Hvad workflowet kontrollerer, før det ændrer noget

Workflowet kører en forhåndskontrol (preflight) og skriver intet til GitHub, medmindre den består:

1. Begge secrets findes og har den forventede form.
2. Gitea accepterer tokenet, og repositoryet er synligt med det.
3. Højst ét GitHub push-spejl er konfigureret. Hvis der ingen er, slutter kørslen med succes uden at synkronisere, og GitHub-secreten bliver ikke læst.
4. GitHub accepterer tokenet for spejl-repositoryet **og** tokenet melder, at det har administrationsadgang.

Ved succes står der i loggen `Preflight passed: Gitea and GitHub accepted the credentials.` Fejl begynder med en kategori som `[credentials]` eller `[permissions]`; se [troubleshooting.md](Troubleshooting-da). Ingen secret-værdi bliver nogensinde udskrevet.

## Secret til publicering af wiki

Workflowet **Publish wiki pages** kopierer `docs/wiki/` til Gitea-wikien i et repository, der har en `docs/wiki/`-mappe (se [onboarding.md](Onboarding-da)). Det bruger sin egen secret, så synkroniseringstokenet forbliver skrivebeskyttet.

| Secret | Indhold | Bruges til |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_WIKI` | Gitea-tokenet, intet andet | At skrive wikisiderne for de repositories i en organisation, der har en `docs/wiki/`-mappe |

- Gem den som en secret i organisationen for hvert repository, der publicerer. Der er ingen reserve til `TOKEN_FOR_GITEA_REPO`: et repository med en `docs/wiki/`-mappe og uden secreten fejler med en konfigurationsfejl, og et repository uden mappen behøver den ikke.
- Tokenet skal have scope `write:repository`, og dets bruger skal have skriveadgang til repositories. Gitea har intet scope kun til wikien, så opret tokenet til en dedikeret bruger. S05 godkender scopet, og S03 gemmer secreten.
- Kald, der foretages: `GET /repos/{owner}/{repo}`, `GET /repos/{owner}/{repo}/wiki/pages`, `GET`, `POST` og `PATCH /repos/{owner}/{repo}/wiki/...` og, for en side, der ikke længere findes i `docs/wiki/`, `DELETE /repos/{owner}/{repo}/wiki/page/{name}` (kun når sletning er slået til, hvilket det scoped workflow ikke gør).
- Wikien skal være aktiveret i repositoryets indstillinger. Workflowet nægter at køre, hvis den ikke er det.
- Sider, der findes i `docs/wiki/`, overskrives altid fra den, så en ændring i Gitea's weboverflade går tabt ved næste publicering. Sider, der kun findes i wikien, beholdes.

## Secret til udgivelse

Det scoped workflow **Release** (ADR-0017) opretter versionstagget, udgivelsessiden og, fra version 1.0.0, major-tagget i ethvert repository i en organisation. Det startes manuelt (se [release-process.md](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/release-process.md)). Det skriver med sin egen secret, så intet andet token behøver at skrive tags.

| Secret | Indhold | Bruges til |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_RELEASE` | Gitea-tokenet, intet andet | At oprette tagget og udgivelsessiden og flytte major-tagget i det repository, workflowet startes i |

- Gem den som en secret i organisationen for hvert repository, der udgives. Der er ingen reserve til kørslens token, til `TOKEN_FOR_GITEA_REPO` eller til nogen anden secret: en kørsel uden den slutter som `[configuration]` og nævner secreten, også som tørkørsel.
- Tokenet skal have scope `write:repository`, og dets bruger skal have skriveadgang til repositories. Gitea har intet scope kun til tags, så opret tokenet til en dedikeret bruger. S05 godkender scopet, og S03 gemmer secreten.
- Workflowet læser den i miljøet i det ene trin, der kører scriptet; den står aldrig på en kommandolinje eller i loggen. Selve workflowet har `permissions: contents: read`.
- Kald, der foretages (en test sammenligner listen med scriptet):
  - `GET /repos/{owner}/{repo}` (standardbranchen)
  - `GET /repos/{owner}/{repo}/branches/{branch}` (spidsen af standardbranchen)
  - `GET /repos/{owner}/{repo}/commits/{sha}/status` (statussen `Validate / validate (push)`)
  - `GET /repos/{owner}/{repo}/tags`
  - `POST /repos/{owner}/{repo}/releases` (udgivelsessiden; Gitea opretter versionstagget med den)
  - `POST /repos/{owner}/{repo}/tags` (major-tagget `vN`)
  - `DELETE /repos/{owner}/{repo}/tags/{tag}` (major-tagget `vN`, før det oprettes igen ved den nye commit)

  En tørkørsel foretager kun `GET`-kaldene.
- En secret, der kan skrive tags og udgivelsessider i alle repositories i en organisation, er et værdifuldt mål (ADR-0017). Det begrænses af den dedikerede bruger og af, at secreten gemmes pr. organisation.
- **Endnu ikke verificeret på instansen:** om tokenet opfører sig, som beslutningen antager, i en scoped kørsel (det kan oprette et tag og en side og flytte et tag), er første opgave i MIL-018. Indtil det er registreret, er scopet og listen over kald ovenfor beslutningen, ikke et testet resultat.

## Secrets til publicering af milepæle

Det scopede workflow **Publicering af accepterede milepæle** (ADR-0018, [vejledning](SyncMilestones-da))
publicerer de accepterede milepæle i et repository, der har en `docs/milestones/`-mappe, som Gitea-milepæle og
-issues. Det bruger to organisations-secrets og læser intet andet navn.

| Secret | Indhold | Bruges til |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_REPO` | Gitea-tokenet og intet andet | At læse repositories: projektet og det private framework, hentet over HTTPS |
| `TOKEN_FOR_GITEA_ISSUES` | Gitea-tokenet og intet andet | At publicere: oprette og opdatere issues og milepæle, kun scope issues |

- Gem begge som secrets i den organisation, hvor hvert publicerende repository ligger. Der er ingen fallback til et
  ældre navn (`GITEA_TOKEN`, `SYNC_TOKEN`): en kørsel uden en af dem slutter som `[configuration]` og nævner den, og et
  repository uden `docs/milestones/` har brug for ingen af dem.
- Workflowet læser dem i miljøet i de trin, der har brug for dem; de står aldrig på en kommandolinje eller i loggen.
  Selve workflowet har `permissions: contents: read`.
- En kopi af `sync-milestones.yml` i et repositorys `.gitea/workflows/` fjernes: den kører ved siden af det scopede
  workflow og publicerer to gange.
- Et token, der publicerer issues i alle repositories i en organisation, kan nås af alle repositorys workflows i den
  organisation (ADR-0018).
- **Endnu ikke verificeret på instansen:** om en scoped kørsel kan læse begge secrets og hente det private framework,
  og om `framework/qc` er nødvendigt, er første opgave i MIL-019. Indtil det er registreret, er dette beslutningen,
  ikke et testet resultat.

## Udskiftning af et token

1. Opret det nye token med de rettigheder, der er nævnt ovenfor.
2. Erstat secret-værdien i repositoryets eller organisationens indstillinger.
3. Kør workflowet manuelt, og vent på `Preflight passed`.
4. Tilbagekald det gamle token.
