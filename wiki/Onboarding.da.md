<!-- translation of Onboarding.md, source sha256 1d431898754e -->

> Dette er en oversættelse af [`Onboarding`](Onboarding). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Onboarding) | Dansk | [Bahasa Melayu](Onboarding.ms)

# Tilslutning af et repository

Sådan får en DevOps-professionel et TirSystem-repository til at bruge det fælles workflow **Sync GitHub mirror metadata**, og hvilke runners det kræver. Kun dette workflow findes i dag; workflows til kvalitetskontrol og udgivelse er planlagt (se [projektplanen](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/docs/project-plan.md)).

## Hvad er verificeret

| Punkt | Status |
| --- | --- |
| Gitea-version | 1.27.3 |
| `.gitea/scoped_workflows/sync-github-metadata.yml` kører i dette repository | Verificeret: kørsel 16, `workflow_dispatch`, gennemført |
| Samme workflow gælder automatisk for andre repositories | Verificeret 2026-10-10: det kørte, uden en kopi i repositoryet, i repositories i `TirSystem`, `TirSystem-BashScript`, `vl-staal` og `Tirsvad-Udemy-100-days-of-code` (fx `TirSystem/sqa-qc-checklists` og `TirSystem-BashScript/RepoFoundry`). Scriptet, det kørte, ændrede sig, når dette repositorys script ændrede sig. |

Leveringen er automatisk, så et repository behøver ingen kopi af workflowet. Secrets deles ikke mellem organisationer: hver organisation skal have sine egne (trin 3).

## Trin

1. **Kontroller forudsætningerne** i repositoryet: Actions er aktiveret, og en runner med labelen `ubuntu-latest` og `python3` er online (se [Runners](#runners)).
2. **Konfigurer ét GitHub push-spejl** i repositoryets indstillinger (Settings, Repository, Mirror settings, Push mirror). Workflowet fejler, hvis der er flere GitHub-spejle. Hvis der ingen er, lykkes det uden at synkronisere noget.
3. **Tilføj de to secrets** i repositoryets (eller organisationens) indstillinger med de scopes, der står i [credentials.md](Credentials.da). Workflowet kører i alle organisationens repositories, så gem secrets én gang pr. organisation; et repository i en anden organisation kan ikke se dem:
   - `TOKEN_FOR_GITEA`
   - `PAT_FOR_GITHUB` (kun GitHub-tokenet)
4. **Lever workflowet:** scoped workflows gælder for alle repositories på denne instans, så der er intet at kopiere. Kun hvor scoped levering ikke er sat op, kopieres `.gitea/scoped_workflows/sync-github-metadata.yml` fra dette repository til `.gitea/workflows/` i mål-repositoryet; fastlås kopien til en gennemgået version, og kopier igen, når den ændres.
5. **Angiv en beskrivelse og emner** på Gitea-repositoryet, så der er noget at synkronisere.
6. **Kør det én gang manuelt:** Actions, **Sync GitHub mirror metadata**, Run workflow. Loggen skal slutte med `Synced description and topics to <owner>/<repo>.`, og GitHub-repositoryet skal vise samme beskrivelse og emner.
7. Hvis det fejler, brug [troubleshooting.md](Troubleshooting.da).

## Publicér en wiki (valgfrit)

Workflowet **Publish wiki** kopierer Markdown-siderne i `wiki/` til repositoryets wiki, når en ændring af `wiki/` flettes til `main`. Det leveres som synkroniseringsworkflowet, men skriver kun, hvor et repository har meldt sig til.

1. Aktivér wikien i repositoryets indstillinger.
2. Tilføj Markdown-sider til `wiki/`. Filnavnet er sidens navn: `Home.md` er forsiden.
3. Tilføj markøren `wiki/.publish`. Lad den være tom for kun at oprette og opdatere sider. Skriv det ene ord `prune` i den for også at slette wiki-sider, der ikke findes i `wiki/`, så wikien altid er lig med mappen.
4. Gem `TOKEN_FOR_GITEA_WIKI` som en secret i repositoryets organisation med det scope, der står i [credentials.md](Credentials.da).
5. Flet ændringen til `main`. Loggen skal slutte med `Published <n> page(s) to the wiki of <owner>/<repo>`.

Et repository uden `wiki/.publish` springes over med linjen `No wiki/.publish marker in <owner>/<repo>`: intet bliver skrevet, og der skal ingen secret til.

## Runners

| Punkt | Værdi |
| --- | --- |
| Label, som workflowet bruger | `ubuntu-latest` |
| Labels, som runneren på denne instans tilbyder | `ubuntu-latest`, `ubuntu-24.04`, `ubuntu-22.04` |
| Værktøjer, workflowet skal bruge | `python3` (kun standardbiblioteket), udgående HTTPS til Gitea API og `api.github.com` |
| Kræves af `actions/checkout` (bruges af valideringsworkflowet) | `git` og Node.js, normalt i runner-imaget |

**Kontroller, at en passende runner er online** (kræver tilladelse til at se runners):

```bash
curl -s -H "Authorization: token $GITEA_TOKEN" \
  https://git.tirsystem.com/api/v1/repos/<owner>/<repo>/actions/runners
```

For runners, der deles af hele instansen, bruger en administrator `/api/v1/admin/actions/runners`. På skrivetidspunktet er lister for repository og organisation tomme, og én runner på instansniveau (`36cd20104923`) er `online`.

**Offline eller inkompatibel runner**

| Symptom | Sandsynlig årsag | Handling |
| --- | --- | --- |
| Kørslen bliver stående som `waiting` | Ingen online runner har den label, der står i `runs-on` | Start runneren, eller registrer én med labelen |
| Jobbet fejler i starten med en manglende kommando | Runner-imaget mangler `python3`, `git` eller Node.js | Brug et image, der har dem |
| Jobbet kan ikke nå API'et | Runneren har ingen udgående HTTPS | Ret runnerens netværks- eller proxyindstillinger |
