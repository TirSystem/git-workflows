<!-- translation of Onboarding.md, source sha256 8e755cad4918 -->

> Dette er en oversættelse af [`Onboarding`](Onboarding). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Onboarding) | Dansk | [Bahasa Melayu](Onboarding.ms)

# Tilslutning af et repository

Sådan får en DevOps-professionel et TirSystem-repository til at bruge det fælles workflow **Sync GitHub mirror metadata**, og hvilke runners det kræver. Kun dette workflow findes i dag; workflows til kvalitetskontrol og udgivelse er planlagt (se [projektplanen](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/docs/project-plan.md)).

## Hvad er verificeret

| Punkt | Status |
| --- | --- |
| Gitea-version | 1.27.3 |
| `.gitea/scoped_workflows/sync-github-metadata.yml` kører i dette repository | Verificeret: kørsel 16, `workflow_dispatch`, gennemført |
| Samme workflow gælder automatisk for andre repositories | **Ikke verificeret.** Bekræft, hvordan scoped workflows leveres på instansen (admin- eller organisationsindstillinger), før du stoler på det. |

Indtil leveringen er verificeret, tilsluttes et repository ved at kopiere workflowet (se nedenfor).

## Trin

1. **Kontroller forudsætningerne** i repositoryet: Actions er aktiveret, og en runner med labelen `ubuntu-latest` og `python3` er online (se [Runners](#runners)).
2. **Konfigurer ét GitHub push-spejl** i repositoryets indstillinger (Settings, Repository, Mirror settings, Push mirror). Workflowet fejler, hvis der er flere GitHub-spejle. Hvis der ingen er, lykkes det uden at synkronisere noget.
3. **Tilføj de to secrets** i repositoryets (eller organisationens) indstillinger med de scopes, der står i [credentials.md](Credentials.da):
   - `TOKEN_FOR_GITEA`
   - `PAT_FOR_GITHUB` (kun GitHub-tokenet)
4. **Lever workflowet:**
   - *Hvis scoped workflows gælder for repositoryet:* der er intet at kopiere.
   - *Ellers:* kopier `.gitea/scoped_workflows/sync-github-metadata.yml` fra dette repository til `.gitea/workflows/` i mål-repositoryet. Fastlås kopien til en gennemgået version af dette repository, og kopier igen, når den ændres.
5. **Angiv en beskrivelse og emner** på Gitea-repositoryet, så der er noget at synkronisere.
6. **Kør det én gang manuelt:** Actions, **Sync GitHub mirror metadata**, Run workflow. Loggen skal slutte med `Synced description and topics to <owner>/<repo>.`, og GitHub-repositoryet skal vise samme beskrivelse og emner.
7. Hvis det fejler, brug [troubleshooting.md](Troubleshooting.da).

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
