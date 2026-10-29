<!-- translation of OpenGrep.md, source sha256 df7e8514b8f7 -->

> Dette er en oversættelse af [`OpenGrep`](OpenGrep). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](OpenGrep) · **Dansk** · [Bahasa Melayu](OpenGrep-ms)

# Statisk sikkerhedsskanning med OpenGrep

Hvordan en softwareudvikler læser og håndterer resultatet af det scopede workflow
`opengrep.yml`. Det skanner repositoryet med OpenGrep og dets fællesskabsregler,
uden en konto, og viser fundene på pull requesten. Det ændrer ingen fil og har
ingen hemmelighed. Beslutningen er ADR-0015 i dette repository; hvornår et
repository bruger det, står i
[adoptionsreglerne](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/adoption-rules.md#opengrep).

## Intet at tilføje

Workflowet er scoped: instansen kører det i hvert repository i organisationen,
på en pull request, på et push til `main` og manuelt. Et repository tilføjer
ingen fil. OpenGrep v1.33.0 er én kørbar fil (`opengrep_manylinux_x86`), hentet
fra GitHub-udgivelsen og kontrolleret mod en fastlåst sha256; der er ingen `pip`
og ingen konto. Kun Linux x86_64-runnere understøttes. OpenGrep har intet
register og ingen metrik-indstilling. Reglerne er repositoryet
`opengrep/opengrep-rules`, fastlåst til ét commit og hentet med git under
kørslen: mapperne `python`, `bash`, `c`, `csharp`, `yaml`, `generic`,
`dockerfile`, `javascript`, `typescript`, `terraform`, `go` og `java`. Den eneste
udgående vært er `github.com`, og kun filer sporet af git skannes. Ingen
kildetekst forlader runneren.

## Hvad der får kørslen til at fejle

| Alvorlighed | I loggen | Får kørslen til at fejle |
| --- | --- | --- |
| `ERROR` | `::error file=...,line=...::[finding] rule-id: message` | Ja |
| `WARNING` | `::warning file=...,line=...::` | Nej |
| `INFO` | `::notice file=...,line=...::` | Nej |

Jobbets resumé lister op til 50 fund med reglen og stedet. Et repository, hvor
ingen sporet fil skannes, ender grønt og skriver "nothing to scan". En fejl i
selve værktøjet er `[tool]`: hentningen mislykkedes, hashen passede ikke,
reglerne kunne ikke hentes, eller rapporten kan ikke læses; kør det igen, før du
leder efter et fund.

## At gøre et fund tavst

Et falsk positivt fund gøres tavst, hvor det står, og begrundelsen hører hjemme
i pull requesten:

- På linjen: `# nosemgrep: rule-id` (kommentarformen i sproget), med regel-id'et
  præcis som loggen udskriver det (id'et begynder med stien til regelkopien, så
  kopiér det fra CI-loggen, ikke fra en lokal kørsel). OpenGrep beholder
  Semgreps kommentarsyntaks; kontrolleret 2026-10-29: id'et gør kun den regel
  tavs, og `# nosemgrep` uden id gør alle regler på linjen tavse.
- For stier: en `.semgrepignore`-fil i roden af repositoryet, med mønstrene fra
  en `.gitignore`, til genereret kode, medleveret kode (vendored) og fixtures.

Et fund, der er ægte, rettes og gøres ikke tavst. Reglerne er gamle (det sidste
commit er fra januar 2025) og støjer på dokumentation, hvor shell-reglerne
udløses af kodeeksempler i Markdown; forvent at gøre falske positive tavse i
hvert repository.

## Et forsøg på dette repository

En prøvekørsel tog omkring 66 sekunder og skannede 243 filer. Den gav 111 fund:
3 `ERROR` i `tools/` (to `dangerous-subprocess-use-audit` og ét
`use-defused-xml`), 10 `WARNING` og 98 `INFO`, mest shell-regler på
kodeeksempler i Markdown. Fem filer havde parsefejl, som ikke får kørslen til at
fejle. På dette repository ville kontrollen derfor fejle, indtil de tre fund er
rettet eller gjort tavse.

## Marker kontrollen som påkrævet

At markere kontrollen som påkrævet i grenbeskyttelsen er det, der blokerer
sammenfletningen ved et `ERROR`-fund. Det er en indstilling i grenbeskyttelsen,
så repositoryets ejer gør det. Advarsler blokerer aldrig.

## Licensen

OpenGrep er LGPL-2.1. Regel-repositoryet er under LGPL-2.1 med Commons Clause,
som forbyder at sælge softwaren som en tjeneste mod betaling, og dets README
siger, at reglerne er beregnet til forskning, test og benchmarking. Workflowet
henter dem under kørslen og gemmer dem aldrig i et repository. En brug til en
tjeneste, eller en ændring af den licens, kræver en ny beslutning.
