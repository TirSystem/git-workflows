<!-- translation of Validate.md, source sha256 d6ec05a17464 -->

> Dette er en oversættelse af [`Validate`](Validate). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Validate) · **Dansk** · [Bahasa Melayu](Validate-ms)

# Validering af workflowfiler og shell-scripts

Sådan læser og håndterer en softwareudvikler resultatet af det scopede workflow
`validate.yml`. Det kontrollerer repositoryets workflowfiler og sporede
shell-scripts mod de kriterier i workflow-tjeklisten (`QC-WF-001`), som et
script kan afgøre, og kører `shellcheck` og `shfmt` på shell-scripts. Det
ændrer ingen fil og har ingen hemmelighed. Beslutningen bag er ADR-0016 i dette
repository; hvornår et repository bruger det, står i
[reglerne for brug](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/adoption-rules.md#validate).

## Intet at tilføje

Workflowet er scoped: instansen kører det i hvert repository i organisationen, på
en pull request, på et push til `main` og manuelt. Et repository tilføjer ingen
fil. Det har `permissions: contents: read` og ingen hemmelighed. Det henter
repositoryet, henter scriptet `tools/validate_repo.py` fra
`TirSystem/git-workflows` ved `v2`, installerer værktøjerne i et virtuelt
miljø med `pip` og kører kontrollerne.

- **Workflowfiler** er `*.yml`- og `*.yaml`-filerne direkte i
  `.gitea/workflows`, `.gitea/scoped_workflows` og `.github/workflows`.
- **Shell-scripts** er de sporede `*.sh`-filer.

Et repository med ingen af delene ender grønt og skriver "nothing to validate".

## Hvad der kontrolleres

Hvert fund angiver filen, linjen og kriteriet:
`::error file=...,line=...::[WF-8] message`.

| Kriterium | Hvad det betyder |
| --- | --- |
| `WF-1` | Filen er ikke gyldig YAML. |
| `WF-2` | Et workflow med samme navn findes i `.gitea/workflows` og i `.github/workflows`. |
| `WF-3` | Workflowet mangler `name`, `on` eller `jobs`. |
| `WF-5` | Et job eller et trin har intet navn, eller et navn bruges to gange i et job. En advarsel. |
| `WF-7` | Hverken workflowet eller jobbet angiver `permissions`. |
| `WF-8` | En action er ikke fastlåst til et commit, et præcist tag eller et bevægeligt major-tag fra organisationen `TirSystem`; en gren afvises. |
| `WF-9` | Workflowet læser `secrets.GITEA_*` eller `secrets.GITHUB_*` (undtagen `GITHUB_TOKEN`), eller lægger en hemmelighed i en `run:`-kommando. |
| `WF-10` | En `run:` interpolerer `inputs.*`, `*.event.*` eller et trins output. |
| `WF-14` | Et job mangler `runs-on` eller `timeout-minutes`. |
| `WF-20` | En `run:`-blok har mere end fem linjer; flyt logikken til en scriptfil. |

De øvrige kriterier i `QC-WF-001` er skøn, en overskriftstekst eller en
værtsadfærd og kontrolleres ikke her. Scriptet læser YAML'ens struktur, ikke
dens betydning; det erstatter ikke `actionlint`.

## Hvad der får kørslen til at fejle

| Fund | I loggen | Får kørslen til at fejle |
| --- | --- | --- |
| Ethvert kriterium undtagen `WF-5` | `::error file=...,line=...::[WF-8] ...` | Ja |
| `WF-5` | `::warning file=...,line=...::[WF-5] ...` | Nej |
| `shellcheck` eller `shfmt -d` finder et problem | værktøjets eget output | Ja |

En fejl i selve værktøjet er `[tool]`: pakkerne kunne ikke installeres (PyPI var
ikke tilgængelig), eller værktøjet startede ikke; kør det igen, før du leder
efter et fund.

## Statusnavnet

Den status, pull requesten og commitet viser, er
`Validate / validate (<event>)`, hvor eventet er `pull_request` eller `push`.
Udgivelsesworkflowet kræver den, som push giver på standardgrenen. Den præcise
tekst, instansen producerer, mangler stadig at blive verificeret (MIL-017,
opgave 1).

## At gøre et fund tavst

Et falsk positivt fund gøres tavst, hvor det står, og begrundelsen hører hjemme i
pull requesten:

- På linjen: `# validate-ignore: WF-8` (flere kriterier adskilles med komma).
- For hele filen: `# validate-ignore-file: WF-5`, hvor som helst i filen.
- Shell: den sædvanlige `# shellcheck disable=SC2086` før kommandoen.
- Formatering af shell: `shfmt` læser repositoryets `.editorconfig`
  (`indent_style`, `indent_size`, `shell_variant`); sæt det der.

Et fund, der er ægte, rettes og gøres ikke tavst.

## Markér kontrollen som påkrævet

At sætte kontrollen som påkrævet i grenbeskyttelsen er det, der blokerer
sammenfletningen ved en fejl. Det er en indstilling i grenbeskyttelsen, så
repositoryets ejer gør det. En advarsel blokerer aldrig.

## De fastlåste værktøjer og deres licenser

Værktøjerne er fastlåst i scriptet og flyttes kun i en udgivelse af dette
repository. Licenserne blev læst 2026-10-29.

| Værktøj | Version | Licens |
| --- | --- | --- |
| PyYAML | 6.0.3 | MIT |
| `shellcheck-py` (bærer binæren) | 0.10.0.1 | MIT |
| ShellCheck | den i `shellcheck-py` | GPL-3.0 |
| `shfmt-py` (bærer binæren) | 3.11.0.2 | MIT |
| shfmt | den i `shfmt-py` | BSD-3-Clause |

Værktøjerne køres som separate programmer, og intet af dem kopieres ind i et
repository, så ShellChecks copyleft berøres ikke.

## Et forsøg på dette repository

En lokal kørsel 2026-10-29 fandt:

- 1 fejl: `WF-20`, `run:` i `publish-wiki-pages.yml` har seks linjer.
- 11 advarsler: `WF-5`, job uden navn.
- `shfmt` 3.14.1 ville ændre `tools/code-metrics.sh` og
  `tools/quality-checks.sh`; den fastlåste 3.11.0.2 aflæses i forsøget på
  instansen og kan formatere anderledes.
- `shellcheck` fandt intet.

På dette repository ville kontrollen derfor fejle, indtil `WF-20`-fejlen er
rettet eller gjort tavs.
