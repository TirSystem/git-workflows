<!-- translation of QualityChecksCpp.md, source sha256 7de98132031b -->

> Dette er en oversættelse af [`QualityChecksCpp`](QualityChecksCpp). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](QualityChecksCpp) | Dansk | [Bahasa Melayu](QualityChecksCpp.ms)

# Aflæsning af resultater fra kvalitetskontrol af C og C++

Sådan kalder en softwareudvikler den fælles kvalitetskontrol af C og C++, aflæser en mislykket kørsel og får den til at bestå. Workflowet formatkontrollerer og analyserer statisk repositoryets C- og C++-filer med clang-værktøjer i præcise versioner, ændrer ingen fil og kræver ingen secret. Dets kontrakt er ADR-0008 i dette repository.

## Kald af workflowet

```yaml
name: Quality C++

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  quality:
    permissions:
      contents: read
    uses: TirSystem/git-workflows/.gitea/workflows/quality-checks-cpp.yml@v1
    with:
      std: c++20
```

| Input | Standard | Betydning |
| --- | --- | --- |
| `working-directory` | `.` | Mappe, relativt til repositoryets rod, hvis filer kontrolleres |
| `std` | `c++20` | C++-standard, som clang-tidy får, når der ikke er en compile-database, for eksempel `c++17` eller `gnu++20` |
| `compile-commands-dir` | tom | Mappe, relativt til repositoryets rod, med en `compile_commands.json`, som din pipeline har bygget før kaldet; når den er sat, bruger clang-tidy den og ignorerer `std` |
| `clang-format-version` | `23.1.3` | Præcis version af pakken clang-format |
| `clang-tidy-version` | `22.1.8` | Præcis version af pakken clang-tidy |
| `tools-ref` | `v2` | Tag eller gren i `TirSystem/git-workflows`, hvorfra scriptet `tools/quality-checks-cpp.sh` hentes |

Henvis til workflowet ved major-tagget (`@v1`) eller et præcist tag, aldrig ved `main`. Et kald ved et præcist tag er kun fuldt fastlåst, når `tools-ref` angiver samme tag. Se opgraderingsvejledningen. Værktøjsversionerne er præcise: en nyere version af et værktøj er en ny udgivelse af dette repository, ikke en stille ændring.

## Hvad repositoryet skal have

- En `.clang-format` i arbejdsmappen eller i en mappe over den, op til repositoryets rod. Uden en fejler kørslen med `[configuration]`, og intet værktøj kører.
- Eventuelt en `.clang-tidy` med projektets kontroller (for eksempel C++ Core Guidelines). Uden en kører workflowet compilerdiagnostik og den statiske analysator (`clang-diagnostic-*` og `clang-analyzer-*`), fordi clang-tidy selv ikke aktiverer nogen kontrol uden konfiguration.
- For præcise statiske kontroller en compile-database: byg den først (for eksempel `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`) og angiv `compile-commands-dir: build`. Workflowet bygger ikke dit projekt.

## Hvad der kontrolleres

| Filer | Værktøj | Hvad det melder |
| --- | --- | --- |
| sporede `*.c`, `*.cc`, `*.cpp`, `*.cxx`, `*.h`, `*.hh`, `*.hpp`, `*.hxx` | `clang-format --dry-run -Werror` | formatering, der afviger fra `.clang-format` |
| de samme filer | `clang-tidy` | fund fra kontrollerne i `.clang-tidy` (eller fra `clang-diagnostic-*` og `clang-analyzer-*` uden en); `*.c`-filer kontrolleres som C17, de øvrige filer som C++-standarden i `std`; hvert fund er en fejl (`--warnings-as-errors=*`), så en advarsel får kørslen til at fejle |

Usporede filer kontrolleres ikke. Et repository uden disse filer består med en bemærkning. Der er ingen `cppcheck`: kun en gammel version findes som pakke, og gamle værktøjer køres ikke (ADR-0008).

## Aflæsning af en kørsel

1. Åbn statuskontrollen på pull requesten og derefter jobbet `quality-checks-cpp`.
2. Hvert værktøj har sin egen logggruppe. Alle værktøjer kører, selv om et tidligere fejlede, så én kørsel viser alle fund.
3. Et værktøj ender med `PASS <værktøj>` eller `FAIL <værktøj>`; sidste linje i en mislykket kørsel nævner dem: `Quality checks failed: clang-format`.
4. Et fund skrives af værktøjet selv som `path:line:column: message`. `clang-format` skriver stier relative til `working-directory`; `clang-tidy` skriver absolutte stier i runnerens arbejdsområde (`/workspace/<owner>/<repo>/main.cpp:5:18`).

## Typiske fejl og rettelser

| Værktøj | Hvad loggen viser | Rettelse |
| --- | --- | --- |
| `clang-format` | `code should be clang-formatted [-Wclang-format-violations]` | Kør `clang-format -i <fil>` med samme version, og commit |
| `clang-tidy` | `warning: ... [modernize-use-nullptr]` | Ret koden, eller slå kontrollen fra i `.clang-tidy` med en begrundelse |
| `clang-tidy` | `error: 'x.h' file not found` | Byg compile-databasen og sæt `compile-commands-dir`, eller tilføj include-stien til den |

For at gentage en kørsel på din egen maskine skal du installere de samme versioner:

```bash
python3 -m venv .qc
.qc/bin/pip install clang-format==23.1.3 clang-tidy==22.1.8
git ls-files '*.cpp' '*.hpp' | xargs .qc/bin/clang-format --dry-run -Werror
```

## Når workflowet selv fejler

| Meddelelse | Årsag | Rettelse |
| --- | --- | --- |
| `[configuration] std '<x>' is not a C++ standard` | `std` er ikke som `c++20` eller `gnu++20` | Ret inputtet |
| `[configuration] ... is not an exact version` | En værktøjsversion er et interval, en kanal eller tom | Angiv en præcis version som `23.1.3` |
| `[configuration] working-directory must be a relative path inside the repository.` | En absolut sti eller `..` | Brug en sti inde i repositoryet |
| `[configuration] No .clang-format found` | Projektet har ingen stilfil | Tilføj en `.clang-format` |
| `[configuration] compile-commands-dir '<x>' has no compile_commands.json` | Databasen blev ikke bygget før kaldet | Byg den i et tidligere trin i jobbet eller i et job, det afhænger af |
| Installationstrinnet fejler | PyPI eller runnerens netværk kan ikke nås | Kør jobbet igen; se [troubleshooting.md](troubleshooting.md) |
