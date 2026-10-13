<!-- translation of QualityChecksPythonShell.md, source sha256 2a0c9d43c77d -->

> Dette er en oversættelse af [`QualityChecksPythonShell`](QualityChecksPythonShell). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](QualityChecksPythonShell) | Dansk | [Bahasa Melayu](QualityChecksPythonShell.ms)

# Aflæsning af resultater fra kvalitetskontrol

Sådan kalder en softwareudvikler den fælles kvalitetskontrol, aflæser en mislykket kørsel og får den til at bestå. Workflowet kører lint og formatkontrol på repositoryets Python- og shell-filer med fastlåste værktøjer, ændrer ingen fil og kræver ingen secret. Dets kontrakt er ADR-0005 i dette repository.

## Kald af workflowet

```yaml
name: Quality

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  quality:
    permissions:
      contents: read
    uses: TirSystem/github-action/.gitea/workflows/quality-checks.yml@v1
    with:
      languages: python,shell
```

| Input | Standard | Betydning |
| --- | --- | --- |
| `languages` | `python,shell` | Kommasepareret liste over de sprog, der kontrolleres |
| `working-directory` | `.` | Mappe, relativt til repositoryets rod, hvis filer kontrolleres |
| `ruff-version` | `0.6.9` | Version af ruff |
| `mypy-version` | `1.11.2` | Version af mypy |
| `shellcheck-py-version` | `0.10.0.1` | Version af pakken shellcheck-py (ShellCheck 0.10.0) |
| `shfmt-py-version` | `3.11.0.2` | Version af pakken shfmt-py (shfmt 3.11.0) |
| `tools-ref` | `v1` | Tag eller gren i `TirSystem/github-action`, hvorfra scriptet `tools/quality-checks.sh` hentes |

Henvis til workflowet ved major-tagget (`@v1`) eller et præcist tag (`@v1.0.0`), aldrig ved `main` og aldrig ved en pull requests gren: den gren slettes, når pull requesten flettes, og henvisningen holder op med at virke. Se opgraderingsvejledningen for, hvad hvert valg modtager.

Workflowfilen kalder et script i dette repository, hentet ved `tools-ref`. Et kald ved et præcist tag er kun fuldt fastlåst, når `tools-ref` angiver samme tag, for eksempel `@v1.0.1` med `tools-ref: v1.0.1`; med standardværdien følger scriptet `v1`.

## Hvad der kontrolleres

| Sprog | Filer | Værktøjer |
| --- | --- | --- |
| Python | sporede `*.py` under arbejdsmappen | `ruff check`, `ruff format --check`, `mypy --strict` |
| Shell | sporede `*.sh` under arbejdsmappen | `shellcheck`, `shfmt -d` |

Ikke-sporede filer kontrolleres ikke. Et sprog uden filer springes over med en meddelelse og tæller som bestået. Projektets tests køres ikke.

## Aflæsning af en kørsel

1. Åbn statuskontrollen på pull requesten og derefter jobbet `quality-checks`.
2. Hvert værktøj har sin egen logsektion med værktøjets navn. Hvert værktøj kører, selv om et tidligere fejlede, så én kørsel viser alle fund.
3. Et værktøj slutter med `PASS <værktøj>` eller `FAIL <værktøj>`. Sidste linje i en mislykket kørsel nævner de værktøjer, der fejlede: `Quality checks failed: ruff check shellcheck`.
4. Et fund skrives af værktøjet selv som `sti:linje:kolonne: KODE meddelelse`. Stier er relative til `working-directory`.

## Typiske fejl og rettelser

| Værktøj | Hvad loggen viser | Rettelse |
| --- | --- | --- |
| `ruff check` | `F401 ... imported but unused` | Fjern importen, eller brug den |
| `ruff format --check` | `Would reformat: <fil>` | Kør `ruff format <fil>` og commit |
| `mypy --strict` | `Function is missing a type annotation` | Tilføj typer til parametre og returværdi |
| `shellcheck` | `SC2086 ... Double quote to prevent globbing` | Sæt udvidelsen i anførselstegn: `"$1"` |
| `shfmt -d` | en forskel mellem `<fil>.orig` og `<fil>` | Kør `shfmt -w <fil>` med projektets indstillinger og commit |

For at gentage en kørsel på din egen maskine skal du installere de samme versioner og køre kommandoerne fra tabellen:

```bash
python3 -m venv .qc
.qc/bin/pip install ruff==0.6.9 mypy==1.11.2 shellcheck-py==0.10.0.1 shfmt-py==3.11.0.2
.qc/bin/ruff check . && .qc/bin/ruff format --check .
```

## Konfiguration af værktøjerne

Workflowet tilføjer ingen konfiguration; det kører fra repositoryets rod, så projektets egne filer gælder:

| Værktøj | Fil | Eksempel |
| --- | --- | --- |
| ruff | `pyproject.toml` | `[tool.ruff]` med `line-length = 100` |
| mypy | `pyproject.toml` | `[tool.mypy]` med `ignore_missing_imports` pr. modul |
| shellcheck | `.shellcheckrc` | `external-sources=true` og `source-path=SCRIPTDIR` |
| shfmt | `.editorconfig` | `[*.sh]` med `indent_size = 2` og `switch_case_indent = true` |

shfmt følger et projekts stil kun gennem `.editorconfig`. Et shell-projekt, der formaterer med egne flag (fx `shfmt -i 2 -ci`), bør forvente en formateringsfejl ved første kørsel og udtrykke flagene dér; ved den første tilslutning (RepoFoundry) var én linje, `switch_case_indent = true`, nok, og intet script blev ændret.

## Når selve workflowet fejler

| Meddelelse | Årsag | Rettelse |
| --- | --- | --- |
| `[configuration] Unknown language '<x>'` | `languages` har en anden værdi end `python` eller `shell` | Ret inputtet |
| `[configuration] working-directory must be a relative path inside the repository.` | En absolut sti eller `..` | Brug en sti inde i repositoryet |
| `[configuration] working-directory '<x>' does not exist.` | Mappen findes ikke i repositoryet | Ret inputtet |
| Installationstrinnet fejler | PyPI eller runnerens netværk kan ikke nås | Kør jobbet igen; se [troubleshooting.md](Troubleshooting.da) |
