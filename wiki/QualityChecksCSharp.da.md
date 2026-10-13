<!-- translation of QualityChecksCSharp.md, source sha256 36e34031e0b9 -->

> Dette er en oversættelse af [`QualityChecksCSharp`](QualityChecksCSharp). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](QualityChecksCSharp) | Dansk | [Bahasa Melayu](QualityChecksCSharp.ms)

# Aflæsning af resultater fra kvalitetskontrol af C#

Sådan kalder en softwareudvikler den fælles kvalitetskontrol af C#, aflæser en mislykket kørsel og får den til at bestå. Workflowet kontrollerer formateringen og bygger en solution eller et projekt med advarsler som fejl, på et præcist .NET SDK i version 10 eller nyere, ændrer ingen fil og kræver ingen secret. Dets kontrakt er ADR-0008 i dette repository.

## Kald af workflowet

```yaml
name: Quality C#

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  quality:
    permissions:
      contents: read
    uses: TirSystem/github-action/.gitea/workflows/quality-checks-csharp.yml@v1
    with:
      project: src/App.sln
```

| Input | Standard | Betydning |
| --- | --- | --- |
| `working-directory` | `.` | Mappe, relativt til repositoryets rod, hvis filer kontrolleres |
| `project` | tom | Solution- eller projektfil, relativt til `working-directory`; tom bruger den eneste sporede `*.sln` eller `*.slnx`, ellers den eneste `*.csproj`, der er sporet dér |
| `dotnet-sdk-version` | `10.0.401` | Præcis version af .NET SDK, 10 eller nyere; en kanal som `10.0`, et interval og en version under 10 afvises |
| `tools-ref` | `v1` | Tag eller gren i `TirSystem/github-action`, hvorfra scriptet `tools/quality-checks-csharp.sh` hentes |

Henvis til workflowet ved major-tagget (`@v1`) eller et præcist tag, aldrig ved `main`. Et kald ved et præcist tag er kun fuldt fastlåst, når `tools-ref` angiver samme tag. Se opgraderingsvejledningen. SDK-versionen er præcis: at hæve standardværdien er en ny udgivelse af dette repository, ikke en stille ændring.

## Hvad repositoryet skal have

- En solution eller et projekt, der bygger med SDK'et. Flere kandidater kræver inputtet `project`; C#-filer uden solution eller projekt fejler med `[configuration]`.
- Netværk: `dotnet format` og `dotnet build` gendanner projektets NuGet-pakker i kørslen.
- Regler i `.editorconfig` (og de analysatorer, projektet slår til, for eksempel med `AnalysisLevel` og `EnforceCodeStyleInBuild`) afgør, hvad et fund er.

## Hvad der kontrolleres

| Filer | Værktøj | Hvad det melder |
| --- | --- | --- |
| solutionen eller projektet | `dotnet format --verify-no-changes` | formatering og stil, der afviger fra `.editorconfig` |
| det samme | `dotnet build -warnaserror` | compiler- og analysatoradvarsler, som får bygningen til at fejle |

Usporede filer kontrolleres ikke. Et repository uden `*.cs`-filer består med en bemærkning. Projektets tests køres ikke.

## Aflæsning af en kørsel

1. Åbn statuskontrollen på pull requesten og derefter jobbet `quality-checks-csharp`.
2. Hvert værktøj har sin egen logggruppe. Begge kører, selv om det første fejlede, så én kørsel viser alle fund.
3. Et værktøj ender med `PASS <værktøj>` eller `FAIL <værktøj>`; sidste linje i en mislykket kørsel nævner dem: `Quality checks failed: dotnet format --verify-no-changes`.
4. Et fund skrives af værktøjet selv som `path(line,column): CODE message`. Stien er absolut i runnerens arbejdsområde (`/workspace/<owner>/<repo>/src/Program.cs(8,27)`).

## Typiske fejl og rettelser

| Værktøj | Hvad loggen viser | Rettelse |
| --- | --- | --- |
| `dotnet format --verify-no-changes` | `Program.cs(12,5): error WHITESPACE: Fix whitespace formatting` | Kør `dotnet format <projekt>`, og commit |
| `dotnet build -warnaserror` | `CS8602: Dereference of a possibly null reference` | Ret koden (null-kontrol); undertryk ikke advarslen uden en begrundelse |
| `dotnet build -warnaserror` | `IDE0005: Using directive is unnecessary` | Fjern direktivet |

For at gentage en kørsel på din egen maskine skal du bruge samme SDK:

```bash
dotnet --version        # 10.0.401
dotnet format src/App.sln --verify-no-changes
dotnet build src/App.sln -warnaserror
```

## Når workflowet selv fejler

| Meddelelse | Årsag | Rettelse |
| --- | --- | --- |
| `[configuration] dotnet-sdk-version '<x>' is not an exact stable version 10 or later` | En kanal, et interval, en preview eller en version under 10 | Angiv en præcis version som `10.0.401` |
| `[configuration] working-directory must be a relative path inside the repository.` | En absolut sti eller `..` | Brug en sti inde i repositoryet |
| `[configuration] C# files exist but no solution or project was found` | Repositoryet har `*.cs`-filer og ingen `*.sln`, `*.slnx` eller `*.csproj` i arbejdsmappen | Tilføj en, eller sæt `working-directory` |
| `[configuration] Several solutions or projects were found` | Mere end én kandidat | Sæt inputtet `project` |
| Installationstrinnet fejler | `dot.net` eller runnerens netværk kan ikke nås | Kør jobbet igen; se [troubleshooting.md](troubleshooting.md) |
