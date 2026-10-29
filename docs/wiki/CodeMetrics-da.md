<!-- translation of CodeMetrics.md, source sha256 2363690e9a6c -->

> Dette er en oversættelse af [`CodeMetrics`](CodeMetrics). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](CodeMetrics) · **Dansk** · [Bahasa Melayu](CodeMetrics-ms)

# Visning af kodemålinger og dækningsbadges

Sådan kalder en softwareudvikler det fælles kodemålings-workflow og viser dets tre badges (kodefiler, kodelinjer og dækning) i en README. Workflowet tæller repositoryets kode, læser en dækningsrapport, som kalderen leverer, og committer tre SVG-filer til en `badges`-gren. Det kører ingen test og kræver ingen secret. Dets kontrakt er ADR-0010 i dette repository.

## Kald af workflowet

Workflowet kan ikke se filerne fra dit testjob, så testene kører i et job, du selv ejer, uploader Cobertura XML-rapporten som artefakt, og målingsjobbet kører bagefter:

```yaml
name: Code metrics

on:
  push:
    branches: [ main ]

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4.2.2
      - run: python3 -m pip install pytest pytest-cov && python3 -m pytest --cov --cov-report=xml
      - uses: actions/upload-artifact@v4.6.2
        with:
          name: coverage
          path: coverage.xml

  metrics:
    needs: tests
    permissions:
      contents: write
    uses: TirSystem/git-workflows/.gitea/workflows/code-metrics.yml@v2
    with:
      coverage-artifact: coverage
      coverage-report: coverage.xml
```

| Input | Standard | Betydning |
| --- | --- | --- |
| `working-directory` | `.` | Mappe, relativt til repositoryets rod, hvis kode tælles |
| `exclude` | tom | Kommasepareret liste af mønstre for filer og mapper, der ikke tælles, ud over standardudeladelserne; et mønster uden `/` matcher et navn overalt, et mønster med `/` matcher stien under `working-directory` |
| `coverage-report` | tom | Cobertura XML-rapport: filen i artefaktet, når `coverage-artifact` er sat, ellers en sti i repositoryet; tom giver intet dækningsbadge |
| `coverage-artifact` | tom | Navn på et artefakt, uploadet af et tidligere job i samme kørsel, der indeholder rapporten |
| `coverage-warn` | `60` | Dækning i procent, under hvilken badget er rødt |
| `coverage-good` | `80` | Dækning i procent, fra hvilken badget er grønt; derimellem er det gult |
| `badges-branch` | `badges` | Gren, der indeholder badge-filerne; den oprettes, hvis den ikke findes |
| `tools-ref` | `v3` | Tag eller gren i `TirSystem/git-workflows`, hvorfra scripts i `tools/` hentes |

Reference workflowet ved major-tagget (`@v1`) eller ved et præcist tag, aldrig ved `main`. Et kald ved et præcist tag er kun fuldt fastlåst, når `tools-ref` navngiver samme tag. Se opgraderingsvejledningen. Start workflowet kun ved push til din standardgren: badge-committet har `[skip ci]` og laves med kørslens token, som ikke starter en ny kørsel, men en trigger på alle grene ville skrive ét commit pr. gren.

## Hvad der tælles

- En kodefil er en tekstfil med filendelsen for et understøttet sprog: Python, shell, PowerShell, C, C++, C#, Java, JavaScript, TypeScript, Go, Rust og SQL. Markdown, YAML, JSON, XML, HTML og CSS er ikke kodefiler.
- Hver linje er præcis én af: tom (kun blanktegn), kommentar (kun kommentartekst) eller kode (alt andet, også en linje med kode og en afsluttende kommentar). Badget viser kun kodelinjerne.
- En kommentarmarkør i en streng er ikke en kommentar, og en Python-docstring er en streng og tæller derfor som kode.
- Mapper, der starter med punktum, og `node_modules`, `vendor`, `third_party`, `dist`, `build`, `out`, `bin`, `obj`, `target`, `venv`, `__pycache__` og `shared-scripts` tælles ikke. Genereret kode udelades med `exclude`.
- Rå og ordrette strenge, der afviger fra en almindelig streng (Rust `r#"..."#`, C# `@"..."`, C++-rå strenge), kan tælles forkert. Tallene afviger lidt fra andre værktøjer; reglerne er de samme ved hver kørsel.

## Dækningsbadget

Rapporten er en Cobertura XML-fil, som `coverage.py` (`coverage xml`), `gcovr` (`--cobertura`) og `coverlet` (formatet `cobertura`) skriver. Badget viser `lines-covered` over `lines-valid`, afrundet til hele procent, og farven følger de to grænser. En rapport, der ikke findes, ikke er velformet Cobertura XML eller ikke har gyldige linjer, får kørslen til at fejle med filen nævnt; dækningsbadget skrives aldrig som `0%` for en dårlig rapport. Uden `coverage-report` består kørslen med en note og uden dækningsbadge.

## Visning af badges

Tilføj billederne til README med grenens rå URL'er:

```markdown
![code files](https://git.tirsystem.com/OWNER/REPO/raw/branch/badges/code-files.svg)
![lines of code](https://git.tirsystem.com/OWNER/REPO/raw/branch/badges/code-lines.svg)
![coverage](https://git.tirsystem.com/OWNER/REPO/raw/branch/badges/coverage.svg)
```

På GitHub-spejlet bruges `https://raw.githubusercontent.com/OWNER/REPO/badges/code-files.svg`; push-spejlet kopierer grenen. `badges`-grenen indeholder også `code-metrics.json` med tallene pr. sprog. Instansen cacher en rå fil i op til seks timer, så et ændret badge kan vise det gamle tal et stykke tid dér; spejlet cacher i fem minutter. Et privat repository viser ikke badges for en læser, der ikke er logget ind.

## Når workflowet fejler

| Meddelelse | Årsag | Løsning |
| --- | --- | --- |
| `[configuration] working-directory must be a relative path inside the repository.` | En absolut sti eller `..` | Brug en sti inde i repositoryet |
| `[configuration] coverage-report '<x>' does not exist.` | Rapporten blev ikke frembragt, eller artefaktnavnet eller stien er forkert | Tjek testjobbet og artefaktnavnet; stien er inde i artefaktet |
| `[configuration] coverage-report '<x>' is not well-formed XML` eller `is not a Cobertura report` | Filen har et andet format | Skriv Cobertura XML (`coverage xml`, `gcovr --cobertura`) |
| `[configuration] coverage-report '<x>' has no valid lines.` | Testene kørte ingen målt kode | Tjek dækningskonfigurationen |
| `[configuration] coverage-artifact '<x>' needs coverage-report` | Artefaktet er navngivet, men ikke filen i det | Sæt `coverage-report` |
| `[configuration] coverage-warn ... is above coverage-good` eller `is not a number from 0 to 100` | En grænse er ugyldig | Ret inputtet |
| `[configuration] badges-branch '<x>' must not be a default branch` eller `holds files that are not badge files` | Grenen hedder `main`, `master` eller har andet indhold | Brug en gren, der kun indeholder badges |
| `the push to '<x>' failed twice` | En anden kørsel skrev grenen samtidig, eller tokenet kan ikke skrive | Kør igen; tjek at jobbet har `contents: write` |
| Download-trinnet fejler | Artefaktet findes ikke i denne kørsel, eller jobbet kører ikke efter testjobbet | Tilføj `needs:` og tjek artefaktnavnet |
