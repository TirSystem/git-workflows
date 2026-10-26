<!-- translation of EnglishComments.md, source sha256 a9533f14d5f5 -->

> Dette er en oversættelse af [`EnglishComments`](EnglishComments). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](EnglishComments) | Dansk | [Bahasa Melayu](EnglishComments.ms)

# Kommentarer i kildekoden på engelsk

Sådan kalder en softwareudvikler det fælles workflow, der kontrollerer, at
kommentarerne og docstrings i en pull request er skrevet på engelsk. Workflowet
lader kørslen fejle, når én ikke er det, og skriver én kommentar på pull
requesten, der nævner forfatteren. Det ændrer ingen fil og sender ingen
kildetekst ud af instansen. Beslutningen bag er ADR-0012 i dette repository.

## Kald af workflowet

```yaml
name: English comments

on:
  pull_request:

jobs:
  english-comments:
    uses: TirSystem/git-workflows/.gitea/workflows/english-comments.yml@v2
    with:
      exclude: "docs/generated/**"
      allowed-words-file: .english-comments-allowed-words
```

| Input | Standard | Betydning |
| --- | --- | --- |
| `scope` | `changed` | `changed` kontrollerer kommentarerne på de linjer, pull requesten tilføjer; `all` kontrollerer hver sporet fil |
| `exclude` | | Kommasepareret liste af fil- eller stimønstre, der ikke kontrolleres (`*` og `**` er jokertegn) |
| `allowed-words-file` | | En fil i repositoryet med ord, der aldrig bedømmes, ét pr. linje; `#` starter en kommentar |
| `threshold` | `0.6` | Sandsynligheden, over 0 og højst 1, hvorfra en kommentar regnes for ikke at være engelsk |
| `min-words` | `3` | En kommentar med færre ord bedømmes ikke |
| `langid-version`, `numpy-version` | `1.1.6`, `2.1.3` | De fastlåste pakker, detektoren bruger |
| `tools-ref` | den nuværende hovedversion | Det tag i dette repository, hvis scripts køres; fastlås det sammen med workflowet |

Den valgfri secret `REPORT_TOKEN` er et Gitea-token, der må kommentere på pull
requests. Uden den bruger workflowet kørslens eget token, så kommentaren
skrives af Actions-botten. En pull request fra en fork har et token med kun
læseadgang: kontrollen får stadig kørslen til at fejle, men der skrives ingen
kommentar.

## Hvad der kontrolleres

Kommentarerne og docstrings i filer på de sprog, kodetælleren kender
([kodemålinger](CodeMetrics)): Python, shell, PowerShell, C, C++, C#, Java,
JavaScript, TypeScript, Go, Rust og SQL. Strenge og kode læses ikke. Kommentarlinjer
efter hinanden danner en blok. Hver linje i en blok bedømmes for sig (mindst fire ord og en
sandsynlighed på mindst 0,7), så en engelsk linje ikke kan skjule en dansk ved siden af; når ingen linje
markeres, bedømmes blokken som helhed (mindst `min-words` ord og `threshold`), så en sætning delt over korte
linjer ikke overses.

Før en blok bedømmes, fjernes alt, der ikke er et ord: stier, URL'er, tilvalg
(`--output`), filnavne, identifikatorer (`snake_case`, `camelCase`), tal,
akronymer og konstanter (`JSON`), en indledende etiket som `Usage:` og ordene
i filen med tilladte ord. En blok med færre end `min-words` ord tilbage
bedømmes ikke, så en kort kommentar slipper igennem. Kommentarer, der
konfigurerer et værktøj (`noqa`, `type:`, `pragma`, `shellcheck`), læses ikke.

## Når kontrollen fejler

Kørslen fejler, hvert fund vises som en annotation (`::error file=...,line=...`)
og i loggen som `file:line: looks Danish (0.93): "the comment"`, og én kommentar
på pull requesten opregner dem og nævner forfatteren. En ny kørsel opdaterer den
kommentar; når pull requesten består, markeres kommentaren som løst og nævner
ikke længere nogen.

Ret det ved at skrive kommentaren om på engelsk. For et citat eller et navn, der
ikke er engelsk, kan du enten skrive `english-comments: ignore` i kommentaren
(det springer hele den kommentarblok over, den står i), eller tilføje ordet til
filen med tilladte ord.

## Blokering af sammenfletningen

En fejlende kørsel blokerer ikke i sig selv en sammenfletning. Markér kontrollen
som påkrævet i grenbeskyttelsen af målgrenen: kør workflowet én gang på en pull
request og vælg dets post på listen over statuskontroller (det præcise navn
dannes af det kaldende workflow, dets job og hændelsen). At indstille
grenbeskyttelse er repositoryejerens handling; workflowet ændrer den ikke.

## Hvor præcis den er

Detektoren er `langid`, begrænset til engelsk, dansk, norsk, svensk, tysk,
fransk, malajisk, indonesisk og hollandsk. På repositoryets korpus markerer den
ingen af 300 engelske kommentarer, 44 af 45 danske og 41 af 45 malajiske
kommentarer og alle 48 tyske, svenske, norske og franske (ADR-0012). Dens
grænser:

- en kommentar på ét eller to ord, eller en der mest består af navne, bedømmes ikke;
- en kommentar på dårligt engelsk slipper igennem, og en kommentar, der blander
  engelske fagudtryk med få danske eller malajiske ord, kan slippe igennem;
- korpussets danske og malajiske kommentarer er skrevet til testen og ikke samlet
  fra rigtig kode, så rigtig kode vil vise andre fejl. Meld en misset kommentar
  eller et falsk fund med kommentaren, så kommer den med i korpussen.

## Fejlfinding

| Besked | Årsag |
| --- | --- |
| `[configuration] give --base` | Workflowet blev startet af en hændelse, der ikke er en pull request, med `scope: changed`; kald det på `pull_request` eller brug `scope: all` |
| `[configuration] git diff failed` | Basisgrenen findes ikke i checkout; workflowet henter hele historikken, så tjek at pull requesten har en målgren |
| `[configuration] langid is not installed` | Installationstrinnet fejlede; tjek de fastlåste versioner |
| `[permissions] ... may not comment on pull requests` | Tokenet må ikke kommentere; giv `REPORT_TOKEN` skriveadgang til issues og pull requests |
| Et fund, der ikke er et fund | Tilføj ordene til filen med tilladte ord, eller `english-comments: ignore` til kommentaren |
