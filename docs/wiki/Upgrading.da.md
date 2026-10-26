<!-- translation of Upgrading.md, source sha256 21362a6fcbd7 -->

> Dette er en oversættelse af [`Upgrading`](Upgrading). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Upgrading) | Dansk | [Bahasa Melayu](Upgrading.ms)

# Opgradering til en ny version af de fælles workflows

Sådan tager en softwareudvikler en ny udgivelse af de fælles workflows i brug uden risiko: læs changelog, prøv opdateringen ét sted, og gå tilbage, hvis den fejler. Versionsreglerne er udgivelsesprocessens: én version for hele repositoryet, tags `vMAJOR.MINOR.PATCH` og et flytbart major-tag `vMAJOR`.

## Hvilken version du følger

| I din `uses:`-linje | Du modtager | Brug den, når |
| --- | --- | --- |
| `@v1.2.0` | aldrig noget nyt | en pipeline ikke må ændre sig |
| `@v1` | kun kompatible udgivelser (minor og patch) | standardvalget for et projekt |
| `@main` | alt, også uudgivet | aldrig; kun til dette repositorys egne tests |

En udgivelse, der bryder kompatibiliteten, får en ny major-version (`v2`), så en pipeline på `@v1` aldrig modtager den, før du selv ændrer linjen.

Kvalitetskontrol-workflowene (`quality-checks.yml`, `quality-checks-cpp.yml` og `quality-checks-csharp.yml`) og kodemålings-workflowet (`code-metrics.yml`) henter deres scripts ved deres input `tools-ref`, som som standard er det aktuelle major-tag (`v2`). For at fastlåse et helt skal du kalde det ved et præcist tag og sætte `tools-ref` til samme tag; ellers følger scriptet major-tagget.

Det scoped workflow **Sync GitHub mirror metadata** leveres af instansen og står ikke i dine `uses:`-linjer; du kan ikke fastlåse det, men det henter sit script ved major-tagget. Publicering af wiki er et genbrugeligt workflow, du kalder (`publish-wiki-pages.yml`); det scoped workflow **Publish wiki** og dets markør `wiki/.publish` blev fjernet i 2.0.0, så et repository, der stadig har markøren, publicerer ikke mere, før det kalder det genbrugelige workflow (se introduktionsguiden).

## Aflæsning af en changelog-post

Åbn `CHANGELOG.md` i `TirSystem/git-workflows` eller tagget udgivelsesside. En post har op til fire grupper:

| Gruppe | Hvad den betyder for dig |
| --- | --- |
| Breaking | Du skal handle: et navn, et input, en secret eller en standardværdi er ændret. En udgivelse med denne gruppe har en ny major-version |
| Added | Intet at gøre; et nyt valgfrit input, workflow eller en ny funktion |
| Changed | Intet at gøre; ingen synlig virkning for eksisterende kaldere |
| Fixed | Intet at gøre; en rettelse, du modtager på `@v1` |

En post, der ændrer credentials, tokens eller tilladelser, siger det; kontroller dine secrets, før du opgraderer.

## Afprøvning af en opdatering

1. Ændr versionen i **ét** repository på en gren:
   ```yaml
   jobs:
     quality:
       uses: TirSystem/git-workflows/.gitea/workflows/quality-checks.yml@v2
   ```
2. Åbn en pull request, og læs kørslen. En mislykket kontrol viser værktøj, fil og meddelelse (se vejledningen til aflæsning af kvalitetskontrollens resultater).
3. For en udgivelse, der bryder kompatibiliteten, følges opgraderingsnoterne i changelog-posten, og trinnet gentages.
4. Når pull requesten er grøn, foretages den samme ændring i de øvrige repositories.

## Tilbage igen

1. Ret linjen tilbage til det forrige præcise tag, fx `@v1.2.0`, og flet. Præcise tags slettes eller flyttes aldrig, så det virker altid.
2. Fortæl vedligeholderne, hvilken udgivelse der fejlede, og hvad du så, så major-tagget kan flyttes tilbage og en rettelse udgives.

## Når noget er uklart

| Symptom | Sandsynlig årsag | Rettelse |
| --- | --- | --- |
| Kørslen siger, at workflowet ikke kan findes | Tagget findes ikke, eller stien er forkert | Kontroller tagget på udgivelsessiden og stien `.gitea/workflows/quality-checks.yml` |
| En grøn pipeline blev rød efter en udgivelse på `@v1` | En kompatibel udgivelse burde ikke gøre det | Fastlås det forrige præcise tag, og meld det som en defekt |
| Et input accepteres ikke længere | En udgivelse, der bryder kompatibiliteten, har omdøbt det | Læs gruppen Breaking i posten |
