<!-- translation of Capabilities.md, source sha256 2f30825f19a1 -->

> Dette er en oversættelse af [`Capabilities`](Capabilities). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Capabilities) | Dansk | [Bahasa Melayu](Capabilities.ms)

## Funktionalitet

Rækker, der siger Implementeret eller Vejledninger er skrevet, findes i dag. Resten er planlagt og følges i [projektplanen](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/docs/project-plan.md), som også beskriver hver enkelt use case.

| Funktionalitet | Status |
| --- | --- |
| Synkronisering af repositorymetadata (Gitea til GitHub-spejl) | Implementeret i `.gitea/scoped_workflows/`, med offline-tests og et valideringsworkflow |
| Konfiguration og validering af workflow-credentials | Implementeret for synkroniseringsworkflowet: en forhåndskontrol tjekker begge tokens før enhver ændring ([vejledning](Credentials.da)) |
| Tilslutning af et repository, administration af runners, fejlfinding | Vejledninger er skrevet ([tilslutning](Onboarding.da), [fejlfinding](Troubleshooting.da)); scoped levering til alle fire organisationers repositories er verificeret (MIL-002) |
| Publicering af et repositorys wiki fra `docs/wiki/` gennem et kaldt workflow | Implementeret som det scoped workflow `.gitea/scoped_workflows/publish-wiki-pages.yml`, med offline-tests; det kører i hvert repository med en `docs/wiki/`-mappe, og dette repositorys egen wiki er i `docs/wiki/` (MIL-008, MIL-009) |
| Fælles kvalitetskontrol (Python og shell) | Implementeret som det genbrugelige workflow `.gitea/workflows/quality-checks.yml`, med offline-tests og et forsøg i en anden organisation; taget i brug i RepoFoundry ([vejledning](QualityChecksPythonShell.da)) |
| Fælles kvalitetskontrol (C og C++, C#) | Implementeret som de genbrugelige workflows `.gitea/workflows/quality-checks-cpp.yml` og `.gitea/workflows/quality-checks-csharp.yml` med præcise værktøjsversioner og offline-tests; endnu ikke brugt i et andet repository (MIL-007) ([vejledning til C og C++](QualityChecksCpp.da), [vejledning til C#](QualityChecksCSharp.da)) |
| Kodemålinger og dækningsbadges | Implementeret og udgivet i 2.1.0 som det genbrugelige workflow `.gitea/workflows/code-metrics.yml` med en tæller, en Cobertura-læser, en SVG-renderer og offline-tests; afprøvet i et kasserepository, endnu ikke brugt i et projektrepository (MIL-010) ([vejledning](CodeMetrics.da)) |
| Engelske kommentarer | Implementeret som det genbrugelige workflow `.gitea/workflows/english-comments.yml` med en kommentarudtrækker, en sprogdetektor målt på et korpus (ADR-0012), en kommentar på pull requesten og offline-tests; endnu ikke kørt på instansen eller krævet af noget repository (MIL-013) ([vejledning](EnglishComments.da)) |
| Versioneret udgivelse og publicering | Udgivelsesproces, changelog og opgraderingsvejledning er defineret; udgivelsesworkflowet findes, og `v1.0.0` er udgivet (MIL-004) ([vejledning](Upgrading.da)) |
