<!-- translation of Capabilities.md, source sha256 a8c03a001880 -->

> Dette er en oversættelse af [`Capabilities`](Capabilities). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](Capabilities) | Dansk | [Bahasa Melayu](Capabilities.ms)

## Funktionalitet

Rækker, der siger Implementeret eller Vejledninger er skrevet, findes i dag. Resten er planlagt og følges i [projektplanen](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/docs/project-plan.md), som også beskriver hver enkelt use case.

| Funktionalitet | Status |
| --- | --- |
| Synkronisering af repositorymetadata (Gitea til GitHub-spejl) | Implementeret i `.gitea/scoped_workflows/`, med offline-tests og et valideringsworkflow |
| Konfiguration og validering af workflow-credentials | Implementeret for synkroniseringsworkflowet: en forhåndskontrol tjekker begge tokens før enhver ændring ([vejledning](Credentials.da)) |
| Tilslutning af et repository, administration af runners, fejlfinding | Vejledninger er skrevet ([tilslutning](Onboarding.da), [fejlfinding](Troubleshooting.da)); scoped levering til alle fire organisationers repositories er verificeret (MIL-002) |
| Publicering af et repositorys wiki fra `wiki/` (tilmelding, leveres til alle organisationer) | Implementeret i `.gitea/scoped_workflows/publish-wiki.yml`, med offline-tests; et pilotforsøg i et andet repository publicerer sin wiki (MIL-006) |
| Fælles kvalitetskontrol (Python og shell) | Implementeret som det genbrugelige workflow `.gitea/workflows/quality-checks.yml`, med offline-tests og et forsøg i en anden organisation; taget i brug i RepoFoundry ([vejledning](QualityChecksPythonShell.da)) |
| Versioneret udgivelse og publicering | Udgivelsesproces, changelog og opgraderingsvejledning er defineret; udgivelsesworkflowet findes, og `v1.0.0` er udgivet (MIL-004) ([vejledning](Upgrading.da)) |
