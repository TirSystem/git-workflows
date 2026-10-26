<!-- Generated from README.md by tools/build_wiki.py. Edit the source, not this page. -->

> This page is generated from [`README.md`](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/README.md). Changes made here are overwritten the next time the wiki is published.

English | [Dansk](Capabilities.da) | [Bahasa Melayu](Capabilities.ms)

## Capabilities

Rows that say Implemented or Guides written exist today. The rest is planned and tracked in the [Project Plan](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/docs/project-plan.md), which also describes each use case.

| Capability | Status |
| --- | --- |
| Synchronize repository metadata (Gitea to GitHub mirror) | Implemented in `.gitea/scoped_workflows/`, with offline tests and a validation workflow |
| Configure and validate workflow credentials | Implemented for the sync workflow: preflight checks both tokens before any change ([guide](Credentials)) |
| Onboard a repository, manage runners, diagnose failures | Guides written ([onboarding](Onboarding), [troubleshooting](Troubleshooting)); scoped delivery to the repositories of all four organizations verified (MIL-002) |
| Publish a repository wiki from `docs/wiki/` through a called workflow | Implemented as the reusable workflow `.gitea/workflows/publish-wiki-pages.yml`, with offline tests; called by every repository that publishes a wiki, and this repository's own wiki is in `docs/wiki/` (MIL-008, MIL-009) |
| Shared quality checks (Python and shell) | Implemented as the reusable workflow `.gitea/workflows/quality-checks.yml`, with offline tests and a trial in a second organization; adopted in RepoFoundry ([guide](QualityChecksPythonShell)) |
| Shared quality checks (C and C++, C#) | Implemented as the reusable workflows `.gitea/workflows/quality-checks-cpp.yml` and `.gitea/workflows/quality-checks-csharp.yml` with exact tool versions and offline tests; not yet used in another repository (MIL-007) ([C and C++ guide](QualityChecksCpp), [C# guide](QualityChecksCSharp)) |
| Code metrics and coverage badges | Implemented and released in 2.1.0 as the reusable workflow `.gitea/workflows/code-metrics.yml` with a counter, a Cobertura reader, an SVG renderer and offline tests; tried in a throwaway repository, not yet used in a project repository (MIL-010) ([guide](CodeMetrics)) |
| English comments | Implemented as the reusable workflow `.gitea/workflows/english-comments.yml` with a comment extractor, a language detector measured on a corpus (ADR-0012), a pull request comment and offline tests; not yet run on the instance or required by any repository (MIL-013) ([guide](EnglishComments)) |
| Versioned release and publishing | Release process, changelog and upgrade guide defined; the release workflow exists and `v1.0.0` is released (MIL-004) ([guide](Upgrading)) |
