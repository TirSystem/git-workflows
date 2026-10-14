# Reading C# quality-check results

How a software engineer calls the shared C# quality checks, reads a failed run
and makes it pass. The workflow checks the formatting and builds a solution or
project with warnings as errors, on an exact .NET SDK of version 10 or later,
changes no file and needs no secret. Its contract is ADR-0008 in this
repository.

## Calling the workflow

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

| Input | Default | Meaning |
| --- | --- | --- |
| `working-directory` | `.` | Directory, relative to the repository root, whose files are checked |
| `project` | empty | Solution or project file, relative to `working-directory`; empty uses the single `*.sln` or `*.slnx`, else the single `*.csproj`, that is tracked there |
| `dotnet-sdk-version` | `10.0.401` | Exact version of the .NET SDK, 10 or later; a channel such as `10.0`, a range and a version below 10 are refused |
| `tools-ref` | `v2` | Tag or branch of `TirSystem/github-action` from which the script `tools/quality-checks-csharp.sh` is fetched |

Reference the workflow at the major tag (`@v1`) or at an exact tag, never at
`main`. A call at an exact tag is pinned completely only when `tools-ref` names
the same tag. See the upgrade guide. The SDK version is exact: raising the
default is a new release of this repository, not a silent change.

## What the repository needs

- A solution or project that builds with the SDK. Several candidates need the
  `project` input; C# files with no solution or project fail with
  `[configuration]`.
- The network: `dotnet format` and `dotnet build` restore the NuGet packages of
  the project in the run.
- Rules in `.editorconfig` (and the analyzers the project enables, for example
  with `AnalysisLevel` and `EnforceCodeStyleInBuild`) decide what a finding is.

## What is checked

| Files | Tool | What it reports |
| --- | --- | --- |
| the solution or project | `dotnet format --verify-no-changes` | formatting and style that differ from `.editorconfig` |
| the same | `dotnet build -warnaserror` | compiler and analyzer warnings, which fail the build |

Untracked files are not checked. A repository without `*.cs` files passes with
a notice. Project tests are not run.

## Reading a run

1. Open the status check on the pull request, then the job
   `quality-checks-csharp`.
2. Each tool has its own log group. Both run even when the first failed, so one
   run shows all findings.
3. A tool ends with `PASS <tool>` or `FAIL <tool>`; the last line of a failed
   run names them:
   `Quality checks failed: dotnet format --verify-no-changes`.
4. A finding is written by the tool itself as `path(line,column): CODE message`.
   The path is absolute in the workspace of the runner
   (`/workspace/<owner>/<repo>/src/Program.cs(8,27)`).

## Typical failures and fixes

| Tool | What the log shows | Fix |
| --- | --- | --- |
| `dotnet format --verify-no-changes` | `Program.cs(12,5): error WHITESPACE: Fix whitespace formatting` | Run `dotnet format <project>` and commit |
| `dotnet build -warnaserror` | `CS8602: Dereference of a possibly null reference` | Fix the code (null check), do not suppress the warning without a reason |
| `dotnet build -warnaserror` | `IDE0005: Using directive is unnecessary` | Remove the directive |

To reproduce a run on your machine, use the same SDK:

```bash
dotnet --version        # 10.0.401
dotnet format src/App.sln --verify-no-changes
dotnet build src/App.sln -warnaserror
```

## When the workflow itself fails

| Message | Cause | Fix |
| --- | --- | --- |
| `[configuration] dotnet-sdk-version '<x>' is not an exact stable version 10 or later` | A channel, a range, a preview or a version below 10 | Give an exact version such as `10.0.401` |
| `[configuration] working-directory must be a relative path inside the repository.` | An absolute path or `..` | Use a path inside the repository |
| `[configuration] C# files exist but no solution or project was found` | The repository has `*.cs` files and no `*.sln`, `*.slnx` or `*.csproj` in the working directory | Add one, or set `working-directory` |
| `[configuration] Several solutions or projects were found` | More than one candidate | Set the input `project` |
| The install step fails | `dot.net` or the runner network is unreachable | Re-run the job; see [troubleshooting.md](troubleshooting.md) |
