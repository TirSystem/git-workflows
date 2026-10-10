<!-- translation of Capabilities.md, source sha256 5856fdc70a30 -->

> Ini ialah terjemahan [`Capabilities`](Capabilities). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Capabilities) | [Dansk](Capabilities.da) | Bahasa Melayu

## Keupayaan

Hanya baris pertama yang dilaksanakan. Selebihnya dirancang dan dijejaki dalam [Pelan Projek](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/docs/project-plan.md), yang juga menerangkan setiap kes guna (use case).

| Keupayaan | Status |
| --- | --- |
| Menyegerakkan metadata repositori (Gitea ke cermin GitHub) | Dilaksanakan dalam `.gitea/scoped_workflows/`, dengan ujian luar talian dan aliran kerja pengesahan |
| Mengkonfigur dan mengesahkan kelayakan (credentials) aliran kerja | Dilaksanakan untuk aliran kerja penyegerakan: semakan awal (preflight) memeriksa kedua-dua token sebelum sebarang perubahan ([panduan](Credentials.ms)) |
| Menyertakan repositori, mengurus runner, mendiagnosis kegagalan | Panduan telah ditulis ([menyertakan repositori](Onboarding.ms), [diagnosis](Troubleshooting.ms)); penghantaran scoped ke repositori lain belum disahkan; use case ringkas masih terbuka (MIL-002) |
| Semakan kualiti bersama | Dirancang (MIL-003) |
| Keluaran dan penerbitan berversi | Dirancang (MIL-004) |

### Menyegerakkan metadata GitHub

Menyegerakkan penerangan dan topik repositori Gitea ke push mirror GitHub.

#### Jadual (cron)

Setiap hari pada 03:17 UTC (`17 3 * * *`), serta pada setiap push ke `main` dan `workflow_dispatch` manual.

#### Aliran kerja

```plantuml
@startuml
title Sync Gitea repository description and topics to GitHub

autonumber

actor "Push to main,\nmanual trigger, or schedule" as Trigger
participant "Gitea Actions\nsync-github-metadata" as Workflow
participant "Gitea REST API" as Gitea
participant "GitHub REST API" as GitHub

Trigger -> Workflow: Start workflow
activate Workflow

Workflow -> Workflow: Read and validate secrets
note right
TOKEN_FOR_GITEA
PAT_FOR_GITHUB
end note

alt secret validation failed
  Workflow --> Trigger: workflow failed
end


Workflow -> Gitea: GET /repos/{owner}/{repo}
Gitea --> Workflow: Description and topics

Workflow -> Gitea: GET /repos/{owner}/{repo}/push_mirrors
Gitea --> Workflow: Push mirror response

alt mirrors is not a list
    Workflow --> Trigger: Log a warning and succeed\n(GitHub metadata not synced)
else mirrors is a list with no GitHub mirror
    Workflow --> Trigger: Log that there is nothing to sync and succeed
else mirrors is a list
    Workflow -> Workflow: Find GitHub owner and repo from remote_address

    Workflow -> GitHub: PATCH /repos/{owner}/{repo}\n{description}
    GitHub --> Workflow: Repository updated

    Workflow -> GitHub: PUT /repos/{owner}/{repo}/topics\n{names}
    GitHub --> Workflow: Topics updated

    Workflow --> Trigger: Sync completed
else Gitea API denies access
    Gitea --> Workflow: HTTP 403 Forbidden
    Workflow --> Trigger: Workflow fails
else GitHub API denies access
    GitHub --> Workflow: HTTP error
    Workflow --> Trigger: Workflow fails
end
deactivate Workflow
@enduml
```
