<!-- translation of Home.md, source sha256 8d1f5ed6df38 -->

> Ini ialah terjemahan [`Home`](Home). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Home) | [Dansk](Home.da) | Bahasa Melayu

# TirSystem GitHub Actions

Koleksi aliran kerja (workflow) Gitea Actions yang boleh digunakan semula untuk profesional DevOps dan jurutera perisian yang mengusahakan projek TirSystem.


## Gambaran keseluruhan

Repositori ini ialah koleksi pusat bagi automasi yang boleh digunakan semula untuk repositori TirSystem. Repositori utama berada di `git.tirsystem.com` (Gitea) dan dicerminkan dengan push ke GitHub.

Ia mengandungi lima aliran kerja: penyegerakan metadata ke cermin GitHub, penerbitan wiki, semakan kualiti bersama, aliran kerja keluaran dan pengesahan repositori sendiri. Ia disenaraikan dengan tujuan dan rajah di bawah [Aliran kerja](#aliran-kerja).


## Aliran kerja

Terdapat lima aliran kerja dalam repositori ini. Aliran kerja **scoped** dihantar oleh instans ke setiap repositori organisasi TirSystem dan tidak memerlukan apa-apa dalam repositori; aliran kerja **boleh guna semula** dipanggil oleh sebuah repositori dengan `uses:`; yang lain hanya berjalan di sini. Rajah ialah kod sumber PlantUML dan dalam bahasa Inggeris.

| Aliran kerja | Fail | Jenis | Bermula apabila | Tujuan |
| --- | --- | --- | --- | --- |
| Sync GitHub mirror metadata | [`sync-github-metadata.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/scoped_workflows/sync-github-metadata.yml) | Scoped | push ke `main`, manual, setiap hari 03:17 UTC | Menyalin penerangan dan topik repositori Gitea ke push mirror GitHub-nya |
| Publish wiki | [`publish-wiki.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/scoped_workflows/publish-wiki.yml) | Scoped, pilih menyertai dengan `wiki/.publish` | push ke `main` yang mengubah `wiki/**`, manual | Menerbitkan halaman dalam `wiki/` ke wiki repositori |
| Quality checks | [`quality-checks.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/quality-checks.yml) | Boleh guna semula (`workflow_call`) | panggilan daripada repositori lain | Menjalankan ruff, mypy, shellcheck dan shfmt pada fail yang dijejaki dan tidak mengubah apa-apa |
| Release | [`release.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/release.yml) | Repositori ini sahaja | manual | Mencipta tag versi, halaman keluaran dan tag major selepas semakan |
| Validate workflows | [`validate-workflows.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/validate-workflows.yml) | Repositori ini sahaja | pull request, push ke `main`, manual | Menghurai setiap aliran kerja sebagai YAML dan menjalankan ujian luar talian |

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

### Menerbitkan wiki

Menerbitkan `wiki/` ke wiki repositori, hanya dalam repositori yang telah menyertai dengan `wiki/.publish`. Perkataan `prune` dalam fail itu juga memadam halaman yang tiada dalam `wiki/`.

#### Aliran kerja

```plantuml
@startuml
title Publish wiki/ to the repository wiki

autonumber

actor "Push to main that changes wiki/**,\nor manual trigger" as Trigger
participant "Gitea Actions\npublish-wiki" as Workflow
participant "shared-scripts\n(tools/publish_wiki.py at v1)" as Script
participant "Gitea wiki API" as Wiki

Trigger -> Workflow: Start workflow
activate Workflow
Workflow -> Script: Check out the repository and the script, run it
activate Script

alt wiki/.publish does not exist
  Script --> Workflow: Log that publishing is not enabled and succeed\n(nothing is written)
else wiki/ has no Markdown pages
  Script --> Workflow: Fail with [configuration]\n(an empty wiki/ never deletes pages)
else
  Script -> Script: Read the marker (empty, or the word prune)\nand TOKEN_FOR_GITEA_WIKI
  Script -> Wiki: GET repository (preflight)
  Wiki --> Script: Wiki is enabled, token accepted
  Script -> Wiki: GET pages
  Wiki --> Script: Existing pages
  Script -> Wiki: Create new pages, update changed pages
  opt marker says prune
    Script -> Wiki: Delete pages that are not in wiki/
  end
  Script --> Workflow: Log created, updated and deleted counts
end
deactivate Script
Workflow --> Trigger: Workflow result
deactivate Workflow
@enduml
```

### Semakan kualiti

Aliran kerja boleh guna semula untuk Python dan shell, dipanggil dengan `uses: TirSystem/github-action/.gitea/workflows/quality-checks.yml@v1` (lihat [panduan](QualityChecksPythonShell)).

#### Aliran kerja

```plantuml
@startuml
title Shared quality checks (reusable workflow)

autonumber

actor "Calling repository\nuses: ...quality-checks.yml@v1" as Caller
participant "Gitea Actions\nquality-checks" as Workflow
participant "PyPI" as PyPI

Caller -> Workflow: workflow_call with languages,\nworking-directory and tool versions
activate Workflow

Workflow -> Workflow: Validate the inputs
alt languages or working-directory is invalid
  Workflow --> Caller: Fail with [configuration]
end

Workflow -> Workflow: Check out the calling repository
Workflow -> PyPI: Install the pinned tools in a virtual environment\n(ruff, mypy, shellcheck-py, shfmt-py as selected)
PyPI --> Workflow: Tools installed

loop for each selected language
  Workflow -> Workflow: List tracked files
  alt no files of that language
    Workflow -> Workflow: Notice: nothing was checked
  else
    Workflow -> Workflow: Run every tool and record PASS or FAIL
  end
end

alt any tool failed
  Workflow --> Caller: Fail and list the failed tools
else
  Workflow --> Caller: All selected checks passed
end
deactivate Workflow
@enduml
```

### Keluaran

Dimulakan secara manual oleh penyelenggara; dengan `dry_run` `true` (lalai) ia hanya menyemak (lihat [proses keluaran](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/guides/release-process.md)).

#### Aliran kerja

```plantuml
@startuml
title Release this repository

autonumber

actor "Maintainer\n(workflow_dispatch: version, dry_run)" as Trigger
participant "Gitea Actions\nrelease" as Workflow
participant "Gitea REST API" as Gitea

Trigger -> Workflow: Start with version and dry_run
activate Workflow

Workflow -> Workflow: Check the version and read CHANGELOG.md
alt version malformed or no changelog entry
  Workflow --> Trigger: Fail with [validation] or [configuration]
end

Workflow -> Gitea: GET branch main and status of the commit
Gitea --> Workflow: Tip of main and the validation run
alt commit is not the tip of main,\nor the validation run is not green
  Workflow --> Trigger: Fail with [validation]\n(no tag is created)
end

Workflow -> Gitea: GET tags
Gitea --> Workflow: Existing tags
alt tag vMAJOR.MINOR.PATCH exists
  Workflow --> Trigger: Fail with [validation]\n(tags are never moved)
end

alt dry_run is true (default)
  Workflow --> Trigger: Log what would be created and stop
else
  Workflow -> Gitea: POST release (creates the version tag,\nbody is the changelog entry)
  opt this is the highest version of its major
    Workflow -> Gitea: Delete and recreate the major tag vMAJOR
  end
  Workflow --> Trigger: Released
end
deactivate Workflow
@enduml
```

### Mengesahkan aliran kerja

Pengesahan repositori sendiri: ujian luar talian yang menjadi syarat bagi setiap pull request.

#### Aliran kerja

```plantuml
@startuml
title Validate workflows (this repository's own checks)

autonumber

actor "Pull request,\npush to main, or manual trigger" as Trigger
participant "Gitea Actions\nvalidate-workflows" as Workflow

Trigger -> Workflow: Start workflow
activate Workflow
Workflow -> Workflow: Check out the repository
Workflow -> Workflow: Create a virtual environment and\ninstall tests/requirements.txt
Workflow -> Workflow: Run pytest on tests/ (offline, no secrets):\nworkflows parse as YAML, no embedded Python,\nscripts compile, wiki pages and translations are current,\nsync, publish and release flows against a fake API

alt a test fails
  Workflow --> Trigger: Workflow fails (the pull request is not ready)
else
  Workflow --> Trigger: Workflow succeeds
end
deactivate Workflow
@enduml
```


## Keperluan

- Satu instans Gitea dengan Actions diaktifkan dan satu runner yang menyediakan `ubuntu-latest` dengan `python3`
- Satu push mirror GitHub yang dikonfigurasi pada repositori Gitea (paling banyak satu; repositori tanpa cermin dilangkau dengan jayanya)
- Rahsia (secret) repositori:
  - `TOKEN_FOR_GITEA`: token API Gitea (token sahaja, tanpa JSON)
  - `PAT_FOR_GITHUB`: personal access token GitHub yang dibenarkan mengubah suai repositori cermin (token sahaja, tanpa JSON)
  - `TOKEN_FOR_GITEA_WIKI` (hanya untuk repositori yang menerbitkan wiki, lihat [panduan menyertakan repositori](Onboarding.ms)): token Gitea yang boleh menulis ke wiki, disimpan sebagai secret organisasi repositori; tiada sandaran kepada `TOKEN_FOR_GITEA`


## Persediaan

Tiada kebergantungan perlu dipasang; aliran kerja hanya menggunakan pustaka standard Python.

1. Klon repositori:
   ```bash
   git clone ssh://git@git.tirsystem.com:10022/TirSystem/github-action.git
   ```
2. Tambah rahsia yang disenaraikan di bawah [Keperluan](#keperluan) ke tetapan repositori dalam Gitea.
3. Konfigurasikan push mirror GitHub dalam tetapan repositori.


## Jalankan

Aliran kerja berjalan secara automatik pada push ke `main` dan mengikut jadual harian. Untuk menjalankannya secara manual, cetuskan **Sync GitHub mirror metadata** melalui `workflow_dispatch` dari tab Actions dalam Gitea.


## Ujian

Fail aliran kerja dan skrip dalam `tools/` disahkan oleh ujian luar talian yang tidak memerlukan akses rangkaian dan tidak memerlukan rahsia:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r tests/requirements.txt
python -m pytest -q tests
```

Semakan yang sama dijalankan pada setiap pull request dan setiap push ke `main` melalui [`validate-workflows.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/validate-workflows.yml). Semakan itu menghurai setiap aliran kerja sebagai YAML, memastikan tiada yang menanam Python, mengkompil skrip dalam `tools/`, memerlukan kebenaran kerja yang jelas, dan menguji penghuraian kelayakan (credentials), penghuraian alamat push mirror serta aliran penyegerakan dan penerbitan terhadap API palsu.

Selepas perubahan pada aliran kerja penyegerakan, cetuskan juga **Sync GitHub mirror metadata** secara manual dalam Gitea dan bandingkan penerangan dan topik pada cermin GitHub.
