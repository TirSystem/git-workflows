<!-- translation of Home.md, source sha256 758940401ac1 -->

> Ini ialah terjemahan [`Home`](Home). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Home) | [Dansk](Home.da) | Bahasa Melayu

# TirSystem GitHub Actions

Koleksi aliran kerja (workflow) Gitea Actions yang boleh digunakan semula untuk profesional DevOps dan jurutera perisian yang mengusahakan projek TirSystem.


## Gambaran keseluruhan

Repositori ini ialah koleksi pusat bagi automasi yang boleh digunakan semula untuk repositori TirSystem. Repositori utama berada di `git.tirsystem.com` (Gitea) dan dicerminkan dengan push ke GitHub.

Buat masa ini ia mengandungi aliran kerja Gitea [`sync-github-metadata.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/scoped_workflows/sync-github-metadata.yml), yang menyalin penerangan dan topik repositori dari Gitea ke cermin GitHub pada setiap push ke `main`, pada pencetusan manual dan setiap hari pada 03:17 UTC.


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

Fail aliran kerja dan kod Python yang tertanam di dalamnya disahkan oleh ujian luar talian yang tidak memerlukan akses rangkaian dan tidak memerlukan rahsia:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r tests/requirements.txt
python -m pytest -q tests
```

Semakan yang sama dijalankan pada setiap pull request dan setiap push ke `main` melalui [`validate-workflows.yml`](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/.gitea/workflows/validate-workflows.yml). Semakan itu menghurai setiap aliran kerja sebagai YAML, mengkompil Python yang tertanam, memerlukan kebenaran kerja yang jelas, dan menguji penghuraian kelayakan (credentials), penghuraian alamat push mirror dan aliran penyegerakan terhadap API palsu.

Selepas perubahan pada aliran kerja penyegerakan, cetuskan juga **Sync GitHub mirror metadata** secara manual dalam Gitea dan bandingkan penerangan dan topik pada cermin GitHub.
