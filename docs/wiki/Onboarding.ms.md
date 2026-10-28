<!-- translation of Onboarding.md, source sha256 27aa210a18df -->

> Ini ialah terjemahan [`Onboarding`](Onboarding). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Onboarding) | [Dansk](Onboarding.da) | Bahasa Melayu

# Menyertakan sebuah repositori

Cara seorang profesional DevOps menjadikan repositori TirSystem menggunakan aliran kerja bersama **Sync GitHub mirror metadata**, dan runner yang diperlukannya. Hanya aliran kerja ini yang wujud sekarang; aliran kerja semakan kualiti dan keluaran dirancang (lihat [Pelan Projek](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/docs/project-plan.md)).

## Perkara yang telah disahkan

| Perkara | Status |
| --- | --- |
| Versi Gitea | 1.27.3 |
| `.gitea/scoped_workflows/sync-github-metadata.yml` berjalan dalam repositori ini | Disahkan: larian 16, `workflow_dispatch`, berjaya |
| Aliran kerja yang sama terpakai pada repositori lain secara automatik | Disahkan pada 2026-10-10: ia berjalan, tanpa salinan dalam repositori, dalam repositori `TirSystem`, `TirSystem-BashScript`, `vl-staal` dan `Tirsvad-Udemy-100-days-of-code` (contohnya `TirSystem/sqa-qc-checklists` dan `TirSystem-BashScript/RepoFoundry`). Skrip yang dijalankannya berubah apabila skrip repositori ini berubah. |

Penghantaran adalah automatik, jadi repositori tidak memerlukan salinan aliran kerja. Rahsia (secret) tidak dikongsi antara organisasi: setiap organisasi memerlukan rahsianya sendiri (langkah 3).

## Langkah

1. **Semak prasyarat** dalam repositori: Actions diaktifkan, dan runner dengan label `ubuntu-latest` dan `python3` berada dalam talian (lihat [Runners](#runners)).
2. **Konfigurasikan satu push mirror GitHub** dalam tetapan repositori (Settings, Repository, Mirror settings, Push mirror). Aliran kerja gagal jika terdapat beberapa cermin GitHub. Jika tiada, ia berjaya tanpa menyegerakkan apa-apa.
3. **Tambah dua rahsia (secret)** dalam tetapan repositori (atau organisasi), dengan skop yang tertera dalam [credentials.md](Credentials.ms). Aliran kerja berjalan dalam setiap repositori sesebuah organisasi, jadi simpan rahsia sekali bagi setiap organisasi; repositori dalam organisasi lain tidak melihatnya:
   - `TOKEN_FOR_GITEA_REPO`
   - `PAT_FOR_GITHUB` (token GitHub sahaja)
4. **Hantar aliran kerja:** scoped workflow terpakai pada setiap repositori dalam instans ini, jadi tiada apa yang perlu disalin. Hanya jika penghantaran scoped tidak disediakan, salin `.gitea/scoped_workflows/sync-github-metadata.yml` dari repositori ini ke `.gitea/workflows/` dalam repositori sasaran, sematkan salinan itu pada versi yang telah disemak dan salin semula apabila ia berubah.
5. **Tetapkan penerangan dan topik** pada repositori Gitea, supaya ada sesuatu untuk disegerakkan.
6. **Jalankan sekali secara manual:** Actions, **Sync GitHub mirror metadata**, Run workflow. Log mesti berakhir dengan `Synced description and topics to <owner>/<repo>.` dan repositori GitHub mesti menunjukkan penerangan dan topik yang sama.
7. Jika gagal, gunakan [troubleshooting.md](Troubleshooting.ms).

## Menerbitkan wiki (pilihan)

Aliran kerja scoped **Publish wiki pages** menyalin halaman Markdown dalam `docs/wiki/` ke wiki repositori apabila perubahan pada `docs/wiki/` digabungkan ke `main`. Instans menghantarnya ke semua repositori, jadi tiada apa-apa untuk dipanggil atau disalin; repositori tanpa folder `docs/wiki/` dilangkau. Halaman yang ada dalam wiki tetapi tiada dalam folder dikekalkan. Wiki ada dalam bahasa Inggeris dan bahasa pemilik produk sekurang-kurangnya.

1. Aktifkan wiki dalam tetapan repositori.
2. Tambah halaman Markdown ke `docs/wiki/`. Nama fail ialah nama halaman: `Home.md` ialah halaman utama. Tanda sempang dalam nama ialah ruang dalam nama halaman: `Home-da.md` ialah halaman "Home da", dan pautan kepadanya ialah `[Dansk](Home-da)`.
3. Simpan `TOKEN_FOR_GITEA_WIKI` sebagai secret organisasi repositori, dengan skop yang tertera dalam [credentials.md](Credentials.ms).
4. Gabungkan perubahan ke `main`. Log mesti berakhir dengan `Published <n> page(s) to the wiki of <owner>/<repo>`.

## Runners

| Perkara | Nilai |
| --- | --- |
| Label yang digunakan oleh aliran kerja | `ubuntu-latest` |
| Label yang ditawarkan oleh runner pada instans ini | `ubuntu-latest`, `ubuntu-24.04`, `ubuntu-22.04` |
| Alat yang diperlukan oleh aliran kerja | `python3` (pustaka standard sahaja), HTTPS keluar ke API Gitea dan `api.github.com` |
| Diperlukan untuk `actions/checkout` (digunakan oleh aliran kerja pengesahan) | `git` dan Node.js, biasanya terdapat dalam imej runner |

**Semak bahawa runner yang sesuai berada dalam talian** (memerlukan kebenaran untuk melihat runner):

```bash
curl -s -H "Authorization: token $TOKEN_FOR_GITEA_REPO" \
  https://git.tirsystem.com/api/v1/repos/<owner>/<repo>/actions/runners
```

Bagi runner yang dikongsi oleh seluruh instans, pentadbir menggunakan `/api/v1/admin/actions/runners`. Pada masa penulisan, senarai repositori dan organisasi kosong dan satu runner peringkat instans (`36cd20104923`) berstatus `online`.

**Runner luar talian atau tidak serasi**

| Gejala | Punca yang mungkin | Tindakan |
| --- | --- | --- |
| Larian kekal `waiting` | Tiada runner dalam talian yang mempunyai label dalam `runs-on` | Mulakan runner, atau daftarkan satu dengan label itu |
| Kerja gagal pada permulaan dengan arahan yang tiada | Imej runner tiada `python3`, `git` atau Node.js | Gunakan imej yang mempunyainya |
| Kerja tidak dapat mencapai API | Runner tiada HTTPS keluar | Betulkan tetapan rangkaian atau proksi runner |
