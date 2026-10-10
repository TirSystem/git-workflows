<!-- translation of Troubleshooting.md, source sha256 e8a34cbe7e93 -->

> Ini ialah terjemahan [`Troubleshooting`](Troubleshooting). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Troubleshooting) | [Dansk](Troubleshooting.da) | Bahasa Melayu

# Mendiagnosis larian yang gagal

Buka larian dalam Gitea (Actions) dan baca baris terakhir langkah yang gagal. Setiap kegagalan daripada skrip penyegerakan ditulis sebagai

```
ERROR: [<category>] <message>
```

Kategori menunjukkan di mana perlu dilihat. Kegagalan di luar skrip (kerja tidak pernah bermula, atau berhenti sebelum langkah itu) ialah masalah **runner**.

| Kategori | Maksud | Perkara pertama yang disemak |
| --- | --- | --- |
| `configuration` | Secret atau tetapan repositori tiada atau tidak betul bentuknya | Nama dan format secret, penyediaan push mirror |
| `credentials` | Satu perkhidmatan menolak token (HTTP 401) | Token tamat tempoh, dibatalkan atau tersalah taip |
| `permissions` | Token sah tetapi tidak dibenarkan (HTTP 403, atau tiada akses pentadbiran GitHub) | Skop token dan akses repositori |
| `api` | Ralat HTTP lain, atau perkhidmatan tidak dapat dicapai | Status perkhidmatan, rangkaian runner |
| runner | Tiada baris `ERROR:`; larian menunggu, atau kerja gagal sebelum skrip | Runner dalam talian, label, alat |

## Mesej dan pembetulan

| Mesej (permulaan) | Kategori | Punca dan pembetulan |
| --- | --- | --- |
| `PAT_FOR_GITHUB is missing or empty.` | configuration | Tambah secret |
| `TOKEN_FOR_GITEA is missing or empty.` | configuration | Tambah secret |
| `Could not determine the Gitea source repository.` | configuration | Larian tiada nama repositori; laporkan sebagai kecacatan |
| `Expected at most one GitHub push mirror ... found N` | configuration | Kekalkan satu push mirror GitHub |
| `TOKEN_FOR_GITEA_WIKI is missing or empty.` | configuration | Penerbitan wiki sahaja: repositori telah memilih menyertainya dengan `wiki/.publish` tetapi organisasinya tiada secret itu; simpannya (lihat [credentials.md](Credentials.ms)) |
| `wiki/.publish may only be empty or contain the word 'prune'.` | configuration | Penerbitan wiki sahaja: biarkan penanda kosong, atau letakkan hanya perkataan `prune` di dalamnya |
| `... HTTP 403 ...` semasa menerbitkan wiki | permissions | Penerbitan wiki sahaja: token memerlukan `write:repository` dan akses tulis kepada repositori ini |
| `The wiki is not enabled on <repo>` | configuration | Penerbitan wiki sahaja: aktifkan wiki dalam tetapan repositori |
| `The wiki source directory ... has no Markdown pages` | configuration | Penerbitan wiki sahaja: `wiki/` kosong atau tiada; tiada apa-apa diubah |
| `Could not determine the GitHub owner and repository ...` | configuration | Alamat cermin mesti kelihatan seperti `https://github.com/<owner>/<repo>.git` |
| `Gitea API request failed with HTTP 401` | credentials | Cipta token Gitea baharu dan kemas kini `TOKEN_FOR_GITEA` |
| `GitHub API request failed with HTTP 401` | credentials | Cipta token GitHub baharu dan kemas kini `PAT_FOR_GITHUB`; nilai mesti token sahaja (tiada nama, tanda petikan atau JSON) |
| `... HTTP 403 ...` (Gitea) | permissions | Token memerlukan `read:repository`, dan penggunanya mesti pentadbir repositori |
| `... HTTP 403 ...` (GitHub) | permissions | Token memerlukan Administration read and write pada repositori cermin |
| `The GitHub token cannot administer <repo>` | permissions | Sama seperti di atas; token boleh membaca repositori tetapi tidak boleh mengeditnya |
| `... HTTP 404 ...` | configuration | Repositori tidak ditemui, atau token tidak dapat melihatnya; semak alamat cermin dan akses repositori token |
| `... HTTP 5xx ...` | api | Masalah perkhidmatan; jalankan semula kemudian |
| `... API is unreachable ...` | api | Masalah rangkaian, DNS atau proksi pada runner |

## Bukan satu ralat

`No GitHub push mirror configured for <repo>; nothing to sync.` Larian berjaya. Tidak semua repositori Gitea mempunyai cermin GitHub, jadi ini dijangka bagi repositori tersebut. Jika repositori itu sepatutnya mempunyainya, tambahkannya dalam tetapan repositori.

`WARNING: Gitea returned an invalid push mirror list; GitHub metadata was not synced.` Larian berjaya tetapi tiada apa-apa disegerakkan. Semak bahawa versi Gitea menyokong API push mirror dan jalankan semula.

`No wiki/.publish marker in <owner>/<repo>; wiki publishing is not enabled for this repository.` Larian Publish wiki berjaya dan tidak menulis apa-apa. Repositori belum memilih menyertainya; tambah `wiki/.publish` jika ia sepatutnya menerbitkan.

`<n> page(s) are in the wiki but not in wiki/ and were kept; put the word 'prune' in wiki/.publish to delete them.` Larian berjaya. Halaman yang hanya ada dalam wiki dibiarkan melainkan penanda mengandungi `prune`.

## Masalah runner

Lihat bahagian [Runners](Onboarding.ms#runners). Ringkasnya: jika larian kekal `waiting`, tiada runner dalam talian yang mempunyai label itu; jika kerja gagal sebelum skrip, imej runner tiada satu alat.

## Menjalankan semula

Gunakan **Run workflow** (`workflow_dispatch`) selepas puncanya dibetulkan. Penyegerakan selamat diulang: ia menimpa penerangan dan topik GitHub dengan nilai daripada Gitea.
