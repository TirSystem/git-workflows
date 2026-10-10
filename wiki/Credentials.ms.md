<!-- translation of Credentials.md, source sha256 2660f2095b78 -->

> Ini ialah terjemahan [`Credentials`](Credentials). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Credentials) | [Dansk](Credentials.da) | Bahasa Melayu

# Kelayakan (credentials) aliran kerja

Aliran kerja penyegerakan menggunakan dua rahsia (secret). Beri setiap satu keistimewaan paling minimum yang berfungsi, simpan hanya sebagai secret Gitea, dan tukar apabila seseorang yang mempunyai akses meninggalkan pasukan.

| Secret | Kandungan | Digunakan untuk |
| --- | --- | --- |
| `TOKEN_FOR_GITEA` | Token Gitea, tiada yang lain | Membaca repositori (penerangan, topik) dan push mirror-nya |
| `PAT_FOR_GITHUB` | Token GitHub, tiada yang lain | Mengubah penerangan dan topik cermin GitHub |

## Kebenaran minimum

Ini datang daripada dokumentasi Gitea dan GitHub serta panggilan API yang dibuat oleh aliran kerja. Ia **belum disahkan dengan token minimum pada instans ini**; S05 harus mengesahkannya apabila token dicipta.

**Token Gitea** (personal access token seorang pengguna, bukan deploy key; deploy key tidak berfungsi untuk REST API):

- skop `read:repository`
- pengguna mesti dibenarkan membaca push mirror repositori, yang dihadkan oleh Gitea kepada pentadbir repositori

Panggilan yang dibuat: `GET /repos/{owner}/{repo}` dan `GET /repos/{owner}/{repo}/push_mirrors`.

**Token GitHub** (fine-grained personal access token):

- Resource owner: pemilik repositori cermin
- Repository access: hanya repositori cermin
- Repository permission: **Administration: Read and write** (tiada kebenaran lain)
- Tetapkan tarikh tamat tempoh

Panggilan yang dibuat: `GET /repos/{owner}/{repo}`, `PATCH /repos/{owner}/{repo}` (penerangan) dan `PUT /repos/{owner}/{repo}/topics`.

Format `PAT_FOR_GITHUB`: hanya rentetan token (contohnya `github_pat_...`) sebagai teks biasa. Aliran kerja hanya menyemak bahawa ia tidak kosong; GitHub menolak nilai yang salah (HTTP 401).

## Perkara yang disemak oleh aliran kerja sebelum mengubah apa-apa

Aliran kerja menjalankan semakan awal (preflight) dan tidak menulis apa-apa ke GitHub melainkan ia lulus:

1. Kedua-dua secret wujud dan mempunyai bentuk yang dijangka.
2. Gitea menerima token dan repositori kelihatan dengannya.
3. Paling banyak satu push mirror GitHub dikonfigurasi. Jika tiada, larian berakhir dengan jayanya tanpa menyegerakkan dan secret GitHub tidak dibaca.
4. GitHub menerima token untuk repositori cermin **dan** token melaporkan akses pentadbiran padanya.

Apabila berjaya, log menyatakan `Preflight passed: Gitea and GitHub accepted the credentials.` Kegagalan bermula dengan kategori seperti `[credentials]` atau `[permissions]`; lihat [troubleshooting.md](Troubleshooting.ms). Tiada nilai secret yang pernah dicetak.

## Secret untuk menerbitkan wiki

Aliran kerja **Publish wiki** menyalin `wiki/` ke wiki Gitea bagi repositori yang telah memilih menyertainya dengan `wiki/.publish` (lihat [onboarding.md](Onboarding.ms)). Ia menggunakan secret sendiri, supaya token penyegerakan metadata kekal baca sahaja.

| Secret | Kandungan | Digunakan untuk |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_WIKI` | Token Gitea, tiada yang lain | Menulis halaman wiki bagi repositori dalam organisasi yang memilih menyertainya |

- Simpan sebagai secret organisasi bagi setiap repositori yang menerbitkan. Tiada sandaran kepada `TOKEN_FOR_GITEA`: repositori yang telah memilih menyertainya dan tidak mempunyai secret itu gagal dengan ralat konfigurasi, dan repositori yang tidak memilih tidak memerlukannya.
- Token mesti mempunyai skop `write:repository`, dan penggunanya mesti mempunyai akses tulis kepada repositori. Gitea tidak mempunyai skop untuk wiki sahaja, jadi cipta token untuk pengguna khusus. S05 meluluskan skop dan S03 menyimpan secret.
- Panggilan yang dibuat: `GET /repos/{owner}/{repo}`, `GET /repos/{owner}/{repo}/wiki/pages`, `GET`, `POST` dan `PATCH /repos/{owner}/{repo}/wiki/...` dan, bagi halaman yang tidak lagi wujud dalam `wiki/`, `DELETE /repos/{owner}/{repo}/wiki/page/{name}`.
- Wiki mesti diaktifkan dalam tetapan repositori. Aliran kerja enggan berjalan jika ia tidak diaktifkan.
- Halaman yang ada dalam `wiki/` sentiasa ditimpa daripadanya, jadi perubahan yang dibuat dalam antara muka web Gitea hilang pada penerbitan seterusnya. Halaman yang hanya ada dalam wiki dibuang hanya apabila `wiki/.publish` mengandungi perkataan `prune`.

## Menukar token

1. Cipta token baharu dengan kebenaran di atas.
2. Gantikan nilai secret dalam tetapan repositori atau organisasi.
3. Jalankan aliran kerja secara manual dan tunggu `Preflight passed`.
4. Batalkan token lama.
