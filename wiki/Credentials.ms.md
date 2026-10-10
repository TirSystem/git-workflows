<!-- translation of Credentials.md, source sha256 57f66acfdc0a -->

> Ini ialah terjemahan [`Credentials`](Credentials). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Credentials) | [Dansk](Credentials.da) | Bahasa Melayu

# Kelayakan (credentials) aliran kerja

Aliran kerja penyegerakan menggunakan dua rahsia (secret). Beri setiap satu keistimewaan paling minimum yang berfungsi, simpan hanya sebagai secret Gitea, dan tukar apabila seseorang yang mempunyai akses meninggalkan pasukan.

| Secret | Kandungan | Digunakan untuk |
| --- | --- | --- |
| `TOKEN_FOR_GITEA` | Token biasa, rentetan JSON, atau JSON dengan `GITEA_TOKEN` | Membaca repositori (penerangan, topik) dan push mirror-nya |
| `CREDENTIALS_FOR_GITHUB` | Objek JSON dengan `GITHUB_PAT` yang tidak kosong | Mengubah penerangan dan topik cermin GitHub |

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

Format `CREDENTIALS_FOR_GITHUB`:

```json
{"GITHUB_PAT": "<token>"}
```

## Perkara yang disemak oleh aliran kerja sebelum mengubah apa-apa

Aliran kerja menjalankan semakan awal (preflight) dan tidak menulis apa-apa ke GitHub melainkan ia lulus:

1. Kedua-dua secret wujud dan mempunyai bentuk yang dijangka.
2. Gitea menerima token dan repositori kelihatan dengannya.
3. Paling banyak satu push mirror GitHub dikonfigurasi. Jika tiada, larian berakhir dengan jayanya tanpa menyegerakkan dan secret GitHub tidak dibaca.
4. GitHub menerima token untuk repositori cermin **dan** token melaporkan akses pentadbiran padanya.

Apabila berjaya, log menyatakan `Preflight passed: Gitea and GitHub accepted the credentials.` Kegagalan bermula dengan kategori seperti `[credentials]` atau `[permissions]`; lihat [troubleshooting.md](Troubleshooting.ms). Tiada nilai secret yang pernah dicetak.

## Secret untuk menerbitkan wiki

Aliran kerja **Publish wiki** (repositori ini sahaja) menyalin `wiki/` ke wiki Gitea apabila perubahan pada `wiki/` digabungkan ke `main`. Ia menggunakan `TOKEN_FOR_GITEA_WIKI` jika secret itu wujud, dan jika tidak, menggunakan semula `TOKEN_FOR_GITEA`.

| Secret | Kandungan | Digunakan untuk |
| --- | --- | --- |
| `TOKEN_FOR_GITEA_WIKI` (pilihan) | Token biasa, rentetan JSON, atau JSON dengan `GITEA_TOKEN` | Menulis halaman wiki repositori ini |

- Token yang digunakan mesti mempunyai skop `write:repository`, dan penggunanya mesti mempunyai akses tulis kepada repositori ini. Gitea tidak mempunyai skop untuk wiki sahaja.
- `TOKEN_FOR_GITEA` didokumenkan di atas dengan `read:repository` sahaja. Menggunakannya semula untuk wiki bermakna meningkatkan skopnya, yang juga memberi akses tulis kepada penyegerakan metadata. `TOKEN_FOR_GITEA_WIKI` yang berasingan untuk pengguna khusus mengekalkan token penyegerakan sebagai baca sahaja. S05 memutuskan yang mana, dan S03 menyimpan secret.
- Panggilan yang dibuat: `GET /repos/{owner}/{repo}`, `GET /repos/{owner}/{repo}/wiki/pages`, `GET`, `POST` dan `PATCH /repos/{owner}/{repo}/wiki/...` dan, bagi halaman yang tidak lagi wujud dalam `wiki/`, `DELETE /repos/{owner}/{repo}/wiki/page/{name}`.
- Wiki mesti diaktifkan dalam tetapan repositori. Aliran kerja enggan berjalan jika ia tidak diaktifkan.
- Wiki sentiasa sama dengan `wiki/`: halaman yang diedit atau ditambah dalam antara muka web Gitea ditimpa atau dibuang pada penerbitan seterusnya.

## Menukar token

1. Cipta token baharu dengan kebenaran di atas.
2. Gantikan nilai secret dalam tetapan repositori atau organisasi.
3. Jalankan aliran kerja secara manual dan tunggu `Preflight passed`.
4. Batalkan token lama.
