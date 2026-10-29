<!-- translation of EnglishComments.md, source sha256 729ac76dcb58 -->

> Ini ialah terjemahan [`EnglishComments`](EnglishComments). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](EnglishComments) · [Dansk](EnglishComments-da) · **Bahasa Melayu**

# Memastikan komen kod sumber dalam bahasa Inggeris

Cara seorang jurutera perisian memanggil aliran kerja bersama yang menyemak bahawa
komen dan docstring sesuatu pull request ditulis dalam bahasa Inggeris. Aliran
kerja menggagalkan larian apabila ada yang bukan bahasa Inggeris, dan menulis satu
komen pada pull request yang menyebut penulisnya. Ia tidak mengubah sebarang fail
dan tidak menghantar teks sumber keluar daripada instans. Keputusan di
belakangnya ialah ADR-0012 dalam repositori ini.

## Memanggil aliran kerja

```yaml
name: English comments

on:
  pull_request:

jobs:
  english-comments:
    uses: TirSystem/git-workflows/.gitea/workflows/english-comments.yml@v2
    with:
      exclude: "docs/generated/**"
      allowed-words-file: .english-comments-allowed-words
```

| Input | Lalai | Maksud |
| --- | --- | --- |
| `scope` | `changed` | `changed` menyemak komen pada baris yang ditambah oleh pull request; `all` menyemak setiap fail yang dijejaki |
| `exclude` | | Senarai corak nama fail atau laluan yang dipisahkan koma dan tidak disemak (`*` dan `**` ialah kad liar) |
| `allowed-words-file` | | Fail dalam repositori dengan perkataan yang tidak pernah dinilai, satu pada setiap baris; `#` memulakan komen |
| `threshold` | `0.6` | Kebarangkalian, melebihi 0 dan paling banyak 1, yang mulai daripadanya sesuatu komen dianggap bukan bahasa Inggeris |
| `min-words` | `3` | Komen dengan perkataan yang lebih sedikit tidak dinilai |
| `langid-version`, `numpy-version` | `1.1.6`, `2.1.3` | Pakej tetap yang diperlukan oleh pengesan |
| `tools-ref` | major semasa | Tag repositori ini yang skripnya dijalankan; tetapkan bersama aliran kerja |

Secret pilihan `REPORT_TOKEN` ialah token Gitea yang boleh memberi komen pada pull
request. Tanpanya, aliran kerja menggunakan token larian itu sendiri, jadi komen
ditulis oleh bot Actions. Pull request daripada fork mempunyai token baca sahaja:
semakan masih menggagalkan larian, tetapi tiada komen ditulis.

## Apa yang disemak

Komen dan docstring dalam fail bahasa yang dikenali oleh pengira kod
([metrik kod](CodeMetrics)): Python, shell, PowerShell, C, C++, C#, Java,
JavaScript, TypeScript, Go, Rust dan SQL. String dan kod tidak dibaca. Baris komen
yang berturutan membentuk satu blok. Setiap baris dalam blok dinilai secara berasingan (sekurang-kurangnya
empat perkataan dan kebarangkalian sekurang-kurangnya 0.7), jadi baris bahasa Inggeris tidak dapat menyembunyikan
baris bahasa Denmark di sebelahnya; apabila tiada baris ditandakan, blok dinilai secara keseluruhan
(sekurang-kurangnya `min-words` perkataan dan `threshold`), supaya ayat yang dipecahkan kepada baris pendek tidak terlepas.

Sebelum sesuatu blok dinilai, segala yang bukan perkataan dibuang: laluan, URL,
pilihan (`--output`), nama fail, pengecam (`snake_case`, `camelCase`), nombor,
akronim dan pemalar (`JSON`), label di permulaan seperti `Usage:`, dan perkataan
dalam fail perkataan yang dibenarkan. Blok yang tinggal kurang daripada
`min-words` perkataan tidak dinilai, jadi komen pendek lulus. Komen yang
mengkonfigurasi alat (`noqa`, `type:`, `pragma`, `shellcheck`) tidak dibaca.

## Apabila semakan gagal

Larian gagal, setiap penemuan dipaparkan sebagai anotasi (`::error file=...,line=...`)
dan dalam log sebagai `file:line: looks Danish (0.93): "the comment"`, dan satu
komen pada pull request menyenaraikannya serta menyebut penulisnya. Larian baharu
mengemas kini komen itu; apabila pull request lulus, komen ditandakan selesai dan
tidak lagi menyebut sesiapa.

Betulkannya dengan menulis semula komen dalam bahasa Inggeris. Untuk petikan atau
nama yang bukan bahasa Inggeris, sama ada letakkan `english-comments: ignore`
dalam komen (ia melangkau seluruh blok komen tempat ia berada), atau tambahkan
perkataan itu ke dalam fail perkataan yang dibenarkan.

## Menyekat penggabungan

Larian yang gagal tidak menyekat penggabungan dengan sendirinya. Dalam
perlindungan cabang bagi cabang sasaran, tandakan semakan sebagai wajib: jalankan
aliran kerja sekali pada sebuah pull request dan pilih entrinya dalam senarai
semakan status (nama tepatnya dibentuk daripada aliran kerja pemanggil, kerjanya
dan peristiwa). Menetapkan perlindungan cabang ialah tindakan pemilik repositori;
aliran kerja tidak mengubahnya.

## Sejauh mana ia tepat

Pengesan ialah `langid`, terhad kepada bahasa Inggeris, Denmark, Norway, Sweden,
Jerman, Perancis, Melayu, Indonesia dan Belanda. Pada korpus repositori, ia
menandakan tiada satu pun daripada 300 komen bahasa Inggeris, 44 daripada 45
komen bahasa Denmark dan 41 daripada 45 komen bahasa Melayu, serta kesemua 48
komen bahasa Jerman, Sweden, Norway dan Perancis (ADR-0012). Batasannya:

- komen satu atau dua perkataan, atau yang kebanyakannya nama, tidak dinilai;
- komen dalam bahasa Inggeris yang lemah lulus, dan komen yang mencampurkan istilah
  teknikal bahasa Inggeris dengan beberapa perkataan Denmark atau Melayu boleh lulus;
- komen bahasa Denmark dan Melayu dalam korpus ditulis untuk ujian, bukan dikumpulkan
  daripada kod sebenar, jadi kod sebenar akan menunjukkan kesilapan lain. Laporkan
  komen yang terlepas atau penemuan palsu bersama komennya, dan ia akan masuk ke
  dalam korpus.

## Diagnosis

| Mesej | Punca |
| --- | --- |
| `[configuration] give --base` | Aliran kerja dimulakan oleh peristiwa yang bukan pull request dengan `scope: changed`; panggil pada `pull_request` atau gunakan `scope: all` |
| `[configuration] git diff failed` | Cabang asas tiada dalam checkout; aliran kerja mengambil seluruh sejarah, jadi semak bahawa pull request mempunyai cabang sasaran |
| `[configuration] langid is not installed` | Langkah pemasangan gagal; semak versi yang ditetapkan |
| `[permissions] ... may not comment on pull requests` | Token tidak boleh memberi komen; berikan `REPORT_TOKEN` akses tulis kepada isu dan pull request |
| Penemuan yang bukan penemuan | Tambahkan perkataan ke dalam fail perkataan yang dibenarkan, atau `english-comments: ignore` pada komen |
