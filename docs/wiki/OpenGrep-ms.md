<!-- translation of OpenGrep.md, source sha256 df7e8514b8f7 -->

> Ini ialah terjemahan [`OpenGrep`](OpenGrep). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](OpenGrep) · [Dansk](OpenGrep-da) · **Bahasa Melayu**

# Imbasan keselamatan statik dengan OpenGrep

Cara seorang jurutera perisian membaca dan mengendalikan hasil aliran kerja
scoped `opengrep.yml`. Ia mengimbas repositori dengan OpenGrep dan peraturan
komunitinya, tanpa akaun, dan menunjukkan dapatan pada pull request. Ia tidak
mengubah sebarang fail dan tidak mempunyai rahsia. Keputusan di belakangnya
ialah ADR-0015 dalam repositori ini; bila sesebuah repositori menggunakannya
dinyatakan dalam [peraturan penggunaan](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/adoption-rules.md#opengrep).

## Tiada apa-apa untuk ditambah

Aliran kerja ini scoped: instans menjalankannya dalam setiap repositori
organisasi, pada pull request, pada push ke `main` dan secara manual. Sesebuah
repositori tidak menambah sebarang fail. OpenGrep v1.33.0 ialah satu fail boleh
laku (`opengrep_manylinux_x86`), dimuat turun daripada keluaran GitHub dan
disemak terhadap sha256 yang dikunci; tiada `pip` dan tiada akaun. Hanya runner
Linux x86_64 disokong. OpenGrep tidak mempunyai registri dan tiada pilihan
metrik. Peraturan ialah repositori `opengrep/opengrep-rules`, dikunci pada satu
commit dan diambil dengan git semasa larian: direktori `python`, `bash`, `c`,
`csharp`, `yaml`, `generic`, `dockerfile`, `javascript`, `typescript`,
`terraform`, `go` dan `java`. Satu-satunya hos keluar ialah `github.com`, dan
hanya fail yang dijejaki git diimbas. Tiada kod sumber keluar daripada runner.

## Apa yang menggagalkan larian

| Tahap | Dalam log | Menggagalkan larian |
| --- | --- | --- |
| `ERROR` | `::error file=...,line=...::[finding] rule-id: message` | Ya |
| `WARNING` | `::warning file=...,line=...::` | Tidak |
| `INFO` | `::notice file=...,line=...::` | Tidak |

Ringkasan kerja menyenaraikan sehingga 50 dapatan dengan peraturan dan
tempatnya. Repositori yang tiada fail dijejaki diimbas berakhir hijau dan
mencetak "nothing to scan". Kegagalan alat itu sendiri ialah `[tool]`: muat turun
gagal, cincangan tidak sepadan, peraturan tidak dapat diambil, atau laporan tidak
dapat dibaca; jalankan semula sebelum mencari dapatan.

## Mendiamkan dapatan

Positif palsu didiamkan di tempatnya, dan sebabnya dicatat dalam pull request:

- Pada baris: `# nosemgrep: rule-id` (bentuk komen bagi bahasa itu), dengan id
  peraturan tepat seperti yang dicetak oleh log (id bermula dengan laluan salinan
  peraturan, jadi salinnya daripada log CI, bukan daripada larian setempat).
  OpenGrep mengekalkan sintaks komen Semgrep; disemak pada 2026-10-29: id hanya
  mendiamkan peraturan itu, dan `# nosemgrep` tanpa id mendiamkan setiap
  peraturan pada baris itu.
- Untuk laluan: fail `.semgrepignore` pada akar repositori, dengan corak
  `.gitignore`, untuk kod janaan, kod vendor dan fixture.

Dapatan yang benar dibetulkan, bukan didiamkan. Peraturan ini lama (commit
terakhir pada Januari 2025) dan bising pada dokumentasi, kerana peraturan shell
terpicu oleh contoh kod dalam Markdown; jangkakan positif palsu didiamkan bagi
setiap repositori.

## Percubaan pada repositori ini

Satu larian percubaan mengambil kira-kira 66 saat dan mengimbas 243 fail. Ia
memberi 111 dapatan: 3 `ERROR` dalam `tools/` (dua `dangerous-subprocess-use-audit`
dan satu `use-defused-xml`), 10 `WARNING` dan 98 `INFO`, kebanyakannya peraturan
shell pada contoh kod dalam Markdown. Lima fail mempunyai ralat penghuraian,
yang tidak menggagalkan larian. Pada repositori ini semakan itu akan gagal
sehingga tiga dapatan tersebut dibetulkan atau didiamkan.

## Menandakan semakan sebagai wajib

Menetapkan semakan sebagai wajib dalam perlindungan cabang ialah apa yang
menghalang penggabungan apabila ada dapatan `ERROR`. Ia tetapan perlindungan
cabang, jadi pemilik repositori yang melakukannya. Amaran tidak pernah menghalang.

## Lesen

OpenGrep ialah LGPL-2.1. Repositori peraturan berada di bawah LGPL-2.1 dengan
Commons Clause, yang melarang menjual perisian sebagai perkhidmatan dengan
bayaran, dan README-nya menyatakan peraturan itu bertujuan untuk penyelidikan,
ujian dan penanda aras. Aliran kerja mengambilnya semasa larian dan tidak
menyimpannya dalam sebarang repositori. Penggunaan untuk perkhidmatan, atau
perubahan lesen itu, memerlukan keputusan baharu.
