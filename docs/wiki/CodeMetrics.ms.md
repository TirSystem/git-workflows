<!-- translation of CodeMetrics.md, source sha256 edfcb7cf99c9 -->

> Ini ialah terjemahan [`CodeMetrics`](CodeMetrics). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](CodeMetrics) | [Dansk](CodeMetrics.da) | Bahasa Melayu

# Menunjukkan metrik kod dan lencana liputan

Cara seorang jurutera perisian memanggil aliran kerja metrik kod bersama dan menunjukkan tiga lencananya (fail kod, baris kod dan liputan) dalam README. Aliran kerja ini mengira kod repositori, membaca laporan liputan yang dibekalkan oleh pemanggil dan melakukan commit tiga fail SVG ke cabang `badges`. Ia tidak menjalankan sebarang ujian dan tidak memerlukan secret. Kontraknya ialah ADR-0010 dalam repositori ini.

## Memanggil aliran kerja

Aliran kerja tidak dapat melihat fail daripada kerja ujian anda, jadi ujian dijalankan dalam kerja anda sendiri, memuat naik laporan Cobertura XML sebagai artifak, dan kerja metrik dijalankan selepasnya:

```yaml
name: Code metrics

on:
  push:
    branches: [ main ]

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4.2.2
      - run: python3 -m pip install pytest pytest-cov && python3 -m pytest --cov --cov-report=xml
      - uses: actions/upload-artifact@v4.6.2
        with:
          name: coverage
          path: coverage.xml

  metrics:
    needs: tests
    permissions:
      contents: write
    uses: TirSystem/github-action/.gitea/workflows/code-metrics.yml@v1
    with:
      coverage-artifact: coverage
      coverage-report: coverage.xml
```

| Input | Lalai | Maksud |
| --- | --- | --- |
| `working-directory` | `.` | Direktori, relatif kepada akar repositori, yang kodnya dikira |
| `exclude` | kosong | Senarai corak fail dan direktori yang tidak dikira, dipisahkan koma, sebagai tambahan kepada pengecualian lalai; corak tanpa `/` sepadan dengan nama di mana-mana, corak dengan `/` sepadan dengan laluan di bawah `working-directory` |
| `coverage-report` | kosong | Laporan Cobertura XML: fail dalam artifak apabila `coverage-artifact` ditetapkan, jika tidak laluan dalam repositori; kosong bermakna tiada lencana liputan |
| `coverage-artifact` | kosong | Nama artifak, dimuat naik oleh kerja yang lebih awal dalam larian yang sama, yang memegang laporan |
| `coverage-warn` | `60` | Liputan dalam peratus di bawahnya lencana berwarna merah |
| `coverage-good` | `80` | Liputan dalam peratus yang bermulanya lencana berwarna hijau; di antaranya kuning |
| `badges-branch` | `badges` | Cabang yang memegang fail lencana; ia dicipta jika tidak wujud |
| `tools-ref` | `v1` | Tag atau cabang `TirSystem/github-action` tempat skrip dalam `tools/` diambil |

Rujuk aliran kerja pada tag major (`@v1`) atau pada tag tepat, jangan sekali-kali pada `main`. Panggilan pada tag tepat hanya tersemat sepenuhnya apabila `tools-ref` menamakan tag yang sama. Lihat panduan menaik taraf. Mulakan aliran kerja pada push ke cabang lalai anda sahaja: commit lencana membawa `[skip ci]` dan dibuat dengan token larian, yang tidak memulakan larian lain, tetapi pencetus pada setiap cabang akan menulis satu commit bagi setiap cabang.

## Apa yang dikira

- Fail kod ialah fail teks dengan sambungan bagi bahasa yang disokong: Python, shell, PowerShell, C, C++, C#, Java, JavaScript, TypeScript, Go, Rust dan SQL. Markdown, YAML, JSON, XML, HTML dan CSS bukan fail kod.
- Setiap baris tepat satu daripada: kosong (hanya ruang putih), komen (hanya teks komen) atau kod (selebihnya, termasuk baris dengan kod dan komen di hujung). Lencana hanya menunjukkan baris kod.
- Penanda komen dalam rentetan bukan komen, dan docstring Python ialah rentetan jadi dikira sebagai kod.
- Direktori yang bermula dengan titik, serta `node_modules`, `vendor`, `third_party`, `dist`, `build`, `out`, `bin`, `obj`, `target`, `venv`, `__pycache__` dan `shared-scripts` tidak dikira. Kod yang dijana dikecualikan dengan `exclude`.
- Rentetan mentah dan verbatim yang berbeza daripada rentetan biasa (Rust `r#"..."#`, C# `@"..."`, rentetan mentah C++) boleh dikira dengan salah. Angka sedikit berbeza daripada alat lain; peraturannya sama pada setiap larian.

## Lencana liputan

Laporan ialah fail Cobertura XML, yang ditulis oleh `coverage.py` (`coverage xml`), `gcovr` (`--cobertura`) dan `coverlet` (format `cobertura`). Lencana menunjukkan `lines-covered` berbanding `lines-valid`, dibundarkan kepada peratus penuh, dan warnanya mengikut dua ambang. Laporan yang tidak wujud, bukan Cobertura XML yang terbentuk dengan baik atau tidak mempunyai baris sah menyebabkan larian gagal dengan nama fail disebut; lencana liputan tidak pernah ditulis sebagai `0%` bagi laporan yang rosak. Tanpa `coverage-report` larian lulus dengan notis dan tanpa lencana liputan.

## Menunjukkan lencana

Tambahkan imej ke README dengan URL mentah cabang:

```markdown
![code files](https://git.tirsystem.com/OWNER/REPO/raw/branch/badges/code-files.svg)
![lines of code](https://git.tirsystem.com/OWNER/REPO/raw/branch/badges/code-lines.svg)
![coverage](https://git.tirsystem.com/OWNER/REPO/raw/branch/badges/coverage.svg)
```

Pada cermin GitHub gunakan `https://raw.githubusercontent.com/OWNER/REPO/badges/code-files.svg`; cermin push menyalin cabang itu. Cabang `badges` juga memegang `code-metrics.json` dengan angka bagi setiap bahasa. Instans menyimpan fail mentah dalam cache sehingga enam jam, jadi lencana yang berubah mungkin menunjukkan angka lama seketika di sana; cermin menyimpannya lima minit. Repositori persendirian tidak menunjukkan lencana kepada pembaca yang belum log masuk.

## Apabila aliran kerja gagal

| Mesej | Punca | Pembetulan |
| --- | --- | --- |
| `[configuration] working-directory must be a relative path inside the repository.` | Laluan mutlak atau `..` | Gunakan laluan di dalam repositori |
| `[configuration] coverage-report '<x>' does not exist.` | Laporan tidak dihasilkan, atau nama artifak atau laluan salah | Semak kerja ujian dan nama artifak; laluan berada di dalam artifak |
| `[configuration] coverage-report '<x>' is not well-formed XML` atau `is not a Cobertura report` | Fail itu berformat lain | Tulis Cobertura XML (`coverage xml`, `gcovr --cobertura`) |
| `[configuration] coverage-report '<x>' has no valid lines.` | Ujian tidak menjalankan kod yang diukur | Semak konfigurasi liputan |
| `[configuration] coverage-artifact '<x>' needs coverage-report` | Artifak dinamakan tetapi bukan fail di dalamnya | Tetapkan `coverage-report` |
| `[configuration] coverage-warn ... is above coverage-good` atau `is not a number from 0 to 100` | Ambang tidak sah | Betulkan input |
| `[configuration] badges-branch '<x>' must not be a default branch` atau `holds files that are not badge files` | Nama cabang ialah `main`, `master` atau cabang dengan kandungan lain | Gunakan cabang yang hanya memegang lencana |
| `the push to '<x>' failed twice` | Larian lain menulis cabang pada masa yang sama, atau token tidak boleh menulis | Jalankan semula; semak bahawa kerja mempunyai `contents: write` |
| Langkah muat turun gagal | Artifak tidak wujud dalam larian ini, atau kerja tidak berjalan selepas kerja ujian | Tambah `needs:` dan semak nama artifak |
