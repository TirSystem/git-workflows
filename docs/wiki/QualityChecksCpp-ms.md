<!-- translation of QualityChecksCpp.md, source sha256 10762f4ef66f -->

> Ini ialah terjemahan [`QualityChecksCpp`](QualityChecksCpp). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](QualityChecksCpp) · [Dansk](QualityChecksCpp-da) · **Bahasa Melayu**

# Membaca keputusan semakan kualiti C dan C++

Cara seorang jurutera perisian memanggil semakan kualiti bersama untuk C dan C++, membaca larian yang gagal dan menjadikannya lulus. Aliran kerja ini menyemak format dan menganalisis secara statik fail C dan C++ sesebuah repositori dengan alat clang pada versi yang tepat, tidak mengubah sebarang fail dan tidak memerlukan secret. Kontraknya ialah ADR-0008 dalam repositori ini.

## Memanggil aliran kerja

```yaml
name: Quality C++

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  quality:
    permissions:
      contents: read
    uses: TirSystem/git-workflows/.gitea/workflows/quality-checks-cpp.yml@v1
    with:
      std: c++20
```

| Input | Lalai | Maksud |
| --- | --- | --- |
| `working-directory` | `.` | Direktori, relatif kepada akar repositori, yang failnya disemak |
| `std` | `c++20` | Piawaian C++ yang diberikan kepada clang-tidy apabila tiada pangkalan data kompilasi, seperti `c++17` atau `gnu++20` |
| `compile-commands-dir` | kosong | Direktori, relatif kepada akar repositori, dengan `compile_commands.json` yang dibina oleh saluran paip anda sebelum panggilan; apabila ditetapkan, clang-tidy menggunakannya dan mengabaikan `std` |
| `clang-format-version` | `23.1.3` | Versi tepat pakej clang-format |
| `clang-tidy-version` | `22.1.8` | Versi tepat pakej clang-tidy |
| `tools-ref` | `v2` | Tag atau cabang `TirSystem/git-workflows` tempat skrip `tools/quality-checks-cpp.sh` diambil |

Rujuk aliran kerja pada tag major (`@v1`) atau pada tag tepat, jangan sekali-kali pada `main`. Panggilan pada tag tepat hanya disematkan sepenuhnya apabila `tools-ref` menamakan tag yang sama. Lihat panduan naik taraf. Versi alat adalah tepat: versi alat yang lebih baharu ialah keluaran baharu repositori ini, bukan perubahan senyap.

## Apa yang diperlukan oleh repositori

- Satu `.clang-format` dalam direktori kerja atau dalam direktori di atasnya, sehingga akar repositori. Tanpanya larian gagal dengan `[configuration]` dan tiada alat dijalankan.
- Pilihan: satu `.clang-tidy` dengan semakan projek (contohnya C++ Core Guidelines). Tanpanya aliran kerja menjalankan diagnostik pengkompil dan penganalisis statik (`clang-diagnostic-*` dan `clang-analyzer-*`), kerana clang-tidy sendiri tidak mengaktifkan sebarang semakan tanpa konfigurasi.
- Untuk semakan statik yang tepat, satu pangkalan data kompilasi: bina dahulu (contohnya `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`) dan berikan `compile-commands-dir: build`. Aliran kerja tidak membina projek anda.

## Apa yang disemak

| Fail | Alat | Apa yang dilaporkan |
| --- | --- | --- |
| `*.c`, `*.cc`, `*.cpp`, `*.cxx`, `*.h`, `*.hh`, `*.hpp`, `*.hxx` yang dijejaki | `clang-format --dry-run -Werror` | pemformatan yang berbeza daripada `.clang-format` |
| fail yang sama | `clang-tidy` | dapatan semakan dalam `.clang-tidy` (atau `clang-diagnostic-*` dan `clang-analyzer-*` tanpanya); fail `*.c` disemak sebagai C17, fail lain sebagai piawaian C++ dalam `std`; setiap dapatan ialah ralat (`--warnings-as-errors=*`), jadi amaran menggagalkan larian |

Fail yang tidak dijejaki tidak disemak. Repositori tanpa fail ini lulus dengan satu notis. Tiada `cppcheck`: hanya versi lama tersedia sebagai pakej, dan alat lama tidak dijalankan (ADR-0008).

## Membaca satu larian

1. Buka semakan status pada pull request, kemudian kerja `quality-checks-cpp`.
2. Setiap alat mempunyai kumpulan lognya sendiri. Setiap alat dijalankan walaupun yang terdahulu gagal, jadi satu larian menunjukkan semua dapatan.
3. Satu alat berakhir dengan `PASS <alat>` atau `FAIL <alat>`; baris terakhir larian yang gagal menamakannya: `Quality checks failed: clang-format`.
4. Satu dapatan ditulis oleh alat itu sendiri sebagai `path:line:column: message`. `clang-format` menulis laluan relatif kepada `working-directory`; `clang-tidy` menulis laluan mutlak dalam ruang kerja runner (`/workspace/<owner>/<repo>/main.cpp:5:18`).

## Kegagalan biasa dan pembetulan

| Alat | Apa yang ditunjukkan log | Pembetulan |
| --- | --- | --- |
| `clang-format` | `code should be clang-formatted [-Wclang-format-violations]` | Jalankan `clang-format -i <fail>` dengan versi yang sama dan commit |
| `clang-tidy` | `warning: ... [modernize-use-nullptr]` | Betulkan kod, atau matikan semakan itu dalam `.clang-tidy` dengan sebab |
| `clang-tidy` | `error: 'x.h' file not found` | Bina pangkalan data kompilasi dan tetapkan `compile-commands-dir`, atau tambah laluan include kepadanya |

Untuk mengulangi satu larian pada mesin anda, pasang versi yang sama:

```bash
python3 -m venv .qc
.qc/bin/pip install clang-format==23.1.3 clang-tidy==22.1.8
git ls-files '*.cpp' '*.hpp' | xargs .qc/bin/clang-format --dry-run -Werror
```

## Apabila aliran kerja itu sendiri gagal

| Mesej | Punca | Pembetulan |
| --- | --- | --- |
| `[configuration] std '<x>' is not a C++ standard` | `std` bukan seperti `c++20` atau `gnu++20` | Betulkan input |
| `[configuration] ... is not an exact version` | Versi alat ialah julat, saluran atau kosong | Berikan versi tepat seperti `23.1.3` |
| `[configuration] working-directory must be a relative path inside the repository.` | Laluan mutlak atau `..` | Gunakan laluan di dalam repositori |
| `[configuration] No .clang-format found` | Projek tiada fail gaya | Tambah `.clang-format` |
| `[configuration] compile-commands-dir '<x>' has no compile_commands.json` | Pangkalan data tidak dibina sebelum panggilan | Bina dalam langkah terdahulu kerja itu atau dalam kerja yang menjadi tanggungannya |
| Langkah pemasangan gagal | PyPI atau rangkaian runner tidak dapat dicapai | Jalankan semula kerja; lihat [troubleshooting.md](troubleshooting.md) |
