<!-- translation of QualityChecks.md, source sha256 aa9c7296fa52 -->

> Ini ialah terjemahan [`QualityChecks`](QualityChecks). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](QualityChecks) | [Dansk](QualityChecks.da) | Bahasa Melayu

# Membaca keputusan semakan kualiti

Cara seorang jurutera perisian memanggil semakan kualiti bersama, membaca larian yang gagal dan menjadikannya lulus. Aliran kerja ini menjalankan lint dan semakan format ke atas fail Python dan shell sesebuah repositori dengan alat yang disematkan versinya, tidak mengubah sebarang fail dan tidak memerlukan secret. Kontraknya ialah ADR-0005 dalam repositori ini.

## Memanggil aliran kerja

```yaml
name: Quality

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  quality:
    permissions:
      contents: read
    uses: TirSystem/github-action/.gitea/workflows/quality-checks.yml@v1
    with:
      languages: python,shell
```

| Input | Lalai | Maksud |
| --- | --- | --- |
| `languages` | `python,shell` | Senarai bahasa yang disemak, dipisahkan koma |
| `working-directory` | `.` | Direktori, relatif kepada akar repositori, yang failnya disemak |
| `ruff-version` | `0.6.9` | Versi ruff |
| `mypy-version` | `1.11.2` | Versi mypy |
| `shellcheck-py-version` | `0.10.0.1` | Versi pakej shellcheck-py (ShellCheck 0.10.0) |
| `shfmt-py-version` | `3.11.0.2` | Versi pakej shfmt-py (shfmt 3.11.0) |

Rujuk aliran kerja pada tag major (`@v1`) atau pada tag tepat (`@v1.0.0`), jangan sekali-kali pada `main` dan jangan pada cabang pull request: cabang itu dipadam apabila pull request digabungkan dan rujukan itu berhenti berfungsi. Lihat panduan naik taraf untuk apa yang diterima oleh setiap pilihan.

## Perkara yang disemak

| Bahasa | Fail | Alat |
| --- | --- | --- |
| Python | `*.py` yang dijejaki di bawah direktori kerja | `ruff check`, `ruff format --check`, `mypy --strict` |
| Shell | `*.sh` yang dijejaki di bawah direktori kerja | `shellcheck`, `shfmt -d` |

Fail yang tidak dijejaki tidak disemak. Bahasa tanpa fail dilangkau dengan notis dan dikira lulus. Ujian projek tidak dijalankan.

## Membaca satu larian

1. Buka semakan status pada pull request, kemudian kerja `quality-checks`.
2. Setiap alat mempunyai kumpulan lognya sendiri yang dinamakan sempena alat itu. Setiap alat dijalankan walaupun alat sebelumnya gagal, jadi satu larian menunjukkan semua dapatan.
3. Satu alat berakhir dengan `PASS <alat>` atau `FAIL <alat>`. Baris terakhir larian yang gagal menamakan alat yang gagal: `Quality checks failed: ruff check shellcheck`.
4. Satu dapatan ditulis oleh alat itu sendiri sebagai `laluan:baris:lajur: KOD mesej`. Laluan relatif kepada `working-directory`.

## Kegagalan biasa dan pembetulan

| Alat | Apa yang ditunjukkan log | Pembetulan |
| --- | --- | --- |
| `ruff check` | `F401 ... imported but unused` | Buang import itu, atau gunakannya |
| `ruff format --check` | `Would reformat: <fail>` | Jalankan `ruff format <fail>` dan commit |
| `mypy --strict` | `Function is missing a type annotation` | Tambah jenis bagi parameter dan nilai pulangan |
| `shellcheck` | `SC2086 ... Double quote to prevent globbing` | Letakkan pengembangan dalam tanda petikan: `"$1"` |
| `shfmt -d` | perbezaan antara `<fail>.orig` dan `<fail>` | Jalankan `shfmt -w <fail>` dengan pilihan projek dan commit |

Untuk mengulang satu larian pada mesin anda, pasang versi yang sama dan jalankan arahan dalam jadual:

```bash
python3 -m venv .qc
.qc/bin/pip install ruff==0.6.9 mypy==1.11.2 shellcheck-py==0.10.0.1 shfmt-py==3.11.0.2
.qc/bin/ruff check . && .qc/bin/ruff format --check .
```

## Mengkonfigur alat

Aliran kerja tidak menambah sebarang konfigurasi; ia berjalan dari akar repositori, jadi fail projek itu sendiri terpakai:

| Alat | Fail | Contoh |
| --- | --- | --- |
| ruff | `pyproject.toml` | `[tool.ruff]` dengan `line-length = 100` |
| mypy | `pyproject.toml` | `[tool.mypy]` dengan `ignore_missing_imports` bagi setiap modul |
| shellcheck | `.shellcheckrc` | `external-sources=true` dan `source-path=SCRIPTDIR` |
| shfmt | `.editorconfig` | `[*.sh]` dengan `indent_size = 2` dan `switch_case_indent = true` |

shfmt mengikut gaya sesebuah projek hanya melalui `.editorconfig`. Projek shell yang memformat dengan bendera sendiri (contohnya `shfmt -i 2 -ci`) patut menjangka kegagalan format pada larian pertama dan menyatakan bendera itu di sana; pada penerimaan pertama (RepoFoundry) satu baris, `switch_case_indent = true`, sudah mencukupi dan tiada skrip diubah.

## Apabila aliran kerja itu sendiri gagal

| Mesej | Punca | Pembetulan |
| --- | --- | --- |
| `[configuration] Unknown language '<x>'` | `languages` mempunyai nilai selain `python` atau `shell` | Betulkan input |
| `[configuration] working-directory must be a relative path inside the repository.` | Laluan mutlak atau `..` | Gunakan laluan di dalam repositori |
| `[configuration] working-directory '<x>' does not exist.` | Direktori itu tiada dalam repositori | Betulkan input |
| Langkah pemasangan gagal | PyPI atau rangkaian runner tidak dapat dicapai | Jalankan semula kerja itu; lihat [troubleshooting.md](Troubleshooting.ms) |
