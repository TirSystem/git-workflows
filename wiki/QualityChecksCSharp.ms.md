<!-- translation of QualityChecksCSharp.md, source sha256 2baa0d48f712 -->

> Ini ialah terjemahan [`QualityChecksCSharp`](QualityChecksCSharp). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](QualityChecksCSharp) | [Dansk](QualityChecksCSharp.da) | Bahasa Melayu

# Membaca keputusan semakan kualiti C#

Cara seorang jurutera perisian memanggil semakan kualiti bersama untuk C#, membaca larian yang gagal dan menjadikannya lulus. Aliran kerja ini menyemak pemformatan dan membina solution atau projek dengan amaran sebagai ralat, pada .NET SDK versi 10 atau lebih baharu yang tepat, tidak mengubah sebarang fail dan tidak memerlukan secret. Kontraknya ialah ADR-0008 dalam repositori ini.

## Memanggil aliran kerja

```yaml
name: Quality C#

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  quality:
    permissions:
      contents: read
    uses: TirSystem/github-action/.gitea/workflows/quality-checks-csharp.yml@v1
    with:
      project: src/App.sln
```

| Input | Lalai | Maksud |
| --- | --- | --- |
| `working-directory` | `.` | Direktori, relatif kepada akar repositori, yang failnya disemak |
| `project` | kosong | Fail solution atau projek, relatif kepada `working-directory`; kosong menggunakan satu-satunya `*.sln` atau `*.slnx` yang dijejaki, jika tiada maka satu-satunya `*.csproj` yang dijejaki di situ |
| `dotnet-sdk-version` | `10.0.401` | Versi tepat .NET SDK, 10 atau lebih baharu; saluran seperti `10.0`, julat dan versi di bawah 10 ditolak |
| `tools-ref` | `v1` | Tag atau cabang `TirSystem/github-action` tempat skrip `tools/quality-checks-csharp.sh` diambil |

Rujuk aliran kerja pada tag major (`@v1`) atau pada tag tepat, jangan sekali-kali pada `main`. Panggilan pada tag tepat hanya disematkan sepenuhnya apabila `tools-ref` menamakan tag yang sama. Lihat panduan naik taraf. Versi SDK adalah tepat: menaikkan nilai lalai ialah keluaran baharu repositori ini, bukan perubahan senyap.

## Apa yang diperlukan oleh repositori

- Satu solution atau projek yang boleh dibina dengan SDK. Beberapa calon memerlukan input `project`; fail C# tanpa solution atau projek gagal dengan `[configuration]`.
- Rangkaian: `dotnet format` dan `dotnet build` memulihkan pakej NuGet projek dalam larian.
- Peraturan dalam `.editorconfig` (dan penganalisis yang diaktifkan projek, contohnya dengan `AnalysisLevel` dan `EnforceCodeStyleInBuild`) menentukan apa yang dikira sebagai dapatan.

## Apa yang disemak

| Fail | Alat | Apa yang dilaporkan |
| --- | --- | --- |
| solution atau projek | `dotnet format --verify-no-changes` | pemformatan dan gaya yang berbeza daripada `.editorconfig` |
| yang sama | `dotnet build -warnaserror` | amaran pengkompil dan penganalisis, yang menggagalkan binaan |

Fail yang tidak dijejaki tidak disemak. Repositori tanpa fail `*.cs` lulus dengan satu notis. Ujian projek tidak dijalankan.

## Membaca satu larian

1. Buka semakan status pada pull request, kemudian kerja `quality-checks-csharp`.
2. Setiap alat mempunyai kumpulan lognya sendiri. Kedua-duanya dijalankan walaupun yang pertama gagal, jadi satu larian menunjukkan semua dapatan.
3. Satu alat berakhir dengan `PASS <alat>` atau `FAIL <alat>`; baris terakhir larian yang gagal menamakannya: `Quality checks failed: dotnet format --verify-no-changes`.
4. Satu dapatan ditulis oleh alat itu sendiri sebagai `path(line,column): CODE message`.

## Kegagalan biasa dan pembetulan

| Alat | Apa yang ditunjukkan log | Pembetulan |
| --- | --- | --- |
| `dotnet format --verify-no-changes` | `Program.cs(12,5): error WHITESPACE: Fix whitespace formatting` | Jalankan `dotnet format <projek>` dan commit |
| `dotnet build -warnaserror` | `CS8602: Dereference of a possibly null reference` | Betulkan kod (semakan null); jangan tindas amaran tanpa sebab |
| `dotnet build -warnaserror` | `IDE0005: Using directive is unnecessary` | Buang arahan itu |

Untuk mengulangi satu larian pada mesin anda, gunakan SDK yang sama:

```bash
dotnet --version        # 10.0.401
dotnet format src/App.sln --verify-no-changes
dotnet build src/App.sln -warnaserror
```

## Apabila aliran kerja itu sendiri gagal

| Mesej | Punca | Pembetulan |
| --- | --- | --- |
| `[configuration] dotnet-sdk-version '<x>' is not an exact stable version 10 or later` | Saluran, julat, pratonton atau versi di bawah 10 | Berikan versi tepat seperti `10.0.401` |
| `[configuration] working-directory must be a relative path inside the repository.` | Laluan mutlak atau `..` | Gunakan laluan di dalam repositori |
| `[configuration] C# files exist but no solution or project was found` | Repositori mempunyai fail `*.cs` tetapi tiada `*.sln`, `*.slnx` atau `*.csproj` dalam direktori kerja | Tambah satu, atau tetapkan `working-directory` |
| `[configuration] Several solutions or projects were found` | Lebih daripada satu calon | Tetapkan input `project` |
| Langkah pemasangan gagal | `dot.net` atau rangkaian runner tidak dapat dicapai | Jalankan semula kerja; lihat [troubleshooting.md](troubleshooting.md) |
