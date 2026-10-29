<!-- translation of Capabilities.md, source sha256 da8f69e41c49 -->

> Ini ialah terjemahan [`Capabilities`](Capabilities). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Capabilities) · [Dansk](Capabilities-da) · **Bahasa Melayu**

## Keupayaan

Baris yang menyatakan Dilaksanakan atau Panduan telah ditulis wujud hari ini. Selebihnya dirancang dan dijejaki dalam [Pelan Projek](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/docs/project-plan.md), yang juga menerangkan setiap kes guna (use case).

| Keupayaan | Status |
| --- | --- |
| Menyegerakkan metadata repositori (Gitea ke cermin GitHub) | Dilaksanakan dalam `.gitea/scoped_workflows/`, dengan ujian luar talian dan aliran kerja pengesahan |
| Mengkonfigur dan mengesahkan kelayakan (credentials) aliran kerja | Dilaksanakan untuk aliran kerja penyegerakan: semakan awal (preflight) memeriksa kedua-dua token sebelum sebarang perubahan ([panduan](Credentials-ms)) |
| Menyertakan repositori, mengurus runner, mendiagnosis kegagalan | Panduan telah ditulis ([menyertakan repositori](Onboarding-ms), [diagnosis](Troubleshooting-ms)); penghantaran scoped ke repositori keempat-empat organisasi telah disahkan (MIL-002) |
| Menerbitkan wiki repositori daripada `docs/wiki/` melalui aliran kerja yang dipanggil | Dilaksanakan sebagai aliran kerja scoped `.gitea/scoped_workflows/publish-wiki-pages.yml`, dengan ujian luar talian; ia berjalan dalam setiap repositori yang mempunyai folder `docs/wiki/`, dan wiki repositori ini sendiri ada dalam `docs/wiki/` (MIL-008, MIL-009) |
| Semakan kualiti bersama (Python dan shell) | Dilaksanakan sebagai aliran kerja boleh guna semula `.gitea/workflows/quality-checks.yml`, dengan ujian luar talian dan percubaan dalam organisasi kedua; digunakan dalam RepoFoundry ([panduan](QualityChecksPythonShell-ms)) |
| Semakan kualiti bersama (C dan C++, C#) | Dilaksanakan sebagai aliran kerja boleh guna semula `.gitea/workflows/quality-checks-cpp.yml` dan `.gitea/workflows/quality-checks-csharp.yml` dengan versi alat yang tepat dan ujian luar talian; belum digunakan dalam repositori lain (MIL-007) ([panduan C dan C++](QualityChecksCpp-ms), [panduan C#](QualityChecksCSharp-ms)) |
| Metrik kod dan lencana liputan | Dilaksanakan dan diterbitkan dalam 2.1.0 sebagai aliran kerja boleh guna semula `.gitea/workflows/code-metrics.yml` dengan pengira, pembaca Cobertura, pemaparan SVG dan ujian luar talian; dicuba dalam repositori sekali pakai, belum digunakan dalam repositori projek (MIL-010) ([panduan](CodeMetrics-ms)) |
| Imbasan keselamatan statik | Dilaksanakan sebagai aliran kerja scoped `.gitea/scoped_workflows/opengrep.yml` dengan OpenGrep, skrip dan ujian luar talian; belum dijalankan pada instans (MIL-016) ([panduan](OpenGrep-ms)) |
| Pengesahan setiap repositori | Dilaksanakan sebagai aliran kerja scoped `.gitea/scoped_workflows/validate.yml` dengan skrip dan ujian luar talian; belum dijalankan pada instans (MIL-017) ([panduan](Validate-ms)) |
| Penerbitan milestone yang diterima | Dilaksanakan sebagai aliran kerja scoped `.gitea/scoped_workflows/sync-milestones.yml` dengan skrip dan ujian luar talian, menggantikan salinan dalam `.gitea/workflows/`; secret dan framework persendirian dalam larian scoped belum disahkan pada instans (MIL-019) ([panduan](SyncMilestones-ms)) |
| Komen dalam bahasa Inggeris | Dilaksanakan sebagai aliran kerja boleh guna semula `.gitea/workflows/english-comments.yml` dengan pengekstrak komen, pengesan bahasa yang diukur pada korpus (ADR-0012), komen pada pull request dan ujian luar talian; belum dijalankan pada instans atau diwajibkan oleh mana-mana repositori (MIL-013) ([panduan](EnglishComments-ms)) |
| Keluaran berversi dan penerbitan | Proses keluaran, changelog dan panduan naik taraf telah ditakrifkan; aliran kerja keluaran sudah ada dan `v1.0.0` telah dikeluarkan (MIL-004) ([panduan](Upgrading-ms)) |
