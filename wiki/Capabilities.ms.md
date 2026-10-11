<!-- translation of Capabilities.md, source sha256 a8c03a001880 -->

> Ini ialah terjemahan [`Capabilities`](Capabilities). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Capabilities) | [Dansk](Capabilities.da) | Bahasa Melayu

## Keupayaan

Baris yang menyatakan Dilaksanakan atau Panduan telah ditulis wujud hari ini. Selebihnya dirancang dan dijejaki dalam [Pelan Projek](https://git.tirsystem.com/TirSystem/github-action/src/branch/main/docs/project-plan.md), yang juga menerangkan setiap kes guna (use case).

| Keupayaan | Status |
| --- | --- |
| Menyegerakkan metadata repositori (Gitea ke cermin GitHub) | Dilaksanakan dalam `.gitea/scoped_workflows/`, dengan ujian luar talian dan aliran kerja pengesahan |
| Mengkonfigur dan mengesahkan kelayakan (credentials) aliran kerja | Dilaksanakan untuk aliran kerja penyegerakan: semakan awal (preflight) memeriksa kedua-dua token sebelum sebarang perubahan ([panduan](Credentials.ms)) |
| Menyertakan repositori, mengurus runner, mendiagnosis kegagalan | Panduan telah ditulis ([menyertakan repositori](Onboarding.ms), [diagnosis](Troubleshooting.ms)); penghantaran scoped ke repositori keempat-empat organisasi telah disahkan (MIL-002) |
| Menerbitkan wiki repositori daripada `wiki/` (pilih menyertai, dihantar ke setiap organisasi) | Dilaksanakan dalam `.gitea/scoped_workflows/publish-wiki.yml`, dengan ujian luar talian; satu juruterbang dalam repositori kedua menerbitkan wikinya (MIL-006) |
| Semakan kualiti bersama (Python dan shell) | Dilaksanakan sebagai aliran kerja boleh guna semula `.gitea/workflows/quality-checks.yml`, dengan ujian luar talian dan percubaan dalam organisasi kedua; digunakan dalam RepoFoundry ([panduan](QualityChecksPythonShell.ms)) |
| Keluaran berversi dan penerbitan | Proses keluaran, changelog dan panduan naik taraf telah ditakrifkan; aliran kerja keluaran sudah ada dan `v1.0.0` telah dikeluarkan (MIL-004) ([panduan](Upgrading.ms)) |
