<!-- translation of Validate.md, source sha256 d6ec05a17464 -->

> Ini ialah terjemahan [`Validate`](Validate). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Validate) · [Dansk](Validate-da) · **Bahasa Melayu**

# Pengesahan fail aliran kerja dan skrip shell

Cara seorang jurutera perisian membaca dan mengendalikan hasil aliran kerja
scoped `validate.yml`. Ia menyemak fail aliran kerja dan skrip shell yang
dijejaki dalam repositori terhadap kriteria senarai semak aliran kerja
(`QC-WF-001`) yang boleh diputuskan oleh skrip, dan menjalankan `shellcheck`
dan `shfmt` pada skrip shell. Ia tidak mengubah sebarang fail dan tidak
mempunyai rahsia. Keputusan di belakangnya ialah ADR-0016 dalam repositori ini;
bila sesebuah repositori menggunakannya dinyatakan dalam
[peraturan penggunaan](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/adoption-rules.md#validate).

## Tiada apa-apa untuk ditambah

Aliran kerja ini scoped: instans menjalankannya dalam setiap repositori
organisasi, pada pull request, pada push ke `main` dan secara manual. Sesebuah
repositori tidak menambah sebarang fail. Ia mempunyai
`permissions: contents: read` dan tiada rahsia. Ia mengeluarkan repositori,
mengambil skrip `tools/validate_repo.py` daripada `TirSystem/git-workflows`
pada `v2`, memasang alat dalam persekitaran maya dengan `pip` dan menjalankan
semakan.

- **Fail aliran kerja** ialah fail `*.yml` dan `*.yaml` terus dalam
  `.gitea/workflows`, `.gitea/scoped_workflows` dan `.github/workflows`.
- **Skrip shell** ialah fail `*.sh` yang dijejaki.

Repositori yang tiada kedua-duanya berakhir hijau dan mencetak
"nothing to validate".

## Apa yang disemak

Setiap dapatan menamakan fail, baris dan kriteria:
`::error file=...,line=...::[WF-8] message`.

| Kriteria | Maksudnya |
| --- | --- |
| `WF-1` | Fail bukan YAML yang sah. |
| `WF-2` | Aliran kerja dengan nama yang sama wujud dalam `.gitea/workflows` dan `.github/workflows`. |
| `WF-3` | Aliran kerja tiada `name`, `on` atau `jobs`. |
| `WF-5` | Sesuatu job atau langkah tiada nama, atau satu nama digunakan dua kali dalam job. Satu amaran. |
| `WF-7` | Aliran kerja mahupun job tidak mengisytiharkan `permissions`. |
| `WF-8` | Sesuatu action tidak dikunci pada commit, tag tepat, atau tag major bergerak milik organisasi `TirSystem`; cabang ditolak. |
| `WF-9` | Aliran kerja membaca `secrets.GITEA_*` atau `secrets.GITHUB_*` (kecuali `GITHUB_TOKEN`), atau meletakkan rahsia dalam arahan `run:`. |
| `WF-10` | Sesuatu `run:` menginterpolasi `inputs.*`, `*.event.*` atau output langkah. |
| `WF-14` | Sesuatu job tiada `runs-on` atau `timeout-minutes`. |
| `WF-20` | Blok `run:` melebihi lima baris; alihkan logik ke fail skrip. |

Kriteria `QC-WF-001` yang lain ialah pertimbangan, teks pengepala atau tingkah
laku hos, dan tidak disemak di sini. Skrip membaca struktur YAML, bukan
maknanya; ia bukan pengganti `actionlint`.

## Apa yang menggagalkan larian

| Dapatan | Dalam log | Menggagalkan larian |
| --- | --- | --- |
| Mana-mana kriteria kecuali `WF-5` | `::error file=...,line=...::[WF-8] ...` | Ya |
| `WF-5` | `::warning file=...,line=...::[WF-5] ...` | Tidak |
| `shellcheck` atau `shfmt -d` menemui masalah | output alat itu sendiri | Ya |

Kegagalan alat itu sendiri ialah `[tool]`: pakej tidak dapat dipasang (PyPI
tidak dapat dicapai) atau alat tidak bermula; jalankan semula sebelum mencari
dapatan.

## Nama status

Status yang ditunjukkan oleh pull request dan commit ialah
`Validate / validate (<event>)`, dengan event ialah `pull_request` atau
`push`. Aliran kerja keluaran memerlukan yang dihasilkan oleh push pada cabang
lalai. Rentetan tepat yang dihasilkan oleh instans masih perlu disahkan
(MIL-017, tugas 1).

## Mendiamkan dapatan

Positif palsu didiamkan di tempatnya, dan sebabnya dicatat dalam pull request:

- Pada baris: `# validate-ignore: WF-8` (beberapa kriteria dipisahkan dengan
  koma).
- Untuk seluruh fail: `# validate-ignore-file: WF-5`, di mana-mana dalam fail.
- Shell: `# shellcheck disable=SC2086` yang biasa sebelum arahan.
- Pemformatan shell: `shfmt` membaca `.editorconfig` repositori
  (`indent_style`, `indent_size`, `shell_variant`); tetapkan di situ.

Dapatan yang benar dibetulkan, bukan didiamkan.

## Menandakan semakan sebagai wajib

Menetapkan semakan sebagai wajib dalam perlindungan cabang ialah apa yang
menghalang penggabungan apabila ada ralat. Ia tetapan perlindungan cabang, jadi
pemilik repositori yang melakukannya. Amaran tidak pernah menghalang.

## Alat yang dikunci dan lesennya

Alat dikunci dalam skrip dan hanya dialihkan dalam keluaran repositori ini.
Lesen dibaca pada 2026-10-29.

| Alat | Versi | Lesen |
| --- | --- | --- |
| PyYAML | 6.0.3 | MIT |
| `shellcheck-py` (membawa binari) | 0.10.0.1 | MIT |
| ShellCheck | yang ada dalam `shellcheck-py` | GPL-3.0 |
| `shfmt-py` (membawa binari) | 3.11.0.2 | MIT |
| shfmt | yang ada dalam `shfmt-py` | BSD-3-Clause |

Alat dijalankan sebagai program berasingan dan tiada apa-apa daripadanya
disalin ke dalam repositori, jadi copyleft ShellCheck tidak tersentuh.

## Percubaan pada repositori ini

Satu larian setempat pada 2026-10-29 menemui:

- 1 ralat: `WF-20`, `run:` dalam `publish-wiki-pages.yml` mempunyai enam baris.
- 11 amaran: `WF-5`, job tanpa nama.
- `shfmt` 3.14.1 akan mengubah `tools/code-metrics.sh` dan
  `tools/quality-checks.sh`; versi dikunci 3.11.0.2 dibaca dalam percubaan pada
  instans dan mungkin memformat secara berbeza.
- `shellcheck` tidak menemui apa-apa.

Pada repositori ini semakan itu akan gagal sehingga ralat `WF-20` dibetulkan
atau didiamkan.
