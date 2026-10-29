<!-- translation of SyncMilestones.md, source sha256 59a0aa110097 -->

> Ini ialah terjemahan [`SyncMilestones`](SyncMilestones). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](SyncMilestones) · [Dansk](SyncMilestones-da) · **Bahasa Melayu**

# Menerbitkan milestone yang diterima

Cara milestone yang diterima bagi sesebuah projek menjadi milestone dan isu di
Gitea dengan aliran kerja scoped `sync-milestones.yml`. Ia menggantikan salinan
`sync-milestones.yml` yang dahulu disimpan oleh repositori dalam
`.gitea/workflows/`. Keputusannya ialah ADR-0018 dalam repositori ini; bila
sesebuah repositori menggunakannya dinyatakan dalam
[peraturan penggunaan](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/adoption-rules.md#publish-accepted-milestones).

## Apa yang dilakukannya

Bagi setiap dokumen milestone dalam `docs/milestones/`, ia mencipta atau
mengemas kini milestone Gitea dan satu isu bagi setiap baris tugas melalui
`framework/scripts/ci-publish-milestones.sh publish`, yang menjalankan
`sync-project.sh --accepted-only`. Hanya milestone yang baris terkini Version
History-nya `Accepted` dan semakan terkininya Go diterbitkan. Milestone
`Proposed`, atau yang tiada semakan Go, dilangkau dengan sebabnya dalam log.

## Folder ialah pilihan menyertai

Aliran kerja ini scoped: instans menjalankannya dalam setiap repositori
organisasi, jadi sesebuah repositori tidak menambah sebarang fail. Repositori
menerbitkan apabila ia mempunyai folder `docs/milestones/`. Repositori tanpanya
tamat dengan hijau, mencetak bahawa tiada apa-apa untuk diterbitkan dan tidak
membuat sebarang panggilan API.

## Secret

Dua secret organisasi, disimpan dalam organisasi bagi setiap repositori yang
menerbitkan. Tiada fallback: larian tanpa salah satu tamat sebagai
`[configuration]` dan menamakannya. Tiada nama lama (`GITEA_TOKEN`, `SYNC_TOKEN`)
dibaca, dan tiada token dicetak atau diletakkan pada baris arahan.

| Secret | Digunakan untuk |
| --- | --- |
| `TOKEN_FOR_GITEA_REPO` | Membaca repositori: projek dan framework persendirian, melalui HTTPS |
| `TOKEN_FOR_GITEA_ISSUES` | Menerbitkan: isu dan milestone sahaja |

Skop, siapa yang menyimpannya dan cara menukarnya ada dalam
[Credentials](Credentials-ms).

## Dari mana skrip framework datang

Skrip milestone ialah skrip framework. Aliran kerja mengambilnya daripada salah
satu daripada dua sumber dan mencetak yang mana satu dalam log:

- **Submodul projek itu sendiri** apabila `framework/scripts/ci-publish-milestones.sh`
  wujud dalam repositori. Skripnya ialah keluaran yang dikunci oleh projek.
- **Keluaran yang dikunci** jika tidak: repositori framework dikeluarkan ke dalam
  `framework/` pada tag `FRAMEWORK_TAG` dalam `tools/sync_milestones.py`. Tag
  hanya dialihkan dalam keluaran repositori ini, dan cabang tidak pernah
  digunakan. Projek tanpa submodul juga boleh menerbitkan.

Baris log menamakan sumber dan tag atau commit yang digunakan.

## Push menerbitkan, larian manual ialah larian percubaan

| Permulaan | Apa yang berlaku |
| --- | --- |
| Push ke cabang lalai yang mengubah `docs/milestones/**` atau `docs/sqa/reviews/**` | Menerbitkan (`--apply`) |
| Larian manual (`workflow_dispatch`) dengan `dry_run` dihidupkan (lalai) | Mencetak pelan dan tidak mencipta apa-apa |
| Larian manual dengan `dry_run` dimatikan | Menerbitkan |

`--accepted-only` sentiasa disertakan. Larian beratur dalam kumpulan
`publish-accepted-milestones` dan satu larian tidak pernah membatalkan yang lain.
Aliran kerja mempunyai `permissions: contents: read`.

## Tiada apa-apa ditutup atau dipadam

Milestone yang dibuang daripada `docs/milestones/` membiarkan milestone Gitea dan
isunya seperti sedia ada. Aliran kerja tidak mempunyai pilihan yang menutup atau
memadam. Setiap larian sebenar mengedit isu bagi semua milestone yang diterima,
dan hos merekodkan setiap suntingan.

## Buang salinan lama

Salinan `sync-milestones.yml` dalam `.gitea/workflows/` berjalan di sebelah
aliran kerja scoped dan menerbitkan dua kali. Padam salinan itu dalam pull request
repositorinya; aliran kerja scoped tidak memerlukan fail sebagai ganti. Memasang
templat framework `templates/ci/` untuk aliran kerja ini tidak diperlukan lagi.

## Masih perlu disahkan pada instans

ADR-0018 bergantung pada fakta yang belum disahkan oleh tugas 1 MIL-019 dalam
larian scoped:

- bahawa secret organisasi `TOKEN_FOR_GITEA_REPO` dan `TOKEN_FOR_GITEA_ISSUES`
  boleh dibaca;
- bahawa framework persendirian boleh dikeluarkan melalui HTTPS;
- sama ada submodul bersarang `framework/qc` diperlukan oleh skrip (salinan lama
  mengambilnya dengan `--recursive`).

Selagi itu belum direkodkan, panduan ini ialah keputusan, bukan hasil yang telah
diuji.
