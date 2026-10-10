<!-- translation of Upgrading.md, source sha256 ff8a06c4a03f -->

> Ini ialah terjemahan [`Upgrading`](Upgrading). Halaman bahasa Inggeris ialah teks yang sah, dan perubahan di sini akan ditimpa pada penerbitan wiki yang seterusnya.

[English](Upgrading) | [Dansk](Upgrading.da) | Bahasa Melayu

# Menaik taraf kepada versi baharu aliran kerja bersama

Cara seorang jurutera perisian menerima keluaran baharu aliran kerja bersama dengan selamat: baca changelog, cuba kemas kini di satu tempat, dan berpatah balik jika gagal. Peraturan versi ialah peraturan proses keluaran: satu versi untuk seluruh repositori, tag `vMAJOR.MINOR.PATCH` dan tag major yang boleh digerakkan `vMAJOR`.

## Versi yang anda ikuti

| Dalam baris `uses:` anda | Anda menerima | Gunakan apabila |
| --- | --- | --- |
| `@v1.2.0` | tiada apa-apa yang baharu, selama-lamanya | saluran paip tidak boleh berubah |
| `@v1` | keluaran serasi sahaja (minor dan patch) | pilihan lalai untuk sesebuah projek |
| `@main` | semuanya, termasuk yang belum dikeluarkan | jangan sekali-kali; hanya untuk ujian repositori ini sendiri |

Keluaran yang memecahkan keserasian mendapat versi major baharu (`v2`), jadi saluran paip pada `@v1` tidak menerimanya sehingga anda sendiri menukar baris itu.

Dua aliran kerja scoped (**Sync GitHub mirror metadata** dan **Publish wiki**) dihantar oleh instans dan tidak terdapat dalam baris `uses:` anda; anda tidak boleh menyematkannya, tetapi ia mengambil skripnya pada tag major.

## Membaca satu catatan changelog

Buka `CHANGELOG.md` bagi `TirSystem/github-action`, atau halaman keluaran tag itu. Satu catatan mempunyai sehingga empat kumpulan:

| Kumpulan | Maksudnya untuk anda |
| --- | --- |
| Breaking | Anda mesti bertindak: nama, input, secret atau nilai lalai telah berubah. Keluaran dengan kumpulan ini mempunyai versi major baharu |
| Added | Tiada apa-apa untuk dibuat; input pilihan, aliran kerja atau keupayaan baharu |
| Changed | Tiada apa-apa untuk dibuat; tiada kesan yang kelihatan bagi pemanggil sedia ada |
| Fixed | Tiada apa-apa untuk dibuat; pembetulan yang anda terima pada `@v1` |

Catatan yang mengubah kelayakan (credentials), token atau kebenaran menyatakannya; semak secret anda sebelum menaik taraf.

## Mencuba satu kemas kini

1. Tukar versi dalam **satu** repositori, pada satu cabang:
   ```yaml
   jobs:
     quality:
       uses: TirSystem/github-action/.gitea/workflows/quality-checks.yml@v2
   ```
2. Buka pull request dan baca larian. Semakan yang gagal menunjukkan alat, fail dan mesej (lihat panduan membaca keputusan semakan kualiti).
3. Bagi keluaran yang memecahkan keserasian, ikut nota naik taraf dalam catatan changelog, kemudian ulang.
4. Apabila pull request hijau, buat perubahan yang sama dalam repositori lain.

## Berpatah balik

1. Tukar baris itu kembali kepada tag tepat yang terdahulu, contohnya `@v1.2.0`, dan gabungkan. Tag tepat tidak pernah dipadam atau digerakkan, jadi ini sentiasa berfungsi.
2. Beritahu penyelenggara keluaran mana yang gagal dan apa yang anda lihat, supaya tag major boleh digerakkan balik dan pembetulan dikeluarkan.

## Apabila ada yang tidak jelas

| Gejala | Punca yang mungkin | Pembetulan |
| --- | --- | --- |
| Larian menyatakan aliran kerja tidak ditemui | Tag tidak wujud, atau laluan salah | Semak tag pada halaman keluaran dan laluan `.gitea/workflows/quality-checks.yml` |
| Saluran paip hijau menjadi merah selepas keluaran pada `@v1` | Keluaran serasi tidak sepatutnya berbuat demikian | Sematkan tag tepat yang terdahulu dan laporkan sebagai kecacatan |
| Satu input tidak lagi diterima | Keluaran yang memecahkan keserasian menamakannya semula | Baca kumpulan Breaking dalam catatan itu |
