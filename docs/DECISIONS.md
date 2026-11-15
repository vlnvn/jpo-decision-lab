# Catatan keputusan metode

## Ditentukan paper

- Empat kandidat A1–A4; lokasi tepat perlu diverifikasi, khususnya penamaan A4.
- Lima kelompok, 14 subkriteria, tipe benefit/cost, dan satuan sesuai Tabel II.
- Fuzzy AHP untuk bobot berbasis pakar, TOPSIS untuk pemeringkatan alternatif.
- Bobot global hierarki diperoleh dari bobot kelompok × bobot subkriteria dan dinormalisasi.
- Observasi IoT dilakukan setelah prioritas awal. Pengamatan dapat memperbarui C1.3, C2.1, C2.2, serta C1.2 bila kecepatan terkalibrasi.
- Uji sensitivitas dan pembandingan AHP konvensional direkomendasikan.

## Keputusan implementasi yang tidak dinyatakan rinci oleh paper

1. Skala TFN: intensitas 1–9, kebalikan triangular `(1/u, 1/m, 1/l)`; rujukan skala [2023, DOI 10.1155/2023/6692916](https://doi.org/10.1155/2023/6692916).
2. Penghitungan bobot: geometric mean Buckley (1985), defuzzifikasi centroid, normalisasi. Rujukan [DOI 10.1016/0165-0114(85)90090-9](https://doi.org/10.1016/0165-0114(85)90090-9).
3. Multi-pakar: geometric mean penilaian fuzzy. Diagnostik AHP memakai nilai modal crisp; CR maksimal 0,10 per matriks dan per penilai. CR crisp bukan bukti konsistensi fuzzy secara menyeluruh.
4. TOPSIS: normalisasi vektor, pembobotan, solusi ideal menurut benefit/cost, jarak Euclidean, dan koefisien kedekatan `D− / (D+ + D−)`.
5. Sensitivitas: perubahan ±10% per kelompok lalu renormalisasi. Persentase ini hanya pilihan uji perangkat lunak, bukan temuan lapangan.

Keputusan 1–5 harus ditinjau tim sebelum dipakai dalam laporan hasil empiris. Kode tidak mengklaim bahwa naskah telah menetapkan rumus lengkap yang sebenarnya belum tercantum.