# Verifikasi rilis

## Yang sudah diuji

- `node test_engine.js`: skala fuzzy, perbandingan berpasangan, CR, bobot hierarki, TOPSIS benefit/cost, kasus matriks identik, dan sensitivitas.
- `python tests/test_ui.py`: data kosong memblokir TOPSIS; input sintetis memungkinkan pembobotan, peringkat, masukan IoT agregat, penghitungan ulang, dan audit.
- `python tests/qa_extended.py`: tujuh layar pada lebar 320, 390, 768, 1440, 1920, dan 2560 piksel tanpa horizontal overflow dokumen; uji konfirmasi lokasi tanpa koordinat, ambiguitas A4, ekspor CSV, impor agregat JSON, dan pemulihan JSON tanpa mempercayai hasil hitung dari berkas impor.

Fixture sintetis hanya disiapkan saat pengujian. Aplikasi distribusi dibuka dengan keadaan kosong.

## Yang belum diuji

Akurasi kamera, kinerja pada video lapangan, kesesuaian output dengan keputusan pakar, kualitas data instansi, keamanan jaringan, peran multiuser, retensi media, kesiapan produksi, dan aturan standar konstruksi JPO. Hasil pada browser tidak menggantikan validasi ini.

## Kondisi penyajian hasil

Sebuah peringkat TOPSIS hanya boleh disebut urutan **prioritas kajian**. Tidak boleh ditafsirkan sebagai hasil penilaian kondisi sebenarnya di empat titik Jatinangor tanpa bukti data dan persetujuan metode.