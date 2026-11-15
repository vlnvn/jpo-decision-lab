# JPO Decision Lab

Ruang kerja analisis untuk memeringkat **prioritas kajian** empat kandidat lokasi jembatan penyeberangan orang (JPO) di Jatinangor. Proyek ini mengimplementasikan rancangan pada makalah kelompok *Model Pendukung Keputusan untuk Memprioritaskan Lokasi Jembatan Penyeberangan Orang di Jatinangor*, khususnya bagian IV–V dan Tabel II.

**Status: research prototype.** Perangkat lunak berfungsi secara offline, tetapi belum terhubung ke kamera atau sistem instansi dan belum diuji menggunakan pengukuran Jatinangor. Tidak ada angka lapangan, penilaian pakar, koordinat, atau peringkat yang dibundel sebagai hasil penelitian.

## Memulai

**Tanpa instalasi:** buka `JPO_DSS_OFFLINE.html` di browser.

**Pengembangan:** buka `index.html` melalui server statis lokal. Misalnya:

```bash
python -m http.server 8000
```

Lalu akses `http://localhost:8000`. Aplikasi hanya menggunakan HTML, CSS, dan JavaScript; tidak ada CDN atau dependensi runtime.

## Urutan kerja

1. Konfirmasi identitas A1–A4 dari bukti yang bisa ditelusuri. Nama A4 belum konsisten antara bagian IV.A dan V naskah; sistem meminta penetapan eksplisit.
2. Isi 56 nilai (empat alternatif × 14 subkriteria) beserta sumber dan periode. Nilai kosong tidak boleh diganti nol.
3. Masukkan perbandingan berpasangan pakar untuk lima kelompok dan masing-masing subkelompok. Tinjau aturan Fuzzy AHP yang digunakan perangkat lunak sebelum menjalankan pembobotan.
4. Jalankan TOPSIS untuk mendapatkan urutan prioritas **kajian teknis**, lalu periksa hasil AHP konvensional dan skenario sensitivitas.
5. Setelah baseline tersedia, masukkan agregat observasi kamera yang telah ditinjau. Sistem memperbarui kriteria dinamis tertentu, menghitung ulang TOPSIS, dan menunjukkan perubahan urutan.
6. Ekspor JSON dari menu Audit untuk menyimpan pekerjaan. Aplikasi tidak melakukan penyimpanan otomatis ke server; JSON impor hanya memulihkan masukan dan membuang hasil perhitungan dari berkas luar.

## Isi repository

| Berkas | Tujuan |
|---|---|
| `index.html`, `styles.css` | Struktur dan sistem visual |
| `app.js` | Alur penelitian, formulir, provenance, input IoT, ekspor/impor |
| `engine.js` | Perhitungan Fuzzy AHP, AHP, TOPSIS, sensitivitas |
| `JPO_DSS_OFFLINE.html` | Distribusi satu berkas tanpa dependensi |
| `build_offline.py` | Reproduksi distribusi offline |
| `test_engine.js` | Pengujian komputasi deterministik |
| `tests/` | Uji alur browser dan responsivitas |
| `docs/` | Batas riset, keputusan metode, catatan desain, verifikasi |
| `.github/workflows/ci.yml` | Pemeriksaan dasar pada setiap perubahan kode |

## Membangun dan menguji

```bash
node test_engine.js
python build_offline.py
python -m pip install -r requirements-dev.txt
python tests/test_ui.py
python tests/qa_extended.py
```

`requirements-dev.txt` hanya diperlukan untuk pengujian browser, bukan untuk menjalankan aplikasinya. Pengujian browser membutuhkan Chromium; jalur executable dapat diatur melalui variabel `CHROMIUM_PATH`.

## Batas interpretasi

TOPSIS tidak menentukan bahwa suatu lokasi berbahaya atau harus dibangun JPO. Jenis fasilitas (JPO, penyeberangan sebidang, atau alternatif lain) dan kesesuaian teknis tetap diputuskan melalui kajian rekayasa lalu lintas. Fuzzy AHP dipilih dari sintesis literatur dalam paper, tetapi implementasi numerik tertentu masih berupa keputusan teknis proyek yang memerlukan persetujuan tim dan pakar. Rinciannya ada di [`docs/DECISIONS.md`](docs/DECISIONS.md).

Aplikasi menerima *agregat* jumlah kendaraan dan pejalan kaki, bukan rekaman video mentah. Kecepatan kendaraan baru boleh digunakan bila sumbernya dikalibrasi dan ditinjau. Komponen kamera fisik, autentikasi, database server, dan audit yang tahan manipulasi belum ada.

Dokumentasi teknis: [`SPESIFIKASI.md`](SPESIFIKASI.md) · [`docs/PRODUCT.md`](docs/PRODUCT.md) · [`docs/VALIDATION.md`](docs/VALIDATION.md).