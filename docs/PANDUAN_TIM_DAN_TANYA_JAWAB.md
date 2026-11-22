# Panduan pengguna dan pertahanan teknis — JPO Decision Lab

> **Status:** research prototype. Berkas ini menjelaskan implementasi yang ada, bukan klaim validasi lokasi atau keputusan konstruksi. Baca bersama `docs/METHOD.md`, `docs/SYNTHETIC_DATA.md`, dan `docs/GEO_SOURCE.md`.

## 1. Jawaban tiga kalimat saat demonstrasi

Website ini membantu tim peneliti **mengurutkan prioritas lokasi yang perlu dikaji lebih lanjut** untuk kemungkinan fasilitas penyeberangan di Jatinangor. Penilaian pakar diproses menjadi bobot dengan Fuzzy AHP, kemudian 14 nilai pengukuran per kandidat diproses dengan TOPSIS. Sistem **tidak** membuktikan bahwa sebuah JPO harus dibangun dan **tidak** memiliki dataset lapangan atau kamera IoT terpasang.

## 2. Peta: jangan samakan tiga objek

- **Batas kecamatan:** poligon visual historis HDX/BPS 2020, disederhanakan secara kartografis menjadi 391 koordinat. Tidak layak untuk penetapan batas hukum.
- **Empat penanda A1–A4:** referensi landmark/kawasan berdasarkan sumber publik. Bukan survei titik penyeberangan. A1 gerbang Unpad, A2 referensi koridor Jalan Ciseke (bukan simpang terverifikasi), A3 koordinat umum kampus ITB (bukan gerbang), A4 Gerbang PKD IPDN dari plus code (bukan bukti GKPN).
- **Titik penyeberangan terverifikasi:** hanya ada ketika pengguna memasukkan koordinat, sumber, dan menyatakan telah memeriksa titiknya. Status default `0/4` harus dipertahankan sampai itu terjadi.

Validasi yang disarankan: cocokkan deskripsi pada paper, survei ruas dan arah penyeberangan, simpan GPS/lokasi peta, foto lokasi beserta tanggal, catat sumber dan nama pemeriksa, lalu tinjau bersama pihak kompeten sebelum memberi flag verifikasi. Koordinat `REFERENCE_AREAS` dalam `server/catalog.py` tidak boleh di-copy sebagai koordinat JPO.

## 3. Uji coba pengguna — simulasi (jangan gunakan data asli)

1. Jalankan server lokal: `python -m uvicorn server.app:app --host 127.0.0.1 --port 8000`; buka `http://127.0.0.1:8000`. Data disimpan pada komputer yang menjalankan server, bukan akun cloud.
2. **Ikhtisar lokasi:** lihat batas Jatinangor, empat landmark A1–A4, status koordinat `0/4`, kontrol layer/fokus, dan data readiness yang masih kosong.
3. Klik **Mulai simulasi** dan masukkan seed `202611`; konfirmasi bahwa workspace saat ini akan diganti. Generator membuat **56 nilai** (4×14), satu panel pakar sintetis dan matriks perbandingan sintetis. Jangan menganggapnya observasi Jatinangor.
4. **Data penelitian:** periksa A1 sampai A4, setiap nilai, sumber, satuan, benefit/cost, dan periode. Unduh CSV lalu cocokkan dengan `examples/synthetic_demo_seed_202611.csv`.
5. **Penilaian pakar:** buka lima kelompok utama dan lima kelompok subkriteria (total **enam matriks**). Dalam mode demo, nilainya bukan pendapat ahli sungguhan.
6. **Pemeringkatan:** klik **Jalankan perhitungan**. Pelajari bobot, consistency ratio, urutan TOPSIS, AHP konvensional sebagai pembanding, dan sensitivitas ±10% bobot per kelompok. Label run adalah `SIMULATION`.
7. **Observasi:** setelah baseline ranking ada, buat observasi A1 dengan penyeberang/jam=240, puncak/15 menit=64, kendaraan/jam=1100, tanpa kecepatan terkalibrasi; isi asal `Skenario pengujian, bukan survei` serta periode simulasi. Simpan, kemudian **Terapkan**.
8. Kembali ke **Pemeringkatan**: hasil lama bertanda `stale` karena dataset berubah. Hitung ulang; peringkat bisa berubah **atau** tetap. Jangan mengubah hasil supaya demo tampak dramatis.
9. **Riwayat & sumber:** tinjau event audit, ekspor CSV/JSON, metode dan rujukan. JSON ekspor bukan pengganti backup SQLite atau sinkronisasi cloud.
10. Untuk mulai data asli, ekspor yang perlu disimpan lalu **Kosongkan data**. Pengosongan menghapus data, run, penilaian, dan observasi pada workspace lokal.

## 4. Alur data asli — tahap penelitian berikutnya

1. Tetapkan A1–A4 secara jelas dari paper. A4 perlu diselesaikan: `GKPN/IPDN` vs `Pertigaan Hegarmanah/IPDN`. Nama lokasi dan identitas crossing harus dikonfirmasi tim.
2. Verifikasi koordinat titik penyeberangan dengan data lapangan/sumber yang dapat dilacak. Simpan titik dan sumber; `coordinate_verified` berbeda dari `identity_verified`.
3. Untuk keempat lokasi, isi 14 subkriteria dengan nilai nonnegatif, unit yang benar, sumber, periode, dan flag pengecekan. Nilai kosong tidak dianggap nol. Pastikan kondisi/interval survei comparable.
4. Bentuk panel pakar nyata, isi pairwise judgments secara hierarkis. Sistem memakai skala Saaty reciprocal (bilangan -x berarti preferensi kebalikan 1/x, bukan bobot negatif).
5. Validasi matriks dan konsistensi. Ambang yang diterapkan sistem adalah crisp modal Saaty CR <=0,10; ini keputusan implementasi yang perlu disetujui tim dan pakar.
6. Jalankan FAHP dan TOPSIS; keluaran berupa prioritas **kajian lebih lanjut**, bukan keputusan pembangunan.
7. Catat data observasi agregat baru yang sudah diperiksa, terapkan untuk memperbarui kriteria dinamis, lalu hitung ulang.
8. Untuk kajian lanjutan, tinjau aturan keselamatan dan kelayakan konstruksi oleh ahli; TOPSIS bersifat kompensatoris dan tidak menggantikan ambang minimum teknis.

## 5. Jalur data dan lokasi kode

`web/index.html` (struktur) + `web/styles.css`/`web/studio.css` (presentasi) + `web/app.js` (event dan permintaan HTTP) → `server/app.py` (FastAPI dan validasi Pydantic) → `server/database.py` (SQLite dengan transaksi serta WAL) → `server/mcdm.py` (Fuzzy AHP, AHP, TOPSIS, sensitivitas) → tabel `runs` (hasil dan hash dataset) → UI.

Tabel: `candidates`, `criteria`, `measurements`, `experts`, `judgments`, `observations`, `runs`, `audit`, `settings`. File default `data/jpo.sqlite3`. Definisi empat kandidat dan 14 kriteria dibaca dari `server/catalog.py`; data simulasi dihasilkan oleh `server/demo.py` dengan `random.Random(seed)`. Peta batas/landmark dari `GET /api/geography/jatinangor`, bukan tabel pengukuran. Cek rincian API interaktif di `http://127.0.0.1:8000/api/docs`.

## 6. Logika pengaman yang benar-benar diterapkan

- Tidak bisa menghitung TOPSIS sebelum **56 nilai checked**, minimal satu panel pakar dan matriks pairwise lengkap. Mode data asli juga membutuhkan **identitas keempat kandidat** terkonfirmasi.
- `C4.2` dan `C4.3` harus integer 1–5; indikator hitungan harus integer; kecepatan dibatasi sampai 250 km/jam sebagai pemeriksaan kewajaran input, **bukan** batas kecepatan jalan setempat.
- Sistem menolak pencampuran input lapangan dengan workspace synthetic sebelum direset.
- Observasi hanya bisa dibuat sesudah ranking baseline yang cocok dengan hash data saat itu; satu observasi tidak boleh diterapkan dua kali.
- `C1.3` berubah oleh jumlah kendaraan, `C2.1` oleh penyeberang per jam, `C2.2` oleh puncak 15 menit, sedangkan `C1.2` hanya berubah bila kecepatan diberi flag terkalibrasi.
- Hasil ranking menyimpan SHA-256 fingerprint dari kandidat, measurement, panel dan judgments. Bila inputs berubah, run lama ditandai `stale`, bukan otomatis dihitung ulang.
- Perbedaan periode antarlokasi menghasilkan `data_quality.period_warnings`, **peringatan**, bukan otomatis blokir matematis.
- CSV menandai `synthetic`/ `field`, melindungi teks sumber yang bisa ditafsirkan sebagai formula spreadsheet. JSON memuat snapshot; audit bersifat log dalam database, bukan tahan manipulasi kriptografis.

## 7. Metode matematika yang harus bisa dijelaskan

**Fuzzy AHP:** bandingkan lima kelompok dan lima kumpulan subkriteria secara berpasangan; ubah intensitas Saaty menjadi triangular fuzzy numbers; hitung geometric mean Buckley, defuzzifikasi centroid dan normalisasi. Bobot global subkriteria = bobot kelompok × bobot lokal, lalu normalisasi sehingga total bobot 1. Konsistensi diperiksa terhadap matriks modal crisp untuk setiap pakar/level; threshold 0,10 adalah aturan implementasi. Kode: `server/mcdm.py` fungsi `tfn`, `judgment_matrix`, `consistency`, `calculate_weights`.

**TOPSIS:** bentuk matriks 4×14; normalisasi kolom dengan norm vektor; kalikan bobot; tentukan solusi ideal positif/negatif sesuai `Benefit`/`Cost`; hitung jarak Euclidean `D+` dan `D-`; koefisien preferensi `D-/(D++D-)`; urutkan dari terbesar. Kode: `topsis`. Pembanding AHP klasik memakai bobot crisp dan TOPSIS yang sama. Sensitivitas mengubah bobot satu kelompok ±10%, normalisasi kembali, dan melihat apakah pemimpin berubah. Semua ini opsi implementasi yang perlu diaudit, bukan rumus lengkap yang semuanya tertulis di paper.

## 8. Pertanyaan kritis yang mungkin diajukan

- **Mengapa A1–A4 belum presisi?** Nama pada paper adalah kawasan; sumber peta masih landmark. Tidak boleh mempromosikan landmark menjadi titik crossing.
- **Apakah A3 berada tepat di gerbang ITB?** Tidak dapat dibuktikan; sumber hanya koordinat umum kampus. Label peta dikoreksi.
- **Kenapa memakai SQLite?** Ringan dan cukup untuk satu workspace lokal serta demo yang butuh persistensi; belum layak untuk multiuser terotorisasi.
- **Apakah sudah IoT nyata?** Belum. Saat ini hanya penerimaan observasi agregat manual. Sistem kamera, model CV dan validasi akurasi belum ada.
- **Apakah dataset demo akurat terhadap Jatinangor?** Tidak. Seed tetap memastikan reproduksibilitas, bukan representativitas lapangan.
- **Apakah ranking tertinggi wajib dibangun JPO?** Tidak. Hanya prioritas *feasibility study*. Kelayakan teknis minimum bisa menggugurkan pilihan meski TOPSIS tinggi.
- **Apa yang dinamis vs hardcoded?** Pengukuran, penilaian, observasi, dan run hidup di SQLite/API; 14 definisi paper, batas historis, dan koordinat landmark bersumber adalah konfigurasi versi tetap.
- **Kenapa tidak bisa dipakai banyak orang melalui internet?** Belum ada authentication, authorization, keamanan deployment, backup, maupun penanganan konflik multiuser. Jalankan pada `127.0.0.1`.
- **Apakah model di paper telah terbukti?** Belum; paper berbentuk scoping review dan usulan rancangan. Software sekarang memvalidasi alur komputasi pada pengujian sintetis, bukan efektivitas intervensi infrastruktur.
- **Bagaimana pembagian review?** Data lapangan diperiksa surveyor; penilaian kriteria oleh panel pakar; metode FAHP-TOPSIS oleh tim penelitian; keputusan fasilitas oleh pihak berwenang dan ahli jalan. Jangan jadikan satu user sebagai pemeriksa semua lapisan.

## 9. Urutan kode untuk code review

Mulai dari `server/catalog.py` (apa data tetapnya), `server/demo.py` (asumsi dummy), `server/database.py` (tabel/transaksi), `server/app.py` (validasi dan endpoint), `server/mcdm.py` (rumus), `web/app.js` (event → HTTP), lalu `tests/` (apa yang benar-benar teruji). Untuk daftar lengkap endpoint, baca `docs/ARCHITECTURE.md`.
