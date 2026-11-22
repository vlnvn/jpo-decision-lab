# Audit antarmuka — copy, hierarki, dan detail interaksi

Cakupan: enam halaman JPO Decision Lab, navigasi desktop/mobile, header, status data, panel kandidat, modal, tabel, peta, dan pemeringkatan. Audit ini dilakukan sebagai perbaikan antarmuka prototipe, bukan sertifikasi aksesibilitas atau kesiapan produksi.

## Temuan yang diperbaiki

| Area | Masalah sebelum revisi | Perbaikan dan alasan |
| --- | --- | --- |
| Identitas dan konteks | Nama produk diulang di sidebar, breadcrumb, kicker halaman, dan footer | Nama produk cukup di sidebar; topbar menunjukkan wilayah studi, judul halaman menjelaskan tugas saat ini; footer dekoratif dihapus |
| Breadcrumb | `Studi Jatinangor / Observasi` dan nama halaman diulang lagi tepat di bawahnya | Topbar hanya `Jatinangor` / `Kabupaten Sumedang`, sedangkan tab dan judul memberikan orientasi halaman |
| Label artifisial | `01 / JPO DECISION LAB`, `INSPEKSI LOKASI`, `STUDI KAWASAN`, `SUMBER GEOMETRI` | Dihapus atau diganti label alami seperti `Kandidat lokasi`, `Alur penelitian`, dan `Batas kecamatan` |
| Teks sangat kecil | Beberapa label penting bergantung pada 9–11 px dan huruf monospaced kapital | Teks kendali, metadata inti, dan bantuan ditingkatkan ke umumnya 12–13 px; kode teknis serta atribusi peta boleh tetap lebih kecil |
| Navigasi mobile | Hanya beberapa dari enam tab terlihat; pengguna harus mengetahui gesture geser horizontal | Enam tab terlihat sebagai grid responsif dua atau tiga kolom, dengan status aktif teridentifikasi oleh `aria-current="page"` |
| Copy teknis berlebihan | Halaman input menjelaskan `SQLite`, halaman ranking menjelaskan `snapshot` sebelum tujuan pengguna | Pembukaan halaman ditulis sesuai tugas yang dikerjakan; detail backend dan metodologi tetap tersedia di dokumen kode |
| Status simulasi | Penjelasan panjang diulang pada setiap halaman dan banyak badge tambahan | Status simulasi tetap terlihat, dengan satu penjelasan ringkas bahwa angka dan bobot bukan observasi Jatinangor |
| Kartu indikator | `1 kecamatan` kurang berguna bagi aktivitas analisis | Diganti metrik operasional `Penilai`; jumlah kandidat, kelengkapan pengukuran, dan koordinat terverifikasi tetap dinamis |
| Ranking *stale* | Kandidat teratas tampil dominan sebelum peringatan bahwa hasil sudah kedaluwarsa | Peringatan *stale* muncul **sebelum** hasil; panel lama dibedakan secara visual, tidak diam-diam dihitung ulang |
| Icon affordance | Lambang `↗` pada tombol edit dan ekspor menyiratkan membuka situs luar | Tombol sunting menggunakan ikon pena; ekspor diberi label tepat `Ekspor JSON`; link navigasi tahapan menggunakan panah kanan |
| Form koordinat | Deskripsi panjang dan label ambigu tentang lokasi yang belum divalidasi | Penjelasan menjadi singkat; nama sumber dan status tetap eksplisit, tanpa menganggap marker referensi sebagai koordinat crossing |

## Dipertahankan dengan sengaja

- Arsitektur FastAPI–SQLite, pemisahan data sintetis dan pengukuran, serta seluruh definisi 14 kriteria.
- Fungsi Fuzzy AHP, TOPSIS, uji konsistensi dan sensitivitas; tidak ada perubahan rumus maupun data.
- Batas administrasi HDX/BPS versi referensi, empat marker kawasan, dan penanda **0/4** crossing terverifikasi pada workspace kosong.
- Validasi input, audit, ekspor, serta keharusan hitung ulang setelah sumber input berubah.
- Peringatan keterbatasan metodologi yang benar-benar penting; tidak dibuat seolah aplikasi telah menentukan pembangunan JPO.

## Pengujian

Jalankan setelah dependency terpasang:

```bash
python -m pytest tests/test_mcdm.py tests/test_api.py tests/test_provenance_csv.py -q
python -m pytest tests/test_ui.py tests/test_journey.py tests/test_map_stack.py tests/test_map_references.py -q
python -m pytest tests/test_ui_alignment.py tests/test_editorial_design.py -q
node --check web/app.js
```

Pengujian browser memeriksa 320–2560 px (berbagai tes), enam navigasi terlihat di mobile, keterbacaan komponen inti, label modal dan tombol, tidak adanya overflow dokumen, serta keadaan *stale*. Preview di `release_preview/` dibuat dengan HTML/CSS/JS nyata melalui fixture API lokal, bukan gambar konseptual.

## Sumber prinsip audit

- [Impeccable — product slop test](https://github.com/pbakaus/impeccable/blob/main/skill/reference/operate.md): setiap elemen harus membantu pengguna menyelesaikan tugas; dekorasi dan micro-label yang mengganggu hierarki perlu ditinjau.
- [Nielsen Norman Group — Design of complex applications](https://www.nngroup.com/articles/complex-application-design/): ketepatan hierarki, status sistem, dan interaksi pada aplikasi kerja.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/): label yang dapat diakses, fokus keyboard, serta ukuran target kontrol.

**Batas audit:** ketiadaan *AI-slop signs* tidak dapat dibuktikan sebagai fakta universal. Uji pengguna pertama kali, aksesibilitas pembaca layar, serta ketersediaan peta pihak ketiga di jaringan sebenarnya masih harus dilakukan. Tidak ada klaim telah menjalankan Impeccable CLI: pemeriksaan dilakukan melalui review source, Playwright, screenshot, dan pengujian API.
