# Interface design notes

## Direction

Antarmuka diperlakukan sebagai meja kerja analisis transportasi. Pembaca perlu melihat **kondisi data terlebih dahulu**, bukan contoh peringkat atau statistik yang tidak ada di paper.

Sistem visual memakai warna netral hangat, hijau gelap untuk struktur, dan status yang dinyatakan dalam teks. Tabel, daftar prasyarat, dan matriks kelengkapan lebih berguna dibanding ilustrasi jalan sintetis. Tipografi menggunakan font lokal browser, tanpa mengunduh font atau ikon pihak ketiga.

## Keputusan antarmuka

- Ringkasan menempatkan matriks 4 × 14 sebagai objek utama. Sel dapat diklik menuju entri data terkait.
- Komponen untuk kandidat dipisahkan dari tabel kriteria karena jenis informasi dan tugas pengguna berbeda.
- Hasil komputasi tidak tampak sampai kondisi input dan konsistensi memenuhi persyaratan.
- Peringatan data hilang dibedakan dari penilaian bahwa suatu lokasi tidak aman.
- Desktop dirancang secara fluid sampai 1920 px dan diuji juga pada 2560 px. Pada viewport kecil, navigasi dan matriks boleh digeser pada sumbu horizontal di dalam komponennya, bukan pada keseluruhan halaman.
- Setiap elemen interaktif memiliki fokus keyboard. Animasi dikurangi bila pengguna meminta reduced motion.

## Pola yang sengaja dihindari

Hero berilustrasi dekoratif, barisan kartu seragam, metrik rekaan, huruf kapital kecil di setiap seksi, gradient text, glow, glassmorphism, emoji sebagai ikon produk, dan promosi yang tidak berkaitan dengan penelitian.

Sumber rujukan desain: [Impeccable](https://github.com/pbakaus/impeccable) (panduan audit produk, tipografi, layout, UX writing) dan [WCAG 2.2](https://www.w3.org/TR/WCAG22/) (reflow, navigasi keyboard, kejelasan antarmuka). Panduan tersebut memengaruhi proses review; kode desain ditulis khusus untuk proyek ini.