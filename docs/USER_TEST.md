# Panduan uji coba JPO Decision Lab

**Tujuan:** mencoba seluruh alur seperti pengguna baru, dari data hingga pemeringkatan ulang. Panduan ini memakai **data sintetis**. Angka berikut bukan hasil survei, bukan rekomendasi lokasi JPO, dan tidak dimaksudkan untuk mendukung pembangunan.

## Sebelum mulai

Jalankan server sesuai README, lalu buka `http://127.0.0.1:8000`. Pastikan indikator koneksi di bar atas menunjukkan server lokal tersambung. Klik **Panduan uji** jika ingin melihat ringkasan langkah tanpa meninggalkan aplikasi.

Hati-hati: **Buat skenario uji** mengganti isi workspace, sedangkan **Reset workspace** mengosongkannya. Unduh JSON dari **Riwayat & sumber** dahulu bila ada pekerjaan yang ingin dipertahankan.

## Uji satu: peta dan kondisi awal

1. Buka **Ikhtisar lokasi**. Peta menonjolkan wilayah Kecamatan Jatinangor; bagian luar terlihat abu-abu ketika peta online berfungsi. Pratinjau vektor batas tetap muncul jika jaringan tidak tersedia.
2. Tekan **Area luar: redup**. Label berubah menjadi **Area luar: terang**. Tekan lagi untuk mengembalikan fokus.
3. Tekan **Fokus wilayah**. Pada peta online, kamera kembali ke batas kecamatan. Pada pratinjau offline, tampilan tetap berada pada batas kecamatan.
4. Periksa daftar A1–A4. Tidak adanya marker bukan bug: paper menyebut area kandidat, bukan titik koordinat crossing yang terkonfirmasi. Klik panah di samping kandidat untuk membuka detail; jangan centang verifikasi tanpa pemeriksaan.

**Hasil yang diharapkan:** batas wilayah tetap terlihat; 0/4 koordinat terverifikasi pada workspace baru; tidak muncul pin buatan.

## Uji dua: simulasi lengkap

1. Klik **Buat skenario uji**. Isi seed `202611` dan tekan **Buat dataset sintetis**.
2. Status berubah menjadi **SIMULASI**, dan kelengkapan pengukuran menjadi **56/56**. Seed sama menghasilkan data yang sama.
3. Buka **Data penelitian**. Pilih A1, lalu A2. Periksa kode, satuan, *benefit/cost*, sumber, dan periode tiap nilai. Nilai ini terkunci pada mode demo; untuk memasukkan data asli harus mengosongkan workspace terlebih dahulu.
4. Buka **Penilaian pakar**. Periksa enam tingkat matriks perbandingan. Penilaian yang tampil merupakan fixture sintetis, bukan hasil wawancara.
5. Buka **Pemeringkatan** dan klik **Jalankan perhitungan**.

**Hasil yang diharapkan:** empat lokasi memperoleh koefisien TOPSIS, bobot global berjumlah satu, tersedia perbandingan AHP biasa, diagnostik konsistensi, dan hasil sensitivitas. Hasilnya berlabel simulasi.

## Uji tiga: observasi mengubah data

1. Setelah ranking awal tersedia, buka **Observasi**, pilih A1.
2. Masukkan contoh masukan buatan berikut:

   | Kolom | Contoh simulasi |
   | --- | --- |
   | Penyeberang/jam | `240` |
   | Puncak/15 menit | `64` |
   | Kendaraan/jam | `1100` |
   | Kecepatan | Kosongkan |
   | Terkalibrasi | **Jangan centang** |
   | Asal data | `Skenario pengujian aplikasi, bukan survei lapangan` |
   | Periode | `Simulasi satu jam, skenario berbeda` |

3. Klik **Simpan observasi**, kemudian **Terapkan** pada catatan yang muncul.
4. Kembali ke **Pemeringkatan**. Hasil lama harus ditandai **tidak mutakhir**. Klik **Jalankan perhitungan** lagi.
5. Buka **Riwayat & sumber** dan lihat urutan tindakan. Unduh JSON bila ingin menyimpan data simulasi.

**Hasil yang diharapkan:** C1.3, C2.1, C2.2 untuk A1 diperbarui, run sebelumnya ditandai *stale*, kemudian run baru tersimpan. Posisi peringkat dapat berubah atau tetap; angka tidak boleh dikarang demi memperlihatkan perpindahan urutan.

## Uji empat: alur data lapangan (tanpa dummy)

1. Unduh JSON apabila perlu, kemudian **Reset workspace**.
2. Verifikasi identitas keempat kandidat, terutama A4 yang namanya berbeda dalam paper.
3. Periksa titik penyeberangan langsung di lapangan atau pada sumber geospasial yang dapat dipertanggungjawabkan. Masukkan koordinat dan sumber, baru tandai verifikasi. Batas polygon pada peta adalah referensi yang **disederhanakan**, bukan bukti bahwa konstruksi layak.
4. Untuk setiap kandidat, isi 14 pengukuran beserta satuan, sumber, periode observasi, dan tinjauan mutu.
5. Tambahkan pakar yang relevan, isi penilaian perbandingan lengkap dan evaluasi konsistensinya.
6. Jalankan TOPSIS. Tinjau kesetaraan periode pengukuran dan hasil analisis sensitivitas sebelum menyampaikan prioritas kajian.
7. Observasi kamera masih harus diproses menjadi hitungan agregat terverifikasi dan dimasukkan secara manual. Tidak ada koneksi kamera fisik atau deteksi otomatis dalam prototipe ini.

## Jika ada masalah

- **Tidak ada peta jalan:** sambungan tile internet/Leaflet belum tersedia. Batas kecamatan versi vektor tetap dapat dipelajari. Perhitungan DSS tidak bergantung pada tile internet.
- **Tidak bisa menjalankan TOPSIS:** periksa 56 nilai yang sudah ditinjau, matriks pakar, konsistensi, dan identitas kandidat (mode input pengguna).
- **Nilai baru tidak mengubah peringkat:** itu mungkin. Bandingkan koefisien sebelum/sesudah dan cek apakah input benar-benar berbeda; jangan memaksakan pergantian peringkat.
- **Satu observasi tidak bisa diterapkan ulang:** memang ditolak untuk mencegah pembaruan ganda.
- **Jangan menampilkan dataset demo sebagai survei:** status simulasi merupakan bagian integritas riset.