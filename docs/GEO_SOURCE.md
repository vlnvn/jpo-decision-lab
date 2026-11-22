# Cakupan geografis Jatinangor

## Apa yang diperlihatkan

Endpoint `/api/geography/jatinangor` mengembalikan satu poligon GeoJSON yang menggambarkan **Kecamatan Jatinangor, Kabupaten Sumedang, Jawa Barat**. Kode referensi wilayah yang digunakan dataset adalah `32.11.15` (Jatinangor). Geometri bersifat **simplified / generalized** untuk visualisasi, bukan batas administratif yang disahkan untuk keperluan hukum, pertanahan, atau penentuan tapak konstruksi.

## Asal geometri dan lisensi

- Geometri dipilih berdasarkan atribut `code=32.11.15`, `name=KEC. JATINANGOR`, `parent_name=KAB. SUMEDANG` pada `districts/32_11.geojson` dalam repositori [aaronsanger/idn-geojson](https://github.com/aaronsanger/idn-geojson). Ekspor sumber menyatakan tanggal 8 September 2026 dan atribut sumber `cahyadsn` untuk fitur tersebut.
- Penyedia hulu yang dikreditkan fitur adalah [cahyadsn/wilayah_boundaries](https://github.com/cahyadsn/wilayah_boundaries), yang menerbitkan repo di bawah [lisensi MIT](https://github.com/cahyadsn/wilayah_boundaries/blob/main/LICENSE). Lisensi dan kredit sumber tetap dicantumkan; salinan geometri hanyalah fitur kecamatan yang diperlukan.
- Snapshot hasil ekstraksi disimpan sebagai `web/data/jatinangor.geojson`, sehingga pengalaman dasar tidak bergantung pada API geometri pihak ketiga. Bagian dalam poligon transparan pada basemap; bagian luar memakai mask abu-abu. Tidak ada koordinat kandidat JPO di dalam berkas ini.
- Sumber turunan menyatakan keterbatasan resolusi dan belum melakukan validasi independen terhadap semua poligon. Poligon ini hanya memiliki sembilan pasangan koordinat termasuk penutup ring. Saat tersedia data resmi skala lebih baik dari Badan Informasi Geospasial/pemerintah daerah dengan hak pakai yang sesuai, ganti berkas, tambahkan versi sumber, dan uji topologi dan kesesuaian titik baru.

## Etika visualisasi

Tampilan tidak boleh menyiratkan bahwa suatu gerbang kampus, jalan, atau titik kandidat sudah diukur. Marker hanya muncul apabila koordinat yang bersumber telah dikonfirmasi. Klik peta untuk memilih titik memberi **draf**, bukan verifikasi otomatis. Mask area hanya memperjelas cakupan penelitian, bukan mengunci kelayakan konstruksi atau aksesibilitas sesungguhnya.

Basemap online default adalah CARTO Positron dengan atribusi [CARTO](https://carto.com/attribution/) dan [OpenStreetMap contributors](https://www.openstreetmap.org/copyright). Jika tile CARTO gagal, aplikasi mencoba tile OpenStreetMap sebagai fallback; hak cipta dan ketentuan masing-masing penyedia tetap berlaku. Tile internet dan kemampuan click-to-pick hanya dapat diuji sepenuhnya pada mesin dengan akses jaringan. Tanpa Leaflet, tersedia fallback vektor geometri versi lokal.

## Implementasi

- `server/app.py`: endpoint GeoJSON dan pengaturan cache HTTP.
- `web/app.js`: pengambilan geometri, pratinjau vektor, mask berongga Leaflet, fitting batas, dan batasan validasi pin.
- `web/workspace.css`: hierarki visual peta, legenda, label sumber, responsive layout, dan fallback tanpa jaringan.
- `tests/test_api.py`: kode wilayah, tipe geometri, penutupan poligon, serta pemisahan geometri dari pin kandidat.
- `tests/test_ui.py`: render geometri pada desktop/mobile, legenda, mode redup/terang, dan tidak ada pin palsu.

Peta visual yang tampak baik adalah **hasil desain antarmuka**, bukan validasi akurasi geospasial atau hasil rekayasa lalu lintas.