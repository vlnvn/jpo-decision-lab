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

Basemap online utama sekarang menggunakan **OpenFreeMap Positron** melalui MapLibre GL di dalam Leaflet. OpenFreeMap menyatakan gaya vector tersedia tanpa API key dan menyediakan style `https://tiles.openfreemap.org/styles/positron`; atribusi tetap wajib. Tombol **Jalan** menggunakan raster standar `https://tile.openstreetmap.org/{z}/{x}/{y}.png` dan juga menjadi fallback jika vector tile/WebGL tidak tersedia. Sumbernya adalah OpenStreetMap dan harus mematuhi [Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/). Tidak ada lagi pemanggilan CARTO anonim yang sebelumnya menghasilkan watermark *API KEY REQUIRED* mulai 2026.

Saat service eksternal atau script CDN tidak tersedia, aplikasi secara eksplisit menampilkan status kegagalan dan SVG batas kecamatan dari GeoJSON yang sama; **tidak menggambar jaringan jalan atau marker fiktif**. Pemuatan tile OpenFreeMap dan OSM nyata belum dapat divalidasi dari runner lokal yang memblokir akses HTTP luar, maka diperlukan pemeriksaan manual di perangkat yang terhubung internet. Kondisi ini tidak mempengaruhi perhitungan DSS melalui FastAPI dan SQLite.

## Implementasi

- `server/app.py`: endpoint GeoJSON dan pengaturan cache HTTP.
- `web/app.js`: pengambilan geometri, pratinjau vektor, mask berongga Leaflet, fitting batas, dan batasan validasi pin.
- `web/studio.css`: hierarki peta, panel inspeksi kandidat, pemilihan basemap, legenda, serta layout responsif. `web/styles.css` memuat kontrol dasar bersama.
- `tests/test_api.py`: kode wilayah, tipe geometri, penutupan poligon, serta pemisahan geometri dari pin kandidat.
- `tests/test_ui.py`, `tests/test_map_stack.py`: geometri dan posisi panel pada berbagai resolusi, mask, pemilihan basemap, atribusi dan larangan pin tanpa verifikasi. Tile online tidak diuji oleh fixture.

Peta visual yang tampak baik adalah **hasil desain antarmuka**, bukan validasi akurasi geospasial atau hasil rekayasa lalu lintas.