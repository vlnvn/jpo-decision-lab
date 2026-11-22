"""Research catalog, transcribed from the team's manuscript Table II.

These are the study's criterion DEFINITIONS, not local field measurements.
Changes to this catalog are a research-method change, not a UI customization.
"""
from __future__ import annotations

GROUPS = ["Keselamatan", "Kebutuhan Pejalan Kaki", "Aksesibilitas", "Kelayakan Teknis", "Ekonomi"]
CANDIDATES = [
    ("A1", "Area Unpad/BNI"),
    ("A2", "Simpang Ciseke/Sayang"),
    ("A3", "Depan ITB Jatinangor"),
    ("A4", "GKPN/IPDN — identitas titik belum dikonfirmasi"),
]
# group is 0-based; direction is the direction of priority to investigate, not desirability.
CRITERIA = [
 ("C1.1",0,"Riwayat kecelakaan pedestrian","Benefit","kejadian/tahun","Kejadian dalam ruang dan periode yang konsisten; sumber resmi"),
 ("C1.2",0,"Kecepatan kendaraan","Benefit","km/jam","Rata-rata atau persentil dari survei/perangkat terkalibrasi"),
 ("C1.3",0,"Volume lalu lintas","Benefit","kendaraan/jam","Penghitungan kendaraan dengan periode yang sebanding"),
 ("C1.4",0,"Kompleksitas penyeberangan","Benefit","lajur","Jumlah lajur aktif yang dilintasi"),
 ("C2.1",1,"Volume penyeberang","Benefit","orang/jam","Pedestrian yang benar-benar menyeberang"),
 ("C2.2",1,"Intensitas jam sibuk","Benefit","orang/15 menit","Puncak dalam jendela observasi 15 menit"),
 ("C3.1",2,"Jarak ke pusat aktivitas","Cost","m","Jarak berjalan/jaringan ke aktivitas atau fasilitas publik"),
 ("C3.2",2,"Jarak ke transportasi umum","Cost","m","Jarak berjalan ke titik layanan transportasi terdekat"),
 ("C4.1",3,"Ketersediaan ruang/lahan","Benefit","m²","Luas efektif untuk struktur dan akses setelah kajian"),
 ("C4.2",3,"Hambatan fisik/geometrik","Cost","ordinal 1–5","Skor audit lapangan; rubrik belum disetujui"),
 ("C4.3",3,"Kelayakan akses difabel","Benefit","ordinal 1–5","Skor rancangan akses inklusif; rubrik belum disetujui"),
 ("C5.1",4,"Estimasi biaya pembangunan","Cost","Rp","Biaya awal konstruksi dengan rincian cakupan"),
 ("C5.2",4,"Kebutuhan lahan tambahan","Cost","m²","Luas tanah tambahan yang mungkin perlu penanganan"),
 ("C5.3",4,"Estimasi biaya pemeliharaan","Cost","Rp/tahun","Perkiraan pemeliharaan tahunan"),
]


# Public landmark reference pins—not validated JPO crossing locations.
# Source coordinates describe the named landmark or road, NEVER the proposed bridge.
# Keeping these outside SQLite candidate records prevents accidental promotion to surveyed sites.
REFERENCE_AREAS = [
    {"candidate_id":"A1", "label":"Gerbang Unpad", "latitude":-6.9314972, "longitude":107.7762528,
     "source":"https://commons.wikimedia.org/wiki/File:Gerbang_Universitas_Padjadjaran_Jatinangor_(2024).jpg",
     "method":"Geotag foto gerbang Unpad 2024", "precision":"Landmark, bukan titik crossing", "verified_crossing":False},
    {"candidate_id":"A2", "label":"Jalan Ciseke", "latitude":-6.9327467, "longitude":107.7749886,
     "source":"https://peraturan.bpk.go.id/Download/323294/2.%20Perbup%20336%20Thn%202022%20ttg%20Batas%20Ds%20Hegarmanah%2C%20Kec.%20Jatinangor.pdf",
     "method":"Koordinat referensi Jalan Ciseke dari dokumen batas desa, tidak membuktikan posisi Simpang Ciseke/Sayang",
     "precision":"Koridor jalan, bukan titik crossing", "verified_crossing":False},
    {"candidate_id":"A3", "label":"Gerbang ITB Jatinangor", "latitude":-6.9280900, "longitude":107.7704500,
     "source":"https://p2k.stekom.ac.id/ensiklopedia/Kampus_ITB_Jatinangor",
     "method":"Koordinat referensi gerbang ITB Jatinangor dari direktori sekunder; perlu konfirmasi GPS lapangan",
     "precision":"Landmark perkiraan, bukan titik crossing", "verified_crossing":False},
    {"candidate_id":"A4", "label":"Gerbang PKD IPDN", "latitude":-6.9330625, "longitude":107.7635625,
     "source":"https://www.arsitag.com/project/videotron-gerbang-pkd-kampus-ipdn-jatinangor/photo/203405",
     "method":"Titik pusat plus code 3Q87+QC5 (referensi gerbang PKD), bukan koordinat GKPN ataupun titik crossing",
     "precision":"Landmark berbasis plus code, bukan titik crossing", "verified_crossing":False},
]

PAPER_TITLE = "Model Pendukung Keputusan untuk Memprioritaskan Lokasi Jembatan Penyeberangan Orang di Jatinangor"
PAPER_SOURCE = "Manuskrip kelompok, halaman 5–7, Tabel II dan Bagian IV–V"
REFERENCES = [
 {"id":"paper","label":"Paper kelompok — Tabel II","url":None,"role":"Definisi kriteria dan kandidat"},
 {"id":"speed","label":"Permenhub PM 111/2015 — aturan batas kecepatan","url":"https://jdih.kemenhub.go.id/peraturan/detail?data=05G3OMsYHZy1KUd8c5eOE38VyYryVUJ0c8m6xDzSKTZ38cNcwqcgz4ed4MRKP4tx4OVxjOjVbT44pH7luwUlV38W3hxIco9HU91PMr0iw8bU5cTvSFZ5jxo1rD6yylVzFwK1PTJOWYOYB","role":"Konteks regulasi, bukan distribusi kecepatan teramati"},
 {"id":"budget-kp","label":"Rencana anggaran JPO Kulon Progo 2024","url":"https://jdih.kulonprogokab.go.id/peraturan/2523/Salinan%2BSK-121-C-2024.pdf","role":"Contoh alokasi Rp3.082.633.000; bukan perkiraan biaya Jatinangor"},
 {"id":"budget-jkt","label":"RUP Dinas Bina Marga DKI Jakarta 2024","url":"https://www.jakarta.go.id/storage/files/shares/CSV/RUP/RUP%202024.pdf","role":"Contoh nilai paket multi-JPO; cakupan dan biaya per lokasi tidak diketahui"},
 {"id":"bps","label":"BPS — Kecamatan Jatinangor Dalam Angka 2026","url":"https://sumedangkab.bps.go.id/id/publication/2026/09/28/c1c3e8b08d871bd4bd577b35/kecamatan-jatinangor-dalam-angka-2026.html","role":"Konteks administrasi; bukan pengukuran 14 subkriteria"},
 {"id":"pedestrian","label":"Pedoman fasilitas pejalan kaki Permen PUPR 03/2014","url":"https://peraturan.bpk.go.id/Details/128205/permen-pupr-no-03prtm2014-tahun-2014","role":"Konteks perencanaan; bukan keputusan konstruksi otomatis"},
]