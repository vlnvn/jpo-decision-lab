# Keamanan dan privasi

Prototipe berjalan di browser tanpa autentikasi atau server. Data yang diketik berada di memori sesi dan hanya disimpan bila pengguna mengekspor JSON. Hindari memasukkan nama atau rekaman pribadi pejalan kaki ke aplikasi; data kamera semestinya dikonversi menjadi hitungan agregat oleh proses edge yang diuji dan berizin.

File JSON dari sumber luar diperlakukan sebagai input tak tepercaya: hasil perhitungan yang dikandungnya dibuang lalu harus dihitung ulang. Ini tidak membuktikan keamanan terhadap semua input berbahaya. Untuk kebutuhan lapangan diperlukan pembatasan akses, pengelolaan hak pengguna, retensi media, keamanan perangkat, validasi skema server, dan audit yang tahan manipulasi.

Kerentanan pada implementasi yang dipublikasikan sebaiknya dilaporkan ke pemilik repository secara privat, bukan melalui issue publik dengan data sensitif.