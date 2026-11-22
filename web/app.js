/* JPO Decision Lab client. State is fetched from the API, never inferred from local hardcoded observations. */
(() => {
    'use strict';
    const view = document.getElementById('content');
    const modal = document.getElementById('modal');
    const flashEl = document.getElementById('flash');
    const TITLES = { overview: 'Ikhtisar lokasi', measurements: 'Data penelitian', weights: 'Penilaian pakar', ranking: 'Pemeringkatan', observations: 'Observasi', audit: 'Riwayat & sumber' };
    let state = null;
    let screen = 'overview';
    let selectedCandidate = 'A1';
    let selectedExpert = null;
    let selectedLevel = 'main';
    let mapInstance = null;
    let activePinCandidate = null;
    const levelNames = { main: 'Lima kelompok kriteria', local0: 'Keselamatan', local1: 'Kebutuhan pejalan kaki', local2: 'Aksesibilitas', local3: 'Kelayakan teknis', local4: 'Ekonomi' };
    const levelSizes = { main: 5, local0: 4, local1: 2, local2: 2, local3: 3, local4: 3 };
    const NF = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 2 });
    const safe = value => String(value ?? '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
    const num = (v, d = 0) => Number(v).toLocaleString('id-ID', { minimumFractionDigits: d, maximumFractionDigits: d });
    const cl = v => v === null || v === undefined ? '—' : NF.format(v);
    const cById = id => state.candidates.find(c => c.id === id);
    const mode = () => state?.mode || 'empty';
    const modeLabel = () => ({ synthetic: 'SIMULASI', field: 'DATA INPUT MANUAL', empty: 'BELUM ADA DATA' })[mode()];
    const dataMap = () => new Map(state.measurements.map(r => [r.candidate_id + '|' + r.code, r]));
    function toast(message, err = false) { flashEl.textContent = message; flashEl.classList.toggle('error', err); flashEl.hidden = false; clearTimeout(toast.timer); toast.timer = setTimeout(() => { flashEl.hidden = true; }, 5200); }
    async function request(path, method = 'GET', payload) {
        let res;
        try {
            res = await fetch('/api' + path, { method, headers: payload ? { 'Content-Type': 'application/json' } : undefined, body: payload ? JSON.stringify(payload) : undefined });
        }
        catch (err) {
            throw new Error('API tidak dapat dihubungi. Jalankan server lokal sebelum membuka aplikasi.');
        }
        let data;
        try {
            data = await res.json();
        }
        catch {
            data = { detail: `HTTP ${res.status}` };
        }
        if (!res.ok) {
            const detail = data.detail;
            throw new Error(typeof detail === 'string' ? detail : typeof detail === 'object' ? JSON.stringify(detail) : `HTTP ${res.status}`);
        }
        return data;
    }
    async function mutate(path, method, payload, notice) {
        try {
            const result = await request(path, method, payload);
            state = result;
            render();
            if (notice)
                toast(notice);
            return true;
        }
        catch (err) {
            toast(err.message, true);
            return false;
        }
    }
    function head(index, title, desc, actions = '') {
        return `<div class="head"><div><div class="kicker">${safe(index)} / JPO DECISION LAB</div><h1>${safe(title)}</h1><p class="subheading">${safe(desc)}</p></div>${actions ? `<div class="head-actions">${actions}</div>` : ''}</div>`;
    }
    function button(action, label, kind = 'secondary', attrs = '') { return `<button type="button" class="btn ${kind}" data-action="${safe(action)}" ${attrs}>${safe(label)}</button>`; }
    function banner() {
        let text = mode() === 'synthetic' ? 'Seluruh nilai dan penilaian pakar merupakan skenario buatan untuk menguji perangkat lunak. Tidak ada data pengamatan Jatinangor di dalam skenario ini.' :
            mode() === 'field' ? 'Data yang dimasukkan pengguna belum diverifikasi oleh ahli transportasi. Peringkat hanya prioritas kajian, bukan keputusan membangun JPO.' :
                'Definisi kandidat dan kriteria bersumber dari manuskrip. Belum ada angka pengukuran atau bobot pakar yang diisikan.';
        return `<div class="mode-banner ${mode() === 'field' ? 'field' : ''}"><span class="tag">${modeLabel()}</span><div><b>${mode() === 'synthetic' ? 'Skenario pengujian aktif' : mode() === 'field' ? 'Workspace dengan data input' : 'Belum ada pengukuran'}</b><span>${text}</span></div></div>`;
    }
    function metrics() {
        const r = state.readiness;
        return `<div class="metrics"><div class="metric"><b class="value">${state.candidates.length}</b><span class="label">Kandidat awal</span></div><div class="metric"><b class="value">${state.criteria.length}</b><span class="label">Subkriteria paper</span></div><div class="metric"><b class="value">${r.measured}<span class="muted"> / ${r.expected}</span></b><span class="label">Nilai diperiksa</span></div><div class="metric"><b class="value">${r.coordinates_verified}<span class="muted"> / ${state.candidates.length}</span></b><span class="label">Koordinat terverifikasi</span></div></div>`;
    }
    function recentRun() { return state.runs[0] || null; }
    function registerRows() {
        return state.candidates.map(c => `<div class="register-row"><span class="location-code">${safe(c.id)}</span><div><p class="location-name">${safe(c.label)}</p><p class="location-meta">${c.coordinate_verified ? 'Titik GIS dengan sumber' : 'Koordinat belum terverifikasi'} · ${c.identity_verified ? 'Identitas diperiksa' : 'Identitas belum dikonfirmasi'}</p></div>${button('edit-candidate', 'Detail', 'secondary small', `data-id="${safe(c.id)}"`)}</div>`).join('');
    }
    function overview() {
        const actions = button('open-demo', 'Buat skenario uji', 'secondary') + button('clear', 'Kosongkan workspace', 'ghost');
        return head('01', 'Prioritas kajian lokasi penyeberangan', 'Dari data lokasi dan penilaian multikriteria menuju urutan kandidat yang dapat ditelusuri. Penentuan jenis fasilitas tetap memerlukan kajian rekayasa lalu lintas.', actions) + banner() + metrics() +
            `<div class="workspace-grid"><section class="panel"><div class="panel-title" style="padding:19px 21px 0"><h2>Peta kandidat</h2><span>Jatinangor, Kabupaten Sumedang</span></div><div class="map-wrap"><div id="map" class="map" aria-label="Peta kandidat yang koordinatnya telah diverifikasi"></div><div class="map-overlay"><b>${state.readiness.coordinates_verified ? `${state.readiness.coordinates_verified} titik sumber terverifikasi` : 'Belum ada pin kandidat'}</b><p>Pin muncul setelah koordinat beserta sumbernya diperiksa. Peta dasar bukan pengukuran lokasi penyeberangan.</p></div></div><div class="panel pad"><span class="note">Peta dasar © OpenStreetMap contributors. Perlu internet untuk memuat tile; tanpa koneksi, nilai penelitian tetap tersedia dari database lokal.</span></div></section>
      <section class="panel pad register"><div class="panel-title"><h2>Empat lokasi awal</h2><span>Bagian IV.A paper</span></div>${registerRows()}<div class="fineprint">A4 ditulis GKPN/IPDN di Bagian IV.A tetapi Pertigaan Hegarmanah/IPDN pada kesimpulan. Identitas titik harus disepakati sebelum pengumpulan data lapangan.</div></section></div>
      <div class="section-heading"><h2>Alur penelitian</h2><span>MODEL KONSEPTUAL / BAGIAN IV–V</span></div><div class="notice"><strong>01</strong> Data lapangan dan provenance → <strong>02</strong> Pembobotan Fuzzy AHP → <strong>03</strong> Peringkat TOPSIS → <strong>04</strong> Observasi agregat → <strong>05</strong> Uji perubahan peringkat. Tidak ada rekomendasi pembangunan otomatis.</div>`;
    }
    function measurements() {
        const cand = cById(selectedCandidate) || state.candidates[0];
        const records = dataMap();
        const rows = state.criteria.map(r => {
            const v = records.get(cand.id + '|' + r.code);
            return `<tr><td class="metadata">${safe(r.code)}</td><td><b>${safe(r.label)}</b><div class="note">${safe(state.groups[r.group_index])} · ${safe(r.direction)}</div></td><td class="num">${v ? num(v.value, Number.isInteger(v.value) ? 0 : 2) : '—'}</td><td>${safe(r.unit)}</td><td>${v ? `<span class="pill ${v.origin === 'synthetic' ? 'synthetic' : ''}">${v.origin === 'synthetic' ? 'Simulasi' : v.checked ? 'Diperiksa' : 'Draft'}</span>` : `<span class="pill missing">Belum ada</span>`}</td><td>${button('edit-measurement', v ? 'Lihat' : 'Isi', 'secondary small', `data-code="${safe(r.code)}" data-id="${safe(cand.id)}"`)}</td></tr>`;
        }).join('');
        return head('02', 'Data dan kelengkapan pengukuran', 'Matriks kandidat × subkriteria disimpan di SQLite. Setiap angka mempunyai satuan, periode, asal, dan status pemeriksaan.') + banner() +
            `<div class="split"><aside class="side-select" aria-label="Pilih kandidat">${state.candidates.map(c => `<button type="button" data-action="select-candidate" data-id="${safe(c.id)}" class="${cand.id === c.id ? 'chosen' : ''}"><b>${safe(c.id)}</b>${safe(c.label)}</button>`).join('')}</aside><section class="panel"><div class="panel pad"><div class="panel-title"><h2>${safe(cand.label)}</h2><span>${state.criteria.filter(r => records.get(cand.id + '|' + r.code)?.checked).length} / ${state.criteria.length} nilai diperiksa</span></div><p class="note">Nilai nol berbeda dari data yang belum tersedia. Urutan semua subkriteria sesuai Tabel II paper.</p></div><div class="table-scroll"><table class="data-table"><thead><tr><th>Kode</th><th>Indikator</th><th>Nilai</th><th>Unit</th><th>Status</th><th>Aksi</th></tr></thead><tbody>${rows}</tbody></table></div></section></div>`;
    }
    function selectOptions(items, current, allowBlank = false) { return (allowBlank ? '<option value="">Pilih…</option>' : '') + items.map(([value, label]) => `<option value="${safe(value)}" ${String(value) === String(current) ? 'selected' : ''}>${safe(label)}</option>`).join(''); }
    function levelCriteria() {
        if (selectedLevel === 'main')
            return state.groups;
        const idx = Number(selectedLevel.slice(-1));
        return state.criteria.filter(r => r.group_index === idx).map(r => `${r.code} ${r.label}`);
    }
    function weights() {
        if (!state.experts.length)
            selectedExpert = null;
        else if (!state.experts.some(e => e.id === Number(selectedExpert)))
            selectedExpert = state.experts[0].id;
        const expert = state.experts.find(e => e.id === Number(selectedExpert));
        const crit = levelCriteria();
        const existing = new Map(state.judgments.filter(j => j.expert_id === Number(selectedExpert) && j.level === selectedLevel).map(j => [`${j.pair_i}-${j.pair_j}`, j.intensity]));
        let rows = '';
        for (let i = 0; i < crit.length; i++)
            for (let j = i + 1; j < crit.length; j++) {
                const found = existing.get(`${i}-${j}`);
                const opts = [['', 'Belum diisi'], ...Array.from({ length: 8 }, (_, i) => [-(i + 2), `1/${i + 2} (kebalikan)`]), ...[1, 2, 3, 4, 5, 6, 7, 8, 9].map(n => [n, String(n)])];
                rows += `<tr><td>${safe(crit[i])}</td><td>${safe(crit[j])}</td><td><select class="pair-select" data-pair-i="${i}" data-pair-j="${j}">${selectOptions(opts, found, false)}</select></td></tr>`;
            }
        return head('03', 'Pembobotan dari penilaian pakar', 'Lima kelompok dibandingkan secara berpasangan; setiap kelompok mempunyai matriks lokal. Diagnostik konsistensi dilakukan sebelum bobot dipakai.') + banner() +
            `<div class="panel pad"><div class="form-inline"><div class="field"><label for="expert">Penilai</label><select id="expert">${selectOptions(state.experts.map(e => [e.id, e.name]), selectedExpert, true)}</select></div><div class="field"><label for="level">Matriks penilaian</label><select id="level">${selectOptions(Object.entries(levelNames), selectedLevel)}</select></div><button type="button" class="btn secondary" data-action="add-expert">Tambah penilai</button></div></div>
     <div class="section-heading"><h2>${safe(levelNames[selectedLevel])}</h2><span>${rows.match(/<tr>/g)?.length || 0} PERBANDINGAN</span></div><div class="panel"><div class="table-scroll"><table class="pairs-table"><thead><tr><th>Indikator A</th><th>Indikator B</th><th>Skala Saaty</th></tr></thead><tbody>${rows || '<tr><td colspan="3">Belum ada kriteria</td></tr>'}</tbody></table></div><div class="panel pad"><div class="section-actions">${button('save-judgments', 'Simpan matriks', 'primary', (!expert || mode() === 'synthetic') ? 'disabled' : '')}${mode() === 'synthetic' ? '<span class="note">Bobot simulasi dibuat oleh generator; untuk penilaian asli, kosongkan workspace.</span>' : ''}</div></div></div><p class="footnote">Konvensi numerik Buckley geometric mean, skala triangular dan ambang CR crisp ≤0,10 adalah keputusan implementasi; naskah penelitian belum mengunci varian Fuzzy AHP. Penilaian 1 berarti sama penting, 2–9 berarti A lebih penting, kebalikan berarti B lebih penting.</p>`;
    }
    function ranking() {
        const run = recentRun(), r = run?.result;
        const records = r?.topsis?.ranked || [];
        let output = !run ? `<div class="empty-panel"><b>Belum ada hasil perhitungan</b><p>Lengkapi seluruh nilai dan penilaian pakar, lalu jalankan TOPSIS. Sistem tidak membuat nilai hasil otomatis.</p></div>` :
            `<div class="panel pad" style="margin-bottom:17px"><div class="panel-title"><h2>Urutan prioritas kajian</h2><span class="pill ${run.mode === 'synthetic' ? 'synthetic' : ''}">${safe(run.mode === 'synthetic' ? 'Simulasi' : 'Input pengguna')}</span></div>${run.stale ? '<div class="mode-banner"><b>Hasil tidak mutakhir — nilai atau penilaian telah berubah. Jalankan ulang perhitungan.</b></div>' : ''}${r.data_quality?.period_warnings?.length ? `<div class="mode-banner"><div><b>Peringatan: periode tidak seragam pada ${r.data_quality.period_warnings.length} indikator.</b><span>Hasil masih bersifat eksploratif. Samakan jendela observasi antarlokasi sebelum membuat kesimpulan lapangan.</span></div></div>` : ''}<div class="table-scroll"><table class="rank-table"><thead><tr><th>Rank</th><th>Kandidat</th><th>Skor C*</th><th>Indikator visual</th></tr></thead><tbody>${records.map(rec => `<tr><td class="rank-no">${rec.rank.toString().padStart(2, '0')}</td><td>${safe(cById(rec.candidate_id)?.label || rec.candidate_id)}</td><td class="rank-score">${num(rec.score, 4)}</td><td><div class="score-track"><span style="width:${Math.max(0, Math.min(100, rec.score * 100))}%"></span></div></td></tr>`).join('')}</tbody></table></div><p class="footnote">Koefisien TOPSIS ini adalah prioritas kajian menurut data dan bobot yang diberikan, bukan probabilitas kecelakaan atau rekomendasi konstruksi.</p></div>
     <div class="run-grid"><div class="panel pad"><div class="panel-title"><h2>Bobot global</h2><span>Jumlah = 1</span></div><div class="table-scroll"><table><thead><tr><th>Kode</th><th>Indikator</th><th>Bobot</th></tr></thead><tbody>${state.criteria.map((c, i) => `<tr><td class="metadata">${safe(c.code)}</td><td>${safe(c.label)}</td><td class="num">${num(r.weights.weights[i] * 100, 2)}%</td></tr>`).join('')}</tbody></table></div></div><div class="panel pad"><h2>Ketahanan hasil</h2><p class="subheading">Setiap bobot kelompok dinaikkan atau diturunkan 10%, kemudian seluruh bobot dinormalisasi kembali.</p><p class="note">${r.sensitivity.filter(s => s.leader_changed).length} dari ${r.sensitivity.length} skenario mengubah peringkat teratas. Perubahan ini diuji pada dataset saat perhitungan disimpan.</p><hr class="rule"><h3>AHP konvensional</h3><p class="note">Urutan pembanding: ${r.ahp_comparison.ranked.map(x => safe(cById(x.candidate_id)?.label || x.candidate_id)).join(' · ')}</p><hr class="rule"><h3>Diagnostik konsistensi</h3>${r.weights.diagnostics.map(x => `<p class="metadata">${safe(x.expert)} · ${safe(levelNames[x.level])}: CR ${num(x.cr * 100, 2)}%</p>`).join('')}</div></div>`;
        return head('04', 'Pemeringkatan kandidat', 'Hasil TOPSIS dihitung di server, dari matriks yang telah diperiksa dan bobot pakar; setiap hasil memiliki snapshot dan tanda perubahan data.', button('run-ranking', 'Jalankan perhitungan', 'primary')) + banner() + output;
    }
    function observations() {
        const obs = state.observations;
        const options = state.candidates.map(c => [c.id, `${c.id} — ${c.label}`]);
        const notReady = !state.runs.length;
        return head('05', 'Observasi untuk validasi', 'Data agregat pengamatan memperbarui indikator dinamis, kemudian peringkat dibandingkan kembali. Video mentah dan deteksi kamera fisik belum terintegrasi.') + banner() +
            `<div class="run-grid"><section class="panel pad"><div class="panel-title"><h2>Catat observasi</h2><span>C1.3 · C2.1 · C2.2</span></div><form id="observation-form" class="grid-form"><div class="field wide"><label for="o-location">Lokasi</label><select id="o-location" name="candidate_id">${selectOptions(options, selectedCandidate)}</select></div><div class="field"><label for="o-ped">Penyeberang / jam</label><input type="number" id="o-ped" name="pedestrians_hour" min="0" step="1" required></div><div class="field"><label for="o-peak">Puncak / 15 menit</label><input type="number" id="o-peak" name="peak_15min" min="0" step="1" required></div><div class="field"><label for="o-vehicles">Kendaraan / jam</label><input type="number" id="o-vehicles" name="vehicles_hour" min="0" step="1" required></div><div class="field"><label for="o-speed">Kecepatan km/jam (opsional)</label><input type="number" id="o-speed" name="speed_kmh" min="0" max="250" step="0.1"></div><div class="field wide"><label class="check"><input type="checkbox" name="calibrated"> Kecepatan telah diukur dengan alat terkalibrasi (C1.2)</label></div><div class="field wide"><label for="o-source">Asal data / instrumen</label><input id="o-source" name="source" placeholder="Contoh: survei manual; lokasi dan tanggal" required minlength="4"></div><div class="field wide"><label for="o-period">Periode pengamatan</label><input id="o-period" name="period" placeholder="Tanggal dan jam, zona waktu" required minlength="3"></div><div class="form-actions field wide"><button type="submit" class="btn" ${notReady ? 'disabled' : ''}>Simpan observasi</button></div></form>${notReady ? '<p class="note">Hitung peringkat awal lebih dahulu agar validasi punya baseline yang jelas.</p>' : ''}</section>
      <aside class="panel pad"><h2>Aturan pembaruan</h2><ul class="analysis-list"><li>Jumlah kendaraan memperbarui C1.3.</li><li>Jumlah penyeberang dan puncak 15 menit memperbarui C2.1 dan C2.2.</li><li>Kecepatan hanya memperbarui C1.2 jika sumber terkalibrasi.</li><li>Pembaharuan dibuat eksplisit dan dicatat di audit.</li><li>Setelah observasi diterapkan, jalankan TOPSIS lagi untuk menilai perubahan.</li></ul><hr class="rule"><p class="note">Penggunaan data sintetis tetap diberi label simulasi meskipun penghitungan ulang berjalan. Tidak ada klaim bahwa kamera sedang aktif.</p></aside></div>
      <div class="section-heading"><h2>Riwayat observasi</h2><span>${obs.length} CATATAN</span></div><div class="panel table-scroll"><table><thead><tr><th>Waktu</th><th>Lokasi</th><th>Pedestrian/jam</th><th>Kendaraan/jam</th><th>Asal</th><th>Status</th></tr></thead><tbody>${obs.length ? obs.map(o => `<tr><td class="metadata">${safe(o.created_at)}</td><td>${safe(o.candidate_id)}</td><td>${cl(o.pedestrians_hour)}</td><td>${cl(o.vehicles_hour)}</td><td>${o.origin === 'synthetic' ? 'Simulasi' : 'Input pengguna'}</td><td>${o.applied ? '<span class="pill">Diterapkan</span>' : button('apply-observation', 'Terapkan', 'secondary small', `data-id="${o.id}"`)}</td></tr>`).join('') : '<tr><td colspan="6" class="empty-panel">Belum ada catatan observasi.</td></tr>'}</tbody></table></div>`;
    }
    function audit() {
        const last = recentRun();
        return head('06', 'Riwayat dan rujukan', 'Jejak perhitungan, perubahan data, dan rujukan yang digunakan untuk menyusun skenario demonstrasi.', button('export', 'Unduh JSON', 'secondary')) + banner() +
            `<div class="section-heading"><h2>Aktivitas penelitian</h2><span>60 ENTRI TERAKHIR</span></div><div class="panel table-scroll"><table class="table-small"><thead><tr><th>Waktu (UTC)</th><th>Tindakan</th><th>Rincian</th></tr></thead><tbody>${state.audit.length ? state.audit.map(a => `<tr><td class="metadata no-wrap">${safe(a.created_at)}</td><td>${safe(a.action)}</td><td class="source-cell" title="${safe(a.payload)}">${safe(a.payload)}</td></tr>`).join('') : '<tr><td colspan="3" class="empty-panel">Belum ada aktivitas.</td></tr>'}</tbody></table></div><div class="section-heading"><h2>Referensi data & metode</h2><span>PROVENANCE</span></div><div class="ref-list">${state.references.map(ref => `<article class="ref-item"><h3>${safe(ref.label)}</h3><p>${safe(ref.role)}</p>${ref.url ? `<a target="_blank" rel="noreferrer" href="${safe(ref.url)}">Lihat sumber</a>` : '<span class="metadata">Manuskrip kelompok yang mendasari model</span>'}</article>`).join('')}</div><div class="section-heading"><h2>Batas penggunaan</h2></div><div class="notice">Biaya pembangunan dalam skenario sintetis mengambil kisaran ilustratif dari skala anggaran proyek publik di wilayah lain—tanpa mengasumsikan biaya Jatinangor sama. Nilai volume pejalan kaki, kendaraan, hambatan, dan luas lahan adalah asumsi eksplisit, bukan hasil observasi atau estimasi statistik populasi.</div>`;
    }
    function render() {
        if (!state)
            return;
        if (mapInstance) {
            try {
                mapInstance.remove();
            }
            catch { }
            mapInstance = null;
        }
        document.getElementById('breadcrumb').textContent = TITLES[screen];
        document.querySelectorAll('[data-screen]').forEach(el => el.classList.toggle('active', el.dataset.screen === screen));
        document.getElementById('api-status').textContent = 'Server lokal · tersambung';
        document.getElementById('api-status').className = 'connection online';
        const routes = { overview, measurements, weights, ranking, observations, audit };
        view.innerHTML = routes[screen]();
        if (screen === 'overview')
            requestAnimationFrame(initMap);
        if (screen === 'weights') {
            document.getElementById('expert')?.addEventListener('change', e => { selectedExpert = Number(e.target.value); render(); });
            document.getElementById('level')?.addEventListener('change', e => { selectedLevel = e.target.value; render(); });
        }
        document.getElementById('observation-form')?.addEventListener('submit', saveObservation);
    }
    function initMap() {
        const target = document.getElementById('map');
        if (!target)
            return;
        if (!window.L) {
            target.innerHTML = '<div class="map-fallback">Peta membutuhkan koneksi internet untuk memuat Leaflet dan tile OSM.<br>Koordinat tetap dapat diisi melalui Detail lokasi.</div>';
            return;
        }
        const L = window.L;
        mapInstance = L.map(target, { scrollWheelZoom: false, zoomControl: true, attributionControl: true }).setView([-6.929, 107.773], 13);
        const tileTemplate = window.JPO_TILE_URL || 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
        L.tileLayer(tileTemplate, { maxZoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(mapInstance);
        const verified = state.candidates.filter(c => c.coordinate_verified && Number.isFinite(c.latitude) && Number.isFinite(c.longitude));
        const markers = verified.map(c => {
            const m = L.marker([c.latitude, c.longitude], { icon: L.divIcon({ className: '', html: `<div class="map-pin">${safe(c.id.slice(1))}</div>`, iconSize: [31, 31], iconAnchor: [15, 15] }) }).addTo(mapInstance);
            m.bindPopup(`<b>${safe(c.id)} · ${safe(c.label)}</b><div style="font-size:12px">Sumber: ${safe(c.coordinate_source)}</div>`);
            return m;
        });
        if (markers.length >= 2)
            mapInstance.fitBounds(L.featureGroup(markers).getBounds().pad(.28));
        else if (markers.length === 1)
            mapInstance.setView(markers[0].getLatLng(), 15);
        mapInstance.on('click', e => {
            // Clicking the map can only create a draft coordinate; it NEVER self-verifies the pin.
            activePinCandidate = state.candidates.find(c => !c.coordinate_verified)?.id || state.candidates[0]?.id;
            if (activePinCandidate)
                openCandidate(activePinCandidate, e.latlng.lat, e.latlng.lng);
        });
    }
    function open(html) { document.getElementById('modal-content').innerHTML = `<div class="modal-inner">${html}</div>`; modal.showModal(); }
    function close() { modal.close(); }
    function openCandidate(id, latitude, longitude) {
        const c = cById(id);
        if (!c)
            return;
        open(`<h2>${safe(c.id)} · Detail kandidat</h2><p>Koordinat baru tidak otomatis terverifikasi. Pastikan titik dan asalnya sesuai lokasi penyeberangan, bukan sekadar bangunan di sekitarnya.</p><form id="candidate-form" class="grid-form"><input type="hidden" name="candidate_id" value="${safe(id)}"><div class="field wide"><label>Nama titik / ruas</label><input name="label" value="${safe(c.label)}" required minlength="3"></div><div class="field"><label>Lintang</label><input name="latitude" type="number" step="any" min="-90" max="90" value="${latitude ?? c.latitude ?? ''}"></div><div class="field"><label>Bujur</label><input name="longitude" type="number" step="any" min="-180" max="180" value="${longitude ?? c.longitude ?? ''}"></div><div class="field wide"><label>Sumber koordinat</label><input name="coordinate_source" maxlength="500" placeholder="Survei GPS / tautan OpenStreetMap / catatan lapangan" value="${safe(c.coordinate_source || '')}"></div><div class="field wide"><label>Catatan perbedaan lokasi atau nama</label><textarea name="note" maxlength="700">${safe(c.note || '')}</textarea></div><div class="field wide"><label class="check"><input type="checkbox" name="identity_verified" ${c.identity_verified ? 'checked' : ''}> Nama dan definisi titik sudah dikonfirmasi tim</label><label class="check"><input type="checkbox" name="coordinate_verified" ${c.coordinate_verified ? 'checked' : ''}> Saya memeriksa titik ini dan sumber koordinatnya</label></div><div class="field wide form-actions"><button type="button" class="btn secondary" data-action="close-modal">Batal</button><button type="submit" class="btn">Simpan kandidat</button></div></form>`);
        document.getElementById('candidate-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const x = new FormData(e.currentTarget);
            const lat = x.get('latitude'), lon = x.get('longitude');
            const data = { label: x.get('label'), latitude: lat !== '' ? Number(lat) : null, longitude: lon !== '' ? Number(lon) : null, coordinate_source: x.get('coordinate_source') || null, note: x.get('note'), identity_verified: x.has('identity_verified'), coordinate_verified: x.has('coordinate_verified') };
            if (await mutate(`/candidates/${encodeURIComponent(id)}`, 'PUT', data, 'Kandidat diperbarui.'))
                close();
        });
    }
    function openMeasurement(id, code) {
        const c = cById(id);
        const crit = state.criteria.find(x => x.code === code), r = dataMap().get(id + '|' + code);
        open(`<h2>${safe(code)} · ${safe(crit.label)}</h2><p>${safe(c.label)} · ${safe(crit.definition)}</p><form id="measurement-form" class="grid-form"><div class="field"><label>Nilai (${safe(crit.unit)})</label><input type="number" name="value" min="0" step="any" value="${r?.value ?? ''}" required ${mode() === 'synthetic' ? 'disabled' : ''}></div><div class="field"><label>Arah prioritas</label><input value="${safe(crit.direction)}" disabled></div><div class="field wide"><label>Asal data / instrumen</label><textarea name="source" required maxlength="1000" ${mode() === 'synthetic' ? 'disabled' : ''}>${safe(r?.source || '')}</textarea></div><div class="field wide"><label>Periode, cakupan atau metode</label><input name="period" maxlength="200" value="${safe(r?.period || '')}" required ${mode() === 'synthetic' ? 'disabled' : ''}></div><div class="field wide"><label class="check"><input type="checkbox" name="checked" ${r?.checked ? 'checked' : ''} ${mode() === 'synthetic' ? 'disabled' : ''}> Satuan, periode, dan sumber sudah ditinjau</label></div><div class="field wide form-actions"><button type="button" class="btn secondary" data-action="close-modal">Tutup</button>${mode() !== 'synthetic' ? '<button type="submit" class="btn">Simpan data</button>' : ''}</div></form>`);
        document.getElementById('measurement-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            if (await mutate('/measurements', 'PUT', { candidate_id: id, code, value: Number(f.get('value')), source: f.get('source'), period: f.get('period'), checked: f.has('checked') }, 'Data di basis data diperbarui.'))
                close();
        });
    }
    function openDemo() {
        open(`<h2>Skenario demonstrasi</h2><p>Mengganti seluruh data, bobot, dan hasil sebelumnya. Angka dibuat dengan seed deterministik dan seluruhnya ditandai sebagai sintetis. Tidak merepresentasikan lokasi nyata.</p><form id="demo-form"><div class="field"><label>Seed simulasi (untuk reproduksi)</label><input name="seed" type="number" min="1" max="999999" value="202611" required></div><div class="form-actions"><button class="btn secondary" type="button" data-action="close-modal">Batal</button><button class="btn" type="submit">Buat dataset sintetis</button></div></form>`);
        document.getElementById('demo-form').addEventListener('submit', async (e) => { e.preventDefault(); const seed = Number(new FormData(e.currentTarget).get('seed')); if (await mutate('/workspace/demo', 'POST', { seed, confirm: 'REPLACE_WORKSPACE_WITH_SYNTHETIC' }, 'Dataset sintetis dimuat dari generator terulang.'))
            close(); });
    }
    async function saveObservation(e) {
        e.preventDefault();
        const f = new FormData(e.currentTarget);
        const v = f.get('speed_kmh');
        const input = { candidate_id: f.get('candidate_id'), pedestrians_hour: Number(f.get('pedestrians_hour')), peak_15min: Number(f.get('peak_15min')), vehicles_hour: Number(f.get('vehicles_hour')), speed_kmh: v !== '' ? Number(v) : null, calibrated: f.has('calibrated'), source: f.get('source'), period: f.get('period') };
        await mutate('/observations', 'POST', input, 'Observasi tercatat. Klik Terapkan untuk pembaruan nilai.');
    }
    async function saveJudgments() {
        if (!selectedExpert) {
            toast('Tambahkan penilai dahulu.', true);
            return;
        }
        const selects = [...view.querySelectorAll('[data-pair-i]')];
        const pairs = selects.filter(x => x.value).map(x => ({ level: selectedLevel, i: Number(x.dataset.pairI), j: Number(x.dataset.pairJ), intensity: Number(x.value) }));
        await mutate('/judgments', 'PUT', { expert_id: Number(selectedExpert), pairs }, 'Penilaian disimpan.');
    }
    async function openAddExpert() {
        open('<h2>Tambahkan penilai</h2><p>Gunakan identitas penilai yang sebenarnya, bukan nilai simulasi. Penilaian tidak otomatis lengkap.</p><form id="expert-form"><div class="field"><label>Nama atau kode penilai</label><input name="name" minlength="3" maxlength="90" required></div><div class="form-actions"><button class="btn secondary" type="button" data-action="close-modal">Batal</button><button type="submit" class="btn">Tambahkan</button></div></form>');
        document.getElementById('expert-form').addEventListener('submit', async (e) => { e.preventDefault(); const name = new FormData(e.currentTarget).get('name'); if (await mutate('/experts', 'POST', { name }, 'Penilai ditambahkan.')) {
            selectedExpert = state.experts.at(-1).id;
            close();
            render();
        } });
    }
    function download() { window.location.href = '/api/export'; }
    async function onAction(event) {
        const target = event.target.closest('[data-action], [data-screen]');
        if (!target)
            return;
        if (target.dataset.screen) {
            screen = target.dataset.screen;
            render();
            window.scrollTo(0, 0);
            return;
        }
        const action = target.dataset.action;
        if (action === 'edit-candidate')
            openCandidate(target.dataset.id);
        else if (action === 'edit-measurement')
            openMeasurement(target.dataset.id, target.dataset.code);
        else if (action === 'select-candidate') {
            selectedCandidate = target.dataset.id;
            render();
        }
        else if (action === 'open-demo')
            openDemo();
        else if (action === 'close-modal')
            close();
        else if (action === 'clear') {
            if (window.confirm('Hapus semua pengukuran, bobot, observasi, dan hasil dalam workspace lokal ini? Unduh JSON lebih dahulu bila diperlukan.'))
                await mutate('/workspace/clear', 'POST', { confirm: 'CLEAR_ALL_RESEARCH_DATA' }, 'Workspace dikosongkan.');
        }
        else if (action === 'add-expert')
            openAddExpert();
        else if (action === 'save-judgments')
            saveJudgments();
        else if (action === 'run-ranking')
            await mutate('/rankings', 'POST', {}, 'Perhitungan dan snapshot disimpan.');
        else if (action === 'apply-observation')
            await mutate(`/observations/${target.dataset.id}/apply`, 'POST', {}, 'Nilai diperbarui; jalankan TOPSIS kembali untuk membandingkan.');
        else if (action === 'export')
            download();
    }
    document.addEventListener('click', onAction);
    modal.addEventListener('click', event => { if (event.target === modal)
        close(); });
    document.getElementById('export-global').addEventListener('click', download);
    async function start() {
        try {
            state = await request('/workspace');
            render();
        }
        catch (err) {
            view.innerHTML = `<div class="head"><div><h1>Layanan belum berjalan</h1><p class="subheading">${safe(err.message)}</p><p class="note">Mulai dengan <code>python -m uvicorn server.app:app --host 127.0.0.1 --port 8000</code>, kemudian buka http://127.0.0.1:8000.</p></div></div>`;
            document.getElementById('api-status').className = 'connection offline';
            document.getElementById('api-status').textContent = 'API tidak tersambung';
        }
    }
    start();
})();