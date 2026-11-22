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
    let geography = null; // versioned reference geometry from API; not an observed JPO coordinate
    let activePinCandidate = null;
    let boundaryMask = null;
    let boundaryLayer = null;
    let mapMasked = true;
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
        return state.candidates.map((c, i) => `<div class="register-row"><span class="location-code">${safe(c.id)}</span><div class="location-details"><p class="location-name">${safe(c.label)}</p><p class="location-meta">${c.coordinate_verified ? 'Koordinat tervalidasi oleh tim' : 'Titik penyeberangan belum ditetapkan'}${c.identity_verified ? ' · Identitas diperiksa' : ''}</p></div><button type="button" class="location-action" aria-label="Lihat detail ${safe(c.label)}" data-action="edit-candidate" data-id="${safe(c.id)}">↗</button></div>`).join('');
    }
    function workflow() {
        const steps = [['measurements', '01', 'Lengkapi data', '4 lokasi × 14 indikator'], ['weights', '02', 'Bobot pakar', 'Perbandingan Fuzzy AHP'], ['ranking', '03', 'Prioritas kajian', 'Hasil TOPSIS'], ['observations', '04', 'Validasi lapangan', 'Agregat observasi'], ['audit', '05', 'Jejak keputusan', 'Data & perhitungan']];
        return `<div class="workflow-heading"><div><span class="section-overline">ALUR PENGGUNA</span><h2>Dari pengukuran menuju keputusan yang bisa ditelusuri</h2></div><span class="workflow-source">Berdasarkan Bagian IV–V paper kelompok</span></div><div class="workflow-steps">${steps.map(([id, code, title, detail], i) => `<button type="button" class="workflow-step" data-screen="${id}"><span class="step-num">${code}</span><span><b>${title}</b><small>${detail}</small></span><span aria-hidden="true" class="step-arrow">↗</span></button>`).join('')}</div>`;
    }
    function overview() {
        const actions = button('open-demo', 'Buat skenario uji', 'primary') + button('clear', 'Reset workspace', 'ghost');
        return `<div class="overview-head">${head('STUDI KAWASAN', 'Jatinangor, dalam satu peta.', 'Tentukan lokasi yang perlu dikaji lebih dulu dengan data terukur, bobot pakar, dan pemeringkatan yang dapat dijelaskan.', actions)}</div>` + banner() +
            `<div class="map-layout"><section class="map-surface" aria-labelledby="map-heading"><div class="map-topline"><div><div class="section-overline">WILAYAH STUDI / 32.11.15</div><h2 id="map-heading">Kecamatan Jatinangor</h2></div><div class="map-controls"><span class="map-live-dot" aria-hidden="true"></span><span class="map-source-type">Batas wilayah disederhanakan</span><button type="button" class="map-control" data-action="toggle-mask" id="toggle-mask" aria-pressed="${mapMasked}">Area luar: ${mapMasked ? 'redup' : 'terang'}</button><button type="button" class="map-control solid" data-action="focus-region">Fokus wilayah ↗</button></div></div><div class="map-stage" id="map-stage"><div class="map-underlay" id="map-underlay" aria-hidden="true"></div><div id="map" class="map" aria-label="Peta interaktif Kecamatan Jatinangor; klik lokasi hanya saat mode pemilihan titik diaktifkan"></div><div class="map-floating-caption"><span class="map-caption-label">CAKUPAN STUDI</span><strong>Kecamatan Jatinangor</strong><span>Kabupaten Sumedang · Jawa Barat</span><div class="map-caption-rule"></div><span>Area luar diarsir agar fokus tetap pada wilayah penelitian.</span></div><div class="map-legend"><span><i class="legend-swatch in"></i> Dalam kecamatan</span><span><i class="legend-swatch out"></i> Di luar cakupan</span></div><div class="map-north" aria-hidden="true">N <span>↑</span></div></div><div class="map-footnote"><span><strong>Geometri:</strong> cahyadsn, versi disederhanakan · bukan batas legal atau lokasi survei</span><span>Basemap: © OpenStreetMap · © CARTO (saat tersedia)</span></div></section>
            <aside class="candidate-surface"><div class="candidate-head"><span class="section-overline">ALTERNATIF PENELITIAN</span><h2>Empat lokasi awal</h2><p>Daftar kandidat dari paper; titik koordinat baru ditampilkan apabila sudah diperiksa.</p></div><div class="candidate-list">${registerRows()}</div><div class="candidate-bottom"><div class="candidate-progress-head"><span>Persiapan koordinat</span><b>${state.readiness.coordinates_verified} dari ${state.candidates.length}</b></div><div class="candidate-progress"><i style="width:${state.candidates.length ? (100 * state.readiness.coordinates_verified / state.candidates.length) : 0}%"></i></div><p>${state.readiness.coordinates_verified ? 'Hanya titik dengan sumber koordinat yang muncul pada peta.' : 'Peta wilayah tetap tersedia tanpa memasang pin yang belum terbukti.'}</p><div class="candidate-warning">Nama kandidat A4 berbeda antara Bagian IV.A dan kesimpulan. Perlu konfirmasi sebelum survei.</div></div></aside></div>
            <div class="overview-metrics">${metrics()}</div>${workflow()}`;
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
        const leader = records[0];
        const leadHtml = leader ? `<div class="ranking-lead"><div><span class="section-overline">PRIORITAS KAJIAN / URUTAN 01</span><h2>${safe(cById(leader.candidate_id)?.label || leader.candidate_id)}</h2><p>Alternatif teratas menurut bobot dan data pada run ini. Peringkat tidak menggantikan penilaian kelayakan JPO.</p></div><div class="ranking-lead-score"><span>Koefisien TOPSIS</span><b>${num(leader.score,4)}</b><small>Skala relatif 0–1</small></div></div>` : '';
        let output = !run ? `<div class="empty-panel"><b>Belum ada hasil perhitungan</b><p>Lengkapi seluruh nilai dan penilaian pakar, lalu jalankan TOPSIS. Sistem tidak membuat nilai hasil otomatis.</p></div>` :
            `${leadHtml}<div class="panel pad" style="margin-bottom:17px"><div class="panel-title"><h2>Urutan prioritas kajian</h2><span class="pill ${run.mode === 'synthetic' ? 'synthetic' : ''}">${safe(run.mode === 'synthetic' ? 'Simulasi' : 'Input pengguna')}</span></div>${run.stale ? '<div class="mode-banner"><b>Hasil tidak mutakhir — nilai atau penilaian telah berubah. Jalankan ulang perhitungan.</b></div>' : ''}${r.data_quality?.period_warnings?.length ? `<div class="mode-banner"><div><b>Peringatan: periode tidak seragam pada ${r.data_quality.period_warnings.length} indikator.</b><span>Hasil masih bersifat eksploratif. Samakan jendela observasi antarlokasi sebelum membuat kesimpulan lapangan.</span></div></div>` : ''}<div class="table-scroll"><table class="rank-table"><thead><tr><th>Rank</th><th>Kandidat</th><th>Skor C*</th><th>Indikator visual</th></tr></thead><tbody>${records.map(rec => `<tr><td class="rank-no">${rec.rank.toString().padStart(2, '0')}</td><td>${safe(cById(rec.candidate_id)?.label || rec.candidate_id)}</td><td class="rank-score">${num(rec.score, 4)}</td><td><div class="score-track"><span style="width:${Math.max(0, Math.min(100, rec.score * 100))}%"></span></div></td></tr>`).join('')}</tbody></table></div><p class="footnote">Koefisien TOPSIS ini adalah prioritas kajian menurut data dan bobot yang diberikan, bukan probabilitas kecelakaan atau rekomendasi konstruksi.</p></div>
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
    function districtRing() {
        const f = geography?.features?.find(x => x.properties?.code === '32.11.15');
        const ring = f?.geometry?.type === 'Polygon' ? f.geometry.coordinates?.[0] : null;
        return Array.isArray(ring) && ring.length >= 4 ? ring : null;
    }
    function insideDistrict(lat, lng) {
        const pts = districtRing();
        if (!pts) return false;
        let inside = false;
        for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
            const [xi, yi] = pts[i], [xj, yj] = pts[j];
            if ((yi > lat) !== (yj > lat) && lng < (xj - xi) * (lat - yi) / (yj - yi) + xi) inside = !inside;
        }
        return inside;
    }
    function renderBoundaryIllustration() {
        const el = document.getElementById('map-underlay');
        if (!el) return;
        const pts = districtRing();
        if (!pts) { el.innerHTML = '<div class="map-no-geometry"><strong>Batas wilayah tidak tersedia.</strong><span>Coba muat ulang aplikasi; peta tidak menggunakan poligon perkiraan.</span></div>'; return; }
        const lon = pts.map(c => c[0]), lat = pts.map(c => c[1]);
        const midX = (Math.min(...lon) + Math.max(...lon)) / 2, midY = (Math.min(...lat) + Math.max(...lat)) / 2;
        const scale = Math.min(430 / (Math.max(...lon) - Math.min(...lon)), 465 / (Math.max(...lat) - Math.min(...lat)));
        const xy = ([x,y]) => [545 + (x-midX)*scale, 318 - (y-midY)*scale];
        const polygon = pts.map((p,i) => (i?'L':'M') + xy(p).map(n=>n.toFixed(1)).join(',')).join(' ')+' Z';
        const [cx,cy] = xy([midX,midY]);
        el.innerHTML = `<svg class="district-illustration" viewBox="0 0 1050 650" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Visualisasi batas kecamatan Jatinangor yang disederhanakan; tidak menunjukkan jalan atau koordinat kandidat"><defs><pattern id="carto-grid" width="62" height="62" patternUnits="userSpaceOnUse"><path d="M62 0H0V62" fill="none" stroke="#c6d0cb" stroke-width=".7"/></pattern><pattern id="carto-dots" width="13" height="13" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".75" fill="#abbab2" opacity=".6"/></pattern><filter id="district-shadow" x="-40%" y="-40%" width="180%" height="180%"><feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="#224c43" flood-opacity=".16"/></filter><clipPath id="district-clip"><path d="${polygon}"/></clipPath></defs><rect width="1050" height="650" fill="#e5eae7"/><rect width="1050" height="650" fill="url(#carto-grid)"/><rect width="1050" height="650" fill="url(#carto-dots)" opacity=".38"/><g opacity=".32" stroke="#becac4" fill="none" stroke-width="1.1"><path d="M-30 180Q150 125 275 220T620 192T1100 150"/><path d="M-35 470Q125 420 300 500T670 490T1100 395"/></g><path d="${polygon}" fill="#d8e8de" stroke="#fff" stroke-width="16" filter="url(#district-shadow)"/><path d="${polygon}" fill="#c9e2d3" stroke="#286951" stroke-width="3.3"/><g clip-path="url(#district-clip)"><rect width="1050" height="650" fill="url(#carto-grid)" opacity=".45"/></g><g transform="translate(${cx.toFixed(1)} ${cy.toFixed(1)})"><circle r="4" fill="#1e6349"/><circle r="13" fill="none" stroke="#2b7458" stroke-opacity=".35"/><text x="0" y="-29" text-anchor="middle" fill="#1b4d3f" font-size="23" font-family="Segoe UI,sans-serif" font-weight="700" letter-spacing="2">JATINANGOR</text><text x="0" y="35" text-anchor="middle" fill="#466f5d" font-size="12" letter-spacing="1.5">KECAMATAN · 32.11.15</text></g><g fill="#788a81" font-size="11" font-family="ui-monospace,monospace"><text x="32" y="75">${Math.max(...lat).toFixed(3)}°S</text><text x="32" y="612">${Math.min(...lat).toFixed(3)}°S</text><text x="970" y="612">${Math.max(...lon).toFixed(3)}°E</text></g></svg>`;
    }
    function focusDistrict() {
        const ring=districtRing();
        if (!mapInstance || !ring || !window.L) return;
        const bounds=window.L.latLngBounds(ring.map(([lon,lat])=>[lat,lon]));
        mapInstance.fitBounds(bounds.pad(.12),{animate:true,maxZoom:14});
    }
    function addDistrictMask() {
        if (!mapInstance || !window.L || !districtRing()) return;
        const L=window.L, ring=districtRing().map(([lon,lat])=>[lat,lon]);
        // Leaflet polygon: the second ring is a hole, preserving full color INSIDE Jatinangor.
        const outer=[[-20,90],[-20,135],[12,135],[12,90]];
        boundaryMask=L.polygon([outer,ring],{stroke:false,fillColor:'#8a9793',fillOpacity:mapMasked ? .63 : .13,interactive:false,fillRule:'evenodd',pane:'overlayPane'}).addTo(mapInstance);
        boundaryLayer=L.polygon(ring,{color:'#1d775d',weight:3.5,opacity:1,fillColor:'#4b9c70',fillOpacity:.085,interactive:false}).addTo(mapInstance);
        focusDistrict();
    }
    function initMap() {
        const target=document.getElementById('map');
        if(!target) return;
        renderBoundaryIllustration();
        document.getElementById('map-stage')?.classList.toggle('map-bright', !mapMasked);
        if(!districtRing()) return;
        if(!window.L) {
            target.setAttribute('aria-label','Pratinjau vektor batas Jatinangor; Leaflet tidak tersedia.');
            target.style.pointerEvents='none';
            return;
        }
        const L=window.L;
        document.getElementById('map-stage')?.classList.add('leaflet-active');
        mapInstance=L.map(target,{scrollWheelZoom:false,zoomControl:false,attributionControl:true,preferCanvas:false,minZoom:10}).setView([-6.929,107.774],13);
        L.control.zoom({position:'bottomright'}).addTo(mapInstance);
        const url=window.JPO_TILE_URL||'https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
        const primaryTiles=L.tileLayer(url,{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors · © <a href="https://carto.com/attribution/" target="_blank">CARTO</a>',crossOrigin:true});
        let tileErrors=0,tileSuccess=false,switched=false;
        primaryTiles.on('tileload',()=>{tileSuccess=true;});
        primaryTiles.on('tileerror',()=>{
            if(switched||tileSuccess||window.JPO_TILE_URL) return;
            if(++tileErrors<3) return;
            switched=true;
            mapInstance.removeLayer(primaryTiles);
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'}).addTo(mapInstance);
        });
        primaryTiles.addTo(mapInstance);
        addDistrictMask();
        const verified=state.candidates.filter(c=>c.coordinate_verified&&Number.isFinite(c.latitude)&&Number.isFinite(c.longitude));
        verified.forEach(c=>{
            const marker=L.marker([c.latitude,c.longitude],{icon:L.divIcon({className:'map-marker-wrap',html:`<span class="map-pin" data-label="${safe(c.id)}"></span>`,iconSize:[45,43],iconAnchor:[22,42]})}).addTo(mapInstance);
            marker.bindPopup(`<div class="map-popup-title">${safe(c.label)}</div><div class="map-popup-source">${safe(c.coordinate_source)}</div>`);
            marker.on('click',()=>{activePinCandidate=null;});
        });
        mapInstance.on('click', e=>{
            if(!activePinCandidate) return;
            if(!insideDistrict(e.latlng.lat,e.latlng.lng)){
                toast('Titik berada di luar batas visual Jatinangor. Pilih area di dalam kecamatan, atau verifikasi geometri terlebih dahulu.',true);
                return;
            }
            const candidate=activePinCandidate;activePinCandidate=null;
            document.getElementById('map-stage')?.classList.remove('map-picking');
            openCandidate(candidate,e.latlng.lat,e.latlng.lng);
        });
    }
    function openGuide() {
        const steps=[
            ['Buat skenario', 'Gunakan seed 202611. Workspace akan diisi 56 nilai dan penilaian pakar berlabel simulasi. Data lama tergantikan.'],
            ['Baca data dan bobot', 'Buka Data penelitian untuk melihat setiap satuan, lalu Penilaian pakar untuk melihat matriks perbandingan.'],
            ['Hitung ranking awal', 'Buka Pemeringkatan, klik Jalankan perhitungan. Hasilnya hanya prioritas kajian berdasarkan skenario.'],
            ['Uji perubahan observasi', 'Pada Observasi, buat catatan agregat simulasi untuk A1, simpan lalu Terapkan. Hasil ranking sebelumnya menjadi tidak mutakhir.'],
            ['Hitung ulang dan audit', 'Jalankan TOPSIS lagi, bandingkan perubahan dan unduh data di Riwayat & sumber.']
        ];
        open(`<div class="guide-eyebrow">PANDUAN PENGUJIAN · 5 LANGKAH</div><h2>Mencoba DSS dari awal sampai selesai</h2><p>Alur ini memeragakan fungsi software tanpa menyatakan bahwa pengukuran Jatinangor telah dilakukan.</p><ol class="guide-list">${steps.map(([title,desc])=>`<li><b>${title}</b><span>${desc}</span></li>`).join('')}</ol><div class="guide-warning">Peta menampilkan batas kecamatan yang disederhanakan. Empat pin kandidat baru muncul setelah koordinatnya diperiksa; tidak ada pin dummy.</div><div class="form-actions guide-actions"><button type="button" class="btn secondary" data-action="close-modal">Tutup</button><button type="button" class="btn primary" data-action="go-demo">Mulai dari skenario uji</button></div>`);
    }
    function open(html) { document.getElementById('modal-content').innerHTML = `<div class="modal-inner">${html}</div>`; modal.showModal(); }
    function close() { modal.close(); }
    function openCandidate(id, latitude, longitude) {
        const c = cById(id);
        if (!c)
            return;
        open(`<h2>${safe(c.id)} · Detail kandidat</h2><p>Koordinat baru tidak otomatis terverifikasi. Pastikan titik dan asalnya sesuai lokasi penyeberangan, bukan sekadar bangunan di sekitarnya.</p><form id="candidate-form" class="grid-form"><input type="hidden" name="candidate_id" value="${safe(id)}"><div class="field wide"><label>Nama titik / ruas</label><input name="label" value="${safe(c.label)}" required minlength="3"></div><div class="field"><label>Lintang</label><input name="latitude" type="number" step="any" min="-90" max="90" value="${latitude ?? c.latitude ?? ''}"></div><div class="field"><label>Bujur</label><input name="longitude" type="number" step="any" min="-180" max="180" value="${longitude ?? c.longitude ?? ''}"></div><div class="field wide"><label>Sumber koordinat</label><input name="coordinate_source" maxlength="500" placeholder="Survei GPS / tautan OpenStreetMap / catatan lapangan" value="${safe(c.coordinate_source || '')}"></div><div class="field wide"><label>Catatan perbedaan lokasi atau nama</label><textarea name="note" maxlength="700">${safe(c.note || '')}</textarea></div><div class="field wide"><label class="check"><input type="checkbox" name="identity_verified" ${c.identity_verified ? 'checked' : ''}> Nama dan definisi titik sudah dikonfirmasi tim</label><label class="check"><input type="checkbox" name="coordinate_verified" ${c.coordinate_verified ? 'checked' : ''}> Saya memeriksa titik ini dan sumber koordinatnya</label></div><div class="field wide form-actions"><button type="button" class="btn secondary" data-action="close-modal">Batal</button><button type="button" class="btn secondary" data-action="start-pick" data-id="${safe(id)}">Pilih titik di peta</button><button type="submit" class="btn">Simpan kandidat</button></div></form>`);
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
        else if(action === 'go-demo') { close();openDemo(); }
        else if(action === 'start-pick') {
            if(!window.L || !districtRing()) { toast('Pemilihan lewat peta memerlukan Leaflet dan geometri kecamatan. Isi koordinat manual setelah verifikasi sumber.',true);return; }
            const id=target.dataset.id;
            if(!cById(id)) return;
            close();screen='overview';activePinCandidate=id;render();
            document.getElementById('map-stage')?.classList.add('map-picking');
            toast('Pilih titik penyeberangan di dalam Jatinangor. Hasilnya masih draf sampai sumber koordinat dikonfirmasi.');
        }
        else if (action === 'focus-region') {
            focusDistrict();
        }
        else if (action === 'toggle-mask') {
            mapMasked = !mapMasked;
            if (boundaryMask) boundaryMask.setStyle({fillOpacity:mapMasked ? .63 : .13});
            const el=document.getElementById('toggle-mask');
            if(el){el.textContent=mapMasked?'Area luar: redup':'Area luar: terang';el.setAttribute('aria-pressed',String(mapMasked));}
            document.getElementById('map-stage')?.classList.toggle('map-bright', !mapMasked);
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
    document.getElementById('help-guide').addEventListener('click', openGuide);
    async function start() {
        try {
            const result = await Promise.allSettled([request('/workspace'),request('/geography/jatinangor')]);
            if(result[0].status !== 'fulfilled') throw result[0].reason;
            state=result[0].value;
            geography=result[1].status === 'fulfilled' ? result[1].value : null;
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