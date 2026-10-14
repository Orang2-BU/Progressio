# TASKS — Sisa pekerjaan Progressio untuk penerus manusia

> Arsip snapshot 13 Oktober 2026. Untuk pekerjaan berikutnya gunakan [plan penyelesaian](PLAN-COMPLETION.md) dan [task penyelesaian](TASKS-COMPLETION.md). Status dan SHA di bawah bersifat historis; referensi root diperbarui karena HANDOFF.md telah dihapus.

Tanggal snapshot: **13 Oktober 2026 (Asia/Jakarta)**. Cakupan: **14 tiket, 5 In Progress dan 9 Under Review** berdasarkan pembacaan board pada sesi ini.

Baca [PLAN-COMPLETION.md](PLAN-COMPLETION.md) lebih dahulu untuk lokasi hasil kerja, blocker keamanan, urutan eksekusi dan cara menyerahkan hasil. Dokumen ini adalah ekspor serah-terima; **Sokudo Kanban tetap sumber status resmi**, bukan tracker baru. Perbarui tiket asal saat ada hasil. PIC pada tabel adalah PIC board saat snapshot; penerus manusia melanjutkan scope, bukan mengambil kewenangan seluruh gate.

TASK-014/022/025 berstatus Backlog dan tidak termasuk pekerjaan yang diminta. Mereka hanya disebut bila menjadi konteks dependency. TASK-021 sudah Done/merged; jangan implementasikan ulang. Target lama 13 Oktober adalah target delivery, bukan bukti pekerjaan selesai.

## Daftar tiket

| Tiket | Status board | PIC tercatat | Pekerjaan |
|---|---|---|---|
| [TASK-009](#task-009) | Under Review | Sugeng | Pertahankan sesi web dengan cookie HttpOnly dan logout di server |
| [TASK-012](#task-012) | In Progress | Manok | Hubungkan autentikasi Mobile ke API dan hilangkan keberhasilan simulasi |
| [TASK-016](#task-016) | Under Review | Manok | Implementasikan Ringkasan dan Profil akun web sesuai canvas v3 |
| [TASK-018](#task-018) | Under Review | Manok | Implementasikan diagnostic web v3 dengan mode fokus dan hasil skill |
| [TASK-019](#task-019) | Under Review | Owi | Implementasikan roadmap web v3 dengan jalur node dan panel detail |
| [TASK-020](#task-020) | Under Review | Manok | Implementasikan ruang belajar web v3 dengan split pane dan checkpoint |
| [TASK-027](#task-027) | In Progress | Jessica | Verifikasi QA kandidat revisi TASK-006, TASK-007, dan TASK-015 |
| [TASK-029](#task-029) | Under Review | Jessica | Implementasikan bukti regresi dan runbook untuk menutup gap QA aktif |
| [TASK-033](#task-033) | Under Review | Jessica | Tuntaskan QA fondasi frontend dan rapikan handoff backend Jessica |
| [TASK-042](#task-042) | Under Review | Manok | Pulihkan kandidat aman Ringkasan dan Profil untuk menutup TASK-016 |
| [TASK-043](#task-043) | Under Review | Jessica | Pulihkan kandidat QA aman untuk menutup TASK-033 dan sisa TASK-027 |
| [TASK-047](#task-047) | In Progress | Owi | Fix revisi ruang belajar TASK-020 dan lengkapi bukti regresi |
| [TASK-048](#task-048) | In Progress | Adit | Review diff utuh kandidat web yang tertahan akses dan revisi aktif |
| [TASK-049](#task-049) | In Progress | Jessica | Verifikasi gap QA frontend kandidat terintegrasi dan bukti Under Review |

## Definition of done bersama

- Acceptance asli dan revisi terbaru terpenuhi pada **SHA/base yang disebut jelas**. PASS snapshot, PASS unit, validasi YAML, merge dan PASS browser adalah bukti berbeda.
- Fitur/bug fix memakai RED → GREEN → refactor; regression test wajib, coverage kode baru minimal 80% dengan laporan metode/persentase. Jangan menutupi skip atau kegagalan alat.
- Catat full diff `base...SHA`, seluruh commit yang relevan, daftar file, command/cwd, exit code, pass/fail/skip, coverage, artefak dan hasil LSP untuk source berubah.
- Dokumentasi/kontrak serta changelog diperbarui bila perilaku pengguna berubah. Tidak mengarang data, reward, status credential, penyimpanan checkpoint atau kemampuan backend.
- Reviewer kode **Adit**, QA **Jessica**. Herman/Owi tidak menggantikan kedua reviewer tersebut. Urutan gate **Adit → Bimo → Jono → Agus**, dengan QA Jessica sesuai cakupan; temuan BLOCKED Bimo tetap melarang merge.
- Hasil branch worker menunggu **Approve/Discard pengguna pada kartu**. Jangan merge/rebase/cherry-pick branch worker ke main sendiri. Tiket implementasi belum Done sebelum merged; tiket investigasi selesai dengan laporan temuan, bukan commit.
- Untuk tiket QA/investigasi, hasil utamanya laporan: jangan memperbaiki produk diam-diam dalam scope review. Catat defect dan kembalikan ke implementer.

<a id="task-009"></a>

## TASK-009 — Pertahankan sesi web dengan cookie HttpOnly dan logout di server

**Status praktis:** BLOCKED: false logout pada kandidat lama; revisi belum memiliki verdict final.

**Tujuan:** Sesi web pulih saat reload; logout sukses benar-benar mencabut refresh sesi terkait.

**Lokasi kerja:** `front-end/src/api.js`, `front-end/src/App.jsx`, `front-end/src/Profile.jsx`, `front-end/API_CONTRACT.md`, `back-end/apps/accounts/{views.py,urls.py,tests.py}`, `back-end/config/settings.py`. Gunakan versi kandidat, bukan menganggap main sudah berisi sesi cookie.

**Yang sudah ada:** Kandidat lama `7ffcdb5` (base dilaporkan `d83667c`) dan worktree revisi `7228704` tersedia. Kehadiran branch revisi bukan bukti temuan sudah ditutup. Handoff backend lengkap tersedia; lihat PLAN-COMPLETION.md.

### Yang harus dikerjakan

1. Inventaris kedua worktree dan pilih satu kandidat final yang dapat ditelusuri; periksa seluruh history serta full diff. Jangan memasukkan kandidat lama ke main.
2. Tulis regression RED untuk logout 403, 503, timeout dan network error. Teruskan error ke UI dan tampilkan gagal/retry; jangan mengumumkan sukses server atau membiarkan respons refresh terlambat menghidupkan sesi.
3. Pada logout sukses, blacklist refresh dan hapus cookie dengan atribut yang cocok. Buktikan refresh lama ditolak 401 dan reload tetap anonim. Pertahankan HttpOnly, Secure sesuai environment, SameSite, CSRF/origin checks, throttle, serta jalur Bearer Mobile.
4. Uji dua tab, refresh paralel, revoked/expired refresh, race logout-refresh, isolasi SSR antarpengguna. Dokumentasikan batas access token yang telah terbit berdasarkan kontrak final.
5. Perbarui kontrak API/docs/changelog; serahkan exact SHA kepada Adit lalu Bimo sebelum integrasi/E2E.

**Definition of done:** Seluruh kasus gagal tidak menghasilkan sukses palsu; refresh setelah logout sukses ditolak; reload/dua tab/SSR dan kontrak Bearer terbukti. Tes accounts, frontend, probe kontrak dan Sokudo E2E pada runtime yang diizinkan memiliki bukti; semua gate umum terpenuhi.

**Blocker/dependency:** Temuan High Bimo dan keamanan upstream; ikuti paket prasyarat PLAN-COMPLETION.md. Runtime backend belum diizinkan.

**Sumber:** brief dan komentar TASK-009; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-012"></a>

## TASK-012 — Hubungkan autentikasi Mobile ke API dan hilangkan keberhasilan simulasi

**Status praktis:** BLOCKED oleh TASK-046; source Mobile parsial tersimpan sebagai perubahan belum di-commit.

**Tujuan:** Register, login username, /auth/me, pemulihan sesi, profil minimal dan logout perangkat memakai kontrak nyata tanpa sukses simulasi.

**Lokasi kerja:** Khusus worktree TASK-012: `Mobile/lib/core/network/`, `Mobile/lib/data/`, `Mobile/lib/domain/`, `Mobile/lib/presentation/blocs/auth/`, halaman auth/profil, `Mobile/pubspec.yaml`, `Mobile/test/`. Lokasi worktree persis di PLAN-COMPLETION.md.

**Yang sudah ada:** Manok melaporkan fake transport/storage, secure storage, refresh interceptor dan UI unavailable sudah dibuat. Pemeriksaan lokal menemukan 13 file tracked berubah serta direktori/file untracked; HEAD worktree masih `323c4e9`. Belum ada commit final. Klaim basis kerja aman `59ebc369` perlu direkonsiliasi dengan HEAD aktual sebelum menjalankan apa pun.

### Yang harus dikerjakan

1. Amankan inventaris perubahan tracked DAN untracked dari worktree yang sama; jangan reset, clean, menimpa, atau hanya mengirim patch tracked sehingga file baru hilang.
2. Rekonsiliasi source yang ditulis dengan batas Bimo: baseline `59ebc369` + delta Mobile saja, transport dan storage palsu untuk tes offline. Tentukan snapshot aman dan manifest sebelum menjalankan tes.
3. Baca instruksi Mobile; audit kontrak username login dan username/email/password/password_confirm register, token secure storage, refresh terkoordinasi, restore sesi serta logout lokal. Reset/OTP/Google tetap unavailable selama endpoint belum ada.
4. Siapkan Flutter SDK sesuai pubspec, verifikasi dependency/lockfile lalu jalankan analyze dan unit/widget tests. Uji 400/401/offline, refresh gagal/paralel, secure storage dan pemulihan sesi; hasil sebelumnya NOT RUN karena SDK tidak tersedia.
5. Setelah clearance upstream, uji akun sintetis di API disposable: register→login→me→restart→logout. Pastikan endpoint Bearer cocok dengan perubahan TASK-009 dan jangan mengklaim logout lokal sebagai revoke server.

**Definition of done:** Analyze dan unit/widget tests PASS, token tidak bocor/log/SharedPreferences, sukses hanya dari API, hasil restart/logout terbukti di integrasi lokal yang diizinkan. SHA final + source baru + bukti lengkap direview Adit/Jessica dan gate umum.

**Blocker/dependency:** TASK-046 berstatus Done sebagai laporan asesmen, tetapi verdict-nya BLOCKED untuk integrasi. Flutter tidak ditemukan di PATH sesi ini. Tes offline tidak menyelesaikan acceptance API nyata.

**Sumber:** brief dan komentar TASK-012; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-016"></a>

## TASK-016 — Implementasikan Ringkasan dan Profil akun web sesuai canvas v3

**Status praktis:** Under Review; implementasi dashboard/profil sudah terwakili melalui TASK-042/044, masih ada gap tes/QA.

**Tujuan:** Ringkasan dan Profil memakai akun/progres nyata, CTA target yang jujur dan pengaturan unsupported yang jelas.

**Lokasi kerja:** `front-end/src/{Dashboard.jsx,Profile.jsx,dashboard.js,App.jsx,foundation.css}`, `front-end/tests/{dashboard.test.js,logout-accessibility.test.js,api.test.js}`.

**Yang sudah ada:** Kandidat lama `eceaf53` dari `0c064365`; pemulihan `421e36e` dan komposisi `3769318`. Adit TASK-045 menyatakan hunk terwakili. Coverage historis Dashboard.jsx 46,43% dan dashboard.js 45,71%, belum mencapai target kode baru 80%.

### Yang harus dikerjakan

1. Bandingkan source kandidat dengan komposisi yang sudah ada; jangan menerapkan kembali seluruh patch TASK-016/042.
2. Tambahkan tes perilaku loading, akun baru/empty, data terisi, target tanpa query/invalid, error parsial, retry dan respons usang; ukur coverage kode baru minimal 80%.
3. Pertahankan target hanya dari query tervalidasi; tanpa target tampilkan Pilih target. XP/completion/identitas berasal dari server; jangan mengarang streak, level atau riwayat.
4. Tutup notice palsu `/login?logged_out=1` bersama perubahan App/Profile dengan alasan logout dari event nyata. Bedakan logout lokal dari revoke server sesuai kontrak.
5. Validasi copy username/fallback, email kosong, reload, label Keluar di 375px, keyboard, tema dan ukuran 375/768/1440. Edit profil/password/pengingat/privasi tetap disabled bertanda SEGERA.

**Definition of done:** Pemetaan data/fallback dan coverage terbukti pada satu SHA; tidak ada notice/logout palsu; bukti interaktif dan aksesibilitas lengkap, bukan hanya assertion source. Gunakan penutupan TASK-042 dan QA TASK-049 agar tidak menduplikasi pekerjaan.

**Blocker/dependency:** QA browser, coverage dan notice belum ditutup; main belum memperoleh clearance keamanan.

**Sumber:** brief dan komentar TASK-016; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-018"></a>

## TASK-018 — Implementasikan diagnostic web v3 dengan mode fokus dan hasil skill

**Status praktis:** Under Review; kandidat branch `37dca54` berbeda dari SHA review lama `4a431cd`.

**Tujuan:** Diagnostic satu soal per layar dengan hasil per skill dari server dan semantik jawaban yang benar.

**Lokasi kerja:** `front-end/src/{Diagnostic.jsx,diagnostic.js}`, `front-end/src/app/diagnostic/`, `front-end/tests/diagnostic.test.js`.

**Yang sudah ada:** Branch `37dca54` memiliki parent `4a431cd`; review Adit atas SHA lama gagal akses. Klaim 48/48 dan build adalah bukti implementer, bukan verdict review terbaru.

### Yang harus dikerjakan

1. Pin `37dca54` beserta base dan perubahan terhadap `4a431cd`; periksa apakah revisi TDZ/fokus yang disebut di brief review memang tertutup. Serahkan diff utuh ke TASK-048.
2. Pastikan semua ID soal terkirim; Belum tahu adalah key bernilai string kosong yang dihitung dijawab dan dinilai salah, berbeda dari belum menjawab. Jangan submit saat memilih opsi.
3. Uji navigasi prev/next tanpa kehilangan jawaban, submit lock, query berubah/abort, uncertain submit/recovery, empty questions, latest 404, error/retry dan konfirmasi keluar accessible.
4. Periksa focus ke soal yang belum diisi; mode soal tanpa sidebar/topbar workspace. Hasil memakai shell workspace tanpa sidebar item aktif.
5. Verifikasi result overall_score/completed_at/skill_scores/recommendations berasal dari server; diagnostic tidak memberi XP dan hasil attempt terbaru bukan penurunan mastery tersimpan.

**Definition of done:** Review exact final SHA oleh Adit, regression perilaku dan QA interaktif Jessica terpenuhi; tidak mengarang durasi, histori jawaban, subskill, reward atau kelulusan credential. Tes/build/coverage/LSP sesuai gate umum.

**Blocker/dependency:** Rekonsiliasi SHA dan review/QA belum selesai; TASK-048 gagal startup; integrasi penuh TASK-022 tetap di luar paket ini.

**Sumber:** brief dan komentar TASK-018; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-019"></a>

## TASK-019 — Implementasikan roadmap web v3 dengan jalur node dan panel detail

**Status praktis:** Under Review; code gate Adit HOLD karena full diff belum terbaca pada run terdahulu.

**Tujuan:** Roadmap mengikuti urutan/status server dengan node dan panel detail yang dapat digunakan di semua viewport.

**Lokasi kerja:** `front-end/src/{Roadmap.jsx,roadmap.js,study.js,styles.css,foundation.css}`, `front-end/tests/roadmap.test.js`.

**Yang sudah ada:** SHA `dbbcbdb88e73c260711506458ff2e8df1b655ec2`, parent terverifikasi `6086b401951cb491cd2f4f267af1052d6ebd5480`. 33/33 dan build adalah laporan Owi. Review Herman atau pernyataan implementer tidak menggantikan Adit/Jessica.

### Yang harus dikerjakan

1. Sediakan full parent...candidate dan range baseline...candidate untuk Adit melalui TASK-048; bedakan delta roadmap dari backend/auth inherited. Jangan menjalankan inherited tree.
2. Tambahkan regresi denominator unik, duplikasi data, coveragePercent dan nol langkah; total_steps tetap langkah tersisa, bukan denominator kelulusan credential.
3. Pastikan urutan DOM/server, fokus/selection, query target dan studyHref benar. Status locked hanya dari larangan kontrak, bukan ilustrasi; already_satisfied berlabel Cukup untuk roadmap.
4. Uji loading/error/empty, tanpa diagnostic, seluruh skill sudah cukup dan prerequisite belum cukup. Empty tidak berarti credential sudah terbit.
5. Validasi panel detail mudah ditemukan setelah klik node di 375px; perbaiki hanya bila QA membuktikan masalah interaksi. Lengkapi tema, keyboard, reduced motion, 375/768/1440.

**Definition of done:** Full diff telah direview Adit; tes persentase/zero guard dan QA live tersedia; node dan CTA membuka skill benar, tanpa status/reward buatan. Seluruh gate umum terpenuhi.

**Blocker/dependency:** TASK-048 belum menghasilkan verdict; QA live belum selesai dan kandidat memiliki inherited backend/auth yang belum clearance.

**Sumber:** brief dan komentar TASK-019; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-020"></a>

## TASK-020 — Implementasikan ruang belajar web v3 dengan split pane dan checkpoint

**Status praktis:** Under Review; revisi konkret diteruskan melalui TASK-047.

**Tujuan:** Split pane Study mempertahankan identitas lesson, feedback checkpoint sementara dan completion server yang terpisah.

**Lokasi kerja:** `front-end/src/{Study.jsx,study.js,styles.css}`, `front-end/tests/study.test.js`, tes completion/component terkait.

**Yang sudah ada:** Kandidat branch `4171af1`; implementer melaporkan 49/49 dan build PASS, LSP timeout. Reviewer menemukan auto-pindah lesson/receipt bocor dan gap state UI; helper/API test belum membuktikan lifecycle komponen.

### Yang harus dikerjakan

1. Kerjakan perbaikan sekali melalui TASK-047; jangan membuat implementasi Study paralel dari tiket ini.
2. Rekonsiliasi temuan terhadap SHA final: completion lesson A tidak memindahkan pilihan ke B tanpa aksi pengguna; receipt/error/busy dan checkpoint A tidak terbawa ke B.
3. Pertahankan sourceHref HTTP(S) aman, link broken disabled, provider/license/attribution, serta label status verifikasi pengelola. Jangan menyalin materi penerbit.
4. Checkpoint hanya feedback sementara, tanpa autosave/XP; completion memakai completed_lesson_ids dan receipt server. Jangan mewajibkan checkpoint benar bila kontrak tidak mensyaratkan.
5. Lengkapi acceptance loading/empty/error, progress unknown/retry, duplicate click, already-completed dan jalur assessment; QA split pane mobile/desktop.

**Definition of done:** Regresi lifecycle yang dijelaskan TASK-047 PASS, journey faktual, tidak ada receipt/reward campur atau ganda. Final SHA dinilai Adit/Jessica; batas LSP dan UI lama ditutup atau dinyatakan masih terbuka.

**Blocker/dependency:** TASK-047 gagal memulai worker tiga run; belum ada bukti revisi dari run tersebut. Tidak berarti patch Study sudah selesai.

**Sumber:** brief dan komentar TASK-020; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-027"></a>

## TASK-027 — Verifikasi QA kandidat revisi TASK-006, TASK-007, dan TASK-015

**Status praktis:** In Progress; QA independen belum memiliki verdict lengkap.

**Tujuan:** Buktikan acceptance kandidat revisi TASK-006/007/015 pada SHA yang benar, bukan tes baseline lain.

**Lokasi kerja:** `docs/demo-test-matrix.md`, `docs/demo-runbook.md`, `docs/QA-TASK-033-frontend-foundation.md`, `e2e/`, suite frontend/accounts/assessments/ai/verification.

**Yang sudah ada:** QA frontend dilanjutkan TASK-033/043/044/049. Backend tetap handoff manusia; TASK-025 gagal tanpa verdict tidak dianggap PASS.

### Yang harus dikerjakan

1. Petakan tiap acceptance ke final SHA, bukti yang sudah tersedia dan gap. Jangan ulang klaim tes baseline sebagai bukti revisi.
2. Tutup frontend melalui TASK-049: notice expired vs logout, routing/sidebar/focus, draft/mock, responsif/tema dan error state.
3. Sesudah keamanan backend/fixture dinyatakan lolos, verifikasi 429/retry/expiry/isolasi user, cache shared Redis lintas proses, proxy dan probe kontrak pada runtime disposable.
4. Untuk flow demo, cocokkan runtime/SHA/fixture dengan run ID; buktikan draft invalid/unanchored dan repeat completion tanpa XP tambahan. Ikuti batas runner di PLAN-COMPLETION.md.
5. Terbitkan laporan per acceptance PASS/FAIL/NOT RUN, reproduksi defect, severity/file:line/fix serta alasan blocker. Temuan produk dikembalikan ke implementer.

**Definition of done:** Laporan QA independen memiliki exact SHA/base, command/cwd/output, artefak dan verdict per tiket; acceptance yang belum berjalan tetap terbuka. Tidak mengubah produk dalam tugas investigasi.

**Blocker/dependency:** Backend TASK-009/029 dan TASK-046 belum clearance; TASK-049 gagal dua run. TASK-006/007/015 yang sudah Done tidak perlu diimplementasikan ulang.

**Sumber:** brief dan komentar TASK-027; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-029"></a>

## TASK-029 — Implementasikan bukti regresi dan runbook untuk menutup gap QA aktif

**Status praktis:** Under Review; automation QA BLOCKED/HOLD, diserahkan ke developer manusia.

**Tujuan:** Tes/fixture/flow/runbook reproduktif untuk gap konkurensi, throttle/hosting dan QA batch.

**Lokasi kerja:** Kandidat TASK-029: `front-end/tests/backend_server.py`, `front-end/check_api_contract.py`, `qa/test_proxy.py`, `qa/run_services.py`, `e2e/progressio-demo.yaml`, dokumentasi QA. `qa/` ada di worktree TASK-029, tidak ada di main saat snapshot.

**Yang sudah ada:** Source historis `4b160099`, evidence `16a34c1`, HEAD dokumen `12429d1`. 6/6 offline merupakan bukti historis implementer; full patch/source drift belum disahkan Adit.

### Yang harus dikerjakan

1. Pin satu SHA final dan full diff dari base `6720ba1`; audit semua commit hingga HEAD, bukan hanya commit dokumen terakhir.
2. Perbaiki/validasi sanitizer environment sebelum import Django: local, SQLite in-memory, mock providers, tidak mewarisi Redis/Celery milik pengguna.
3. Periksa guard URL proxy agar hanya loopback/port milik run yang diizinkan, menolak userinfo/non-loopback; cleanup harus mencoba semua owned resource lalu mengagregasi kegagalan. Buktikan RED→GREEN dengan tes offline.
4. Ajukan source fixture ke Adit lalu Bimo sebelum menjalankan layanan. Setelah clearance, buktikan concurrency PostgreSQL dengan koneksi terpisah/interleaving deterministik, mastery tidak turun, XP tidak hilang/ganda dan isolasi pengguna.
5. Lanjutkan Redis lintas proses/429/retry/expiry/proxy/hosting serta flow demo dengan selector unik, bootstrap fixture deterministik, draft/invalid dan repeat completion. Tulis matriks dan runbook aktual.

**Definition of done:** Source automation dapat direview pada satu SHA, fixture terisolasi dan cleanup aman; PostgreSQL/Redis/E2E punya hasil nyata atau gap eksplisit. Acceptance TASK-014/025/027 dipetakan, tanpa fake green. Perubahan produk di luar scope automation.

**Blocker/dependency:** Keamanan fixture, SHA drift dan akses review; mengikuti handoff backend yang sudah ada. Jangan menjalankan QA non-keamanan sebelum clearance.

**Sumber:** brief dan komentar TASK-029; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-033"></a>

## TASK-033 — Tuntaskan QA fondasi frontend dan rapikan handoff backend Jessica

**Status praktis:** Under Review; delta tes/docs historis sudah direview, QA browser masih terbuka.

**Tujuan:** Tutup QA fondasi frontend dan pertahankan handoff backend yang dapat diteruskan manusia.

**Lokasi kerja:** `docs/QA-TASK-033-frontend-foundation.md`, `docs/qa-task-033/`, `front-end/tests/api.test.js`, `e2e/foundation-anonymous.yaml`, handoff backend existing.

**Yang sudah ada:** Delta `5233d538` mendapat approval kode historis Adit TASK-034; pemulihan TASK-043 dan komposisi TASK-044 mewakili hunk-nya. HEAD kartu lama `ec7fb713` bukan snapshot aman yang telah dites.

### Yang harus dikerjakan

1. Pertahankan bukti lama dan tautkan komposisi terbaru; jangan menerapkan ulang patch atau menafsirkan approve historis sebagai izin menjalankan HEAD lama.
2. Lengkapi matriks UI melalui TASK-049: sidebar aktif hanya Ringkasan/Pilih target/Credential/Profil, flow tanpa active item dan public verify tanpa sidebar.
3. Buktikan keyboard/focus, tema/reduced motion, 375/768/1440, loading/error/empty, mock/draft dan logout notice dari event nyata.
4. Pisahkan source assertion, SSR, hydration/component runtime dan browser. Validasi YAML saja belum berarti flow berhasil dijalankan.
5. Perbarui laporan existing dengan run ID/SHA/bukti baru; handoff backend tetap merujuk dokumen yang sama.

**Definition of done:** Seluruh acceptance fondasi berstatus jelas dengan bukti pada source tepat; laporan tidak mengklaim QA integrasi penuh TASK-022 atau keamanan backend. Tidak mengubah produk dalam pekerjaan QA.

**Blocker/dependency:** Browser/flow belum dijalankan, LSP historis timeout, main masih tanpa clearance. Penutupan bersama TASK-043/049.

**Sumber:** brief dan komentar TASK-033; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-042"></a>

## TASK-042 — Pulihkan kandidat aman Ringkasan dan Profil untuk menutup TASK-016

**Status praktis:** Under Review; hunk pemulihan dashboard/profil sudah terwakili TASK-044.

**Tujuan:** Rekonsiliasi hasil pemulihan TASK-016 dan tutup gap tersisa tanpa mengulang komposisi.

**Lokasi kerja:** Sama dengan TASK-016; kandidat aman `421e36e62056278dfbf92f74532c5f4814a32b94`, parent exact `59ebc369eff75dd063ca568322e0ca3cade23705`.

**Yang sudah ada:** Fix aria-label Keluar dan dashboard/profil telah dipulihkan. Recorded branch berbeda dari branch awal kartu; pernyataan sistem no file changes tidak membuktikan seluruh acceptance selesai.

### Yang harus dikerjakan

1. Bandingkan candidate/base dan hunk komposisi TASK-044; pertahankan artefak kandidat lama TASK-016 serta dependency aman.
2. Kerjakan gap coverage dashboard dan notice logout bersama TASK-016; satu patch terpin, bukan pemulihan kedua.
3. Pastikan accessible name Keluar bertahan saat teks visual disembunyikan; tambah bukti browser 375px karena tes source hanya membuktikan markup.
4. Sediakan manifest/range final untuk TASK-048 dan QA TASK-049; selesaikan rekonsiliasi kartu melalui owner setelah gate.

**Definition of done:** Provenance hunk dan final SHA jelas, coverage ≥80% kode baru, notice/aksesibilitas terbukti serta acceptance TASK-016 terpenuhi. Kartu lama tidak ditandai Done hanya karena hunk terlihat di main.

**Blocker/dependency:** Gap coverage/notice dan QA; Approve/Discard kartu dan gate belum ditutup.

**Sumber:** brief dan komentar TASK-042; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-043"></a>

## TASK-043 — Pulihkan kandidat QA aman untuk menutup TASK-033 dan sisa TASK-027

**Status praktis:** Under Review; PASS Adit terbatas komposisi, QA runtime/browser belum selesai.

**Tujuan:** Rekonsiliasi kandidat QA aman untuk menutup TASK-033 dan porsi frontend TASK-027.

**Lokasi kerja:** `front-end/tests/`, `docs/qa-task-033/`, `docs/QA-TASK-033-frontend-foundation.md`, `e2e/foundation-anonymous.yaml`.

**Yang sudah ada:** Final `42cff215`; Adit PASS pada `9016d293` dengan base `59ebc369`. 36/36 dan build berasal dari source `fa57bc6`; integrasi TASK-044 melaporkan 47/47 pada snapshot lain. Jangan mencampur angka tersebut.

### Yang harus dikerjakan

1. Cocokkan manifest, source tes dan perubahan docs-only antara SHA review/source/final; pertahankan 13 artefak historis.
2. Gunakan hasil komposisi TASK-044; jangan apply ulang patch TASK-043. Jelaskan setiap acceptance TASK-027/033 yang terwakili vs masih terbuka.
3. Tutup browser/hydration/fokus/notice via TASK-049 dan runner setelah batas keamanan terpenuhi; flow valid inline tetap NOT RUN sampai ada event runner.
4. Catat hasil LSP terbaru atau timeout secara jujur; pertahankan case inherited ke-37 sebagai NOT RUN jika masih belum dieksekusi pada source yang tepat.

**Definition of done:** Pemetaan acceptance + bukti source/snapshot/final dapat diaudit, tidak ada backend/product delta terselip; final QA dan gate terbukti sebelum penutupan kartu.

**Blocker/dependency:** PASS kode komposisi bukan clearance main; runtime lama ditolak policy dan LSP timeout.

**Sumber:** brief dan komentar TASK-043; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-047"></a>

## TASK-047 — Fix revisi ruang belajar TASK-020 dan lengkapi bukti regresi

**Status praktis:** In Progress; tiga run worker gagal startup CLI/PTY, belum menghasilkan revisi.

**Tujuan:** Perbaiki bug identitas lesson/receipt dan journey TASK-020 dengan regresi bermakna.

**Lokasi kerja:** `front-end/src/Study.jsx`, `front-end/src/study.js`, CSS Study, tes study/completion/component, dokumentasi/changelog terkait.

**Yang sudah ada:** Mulai dari kandidat TASK-020 `4171af1`, bukan menulis ulang Study. Worktree TASK-047 masih HEAD `323c4e9`; startup gagal tidak membuktikan perubahan apa pun.

### Yang harus dikerjakan

1. Pin delta Study pada snapshot frontend aman; reproduksi bug completion A→pilihan berubah B dan receipt/error/busy/checkpoint A menempel di B.
2. Tulis test RED yang menguji pergantian identitas dan lifecycle UI; implementer memilih fix minimal agar pilihan tidak berganti otomatis dan state per lesson terisolasi.
3. Perbaiki JourneyTracker hanya berdasar fakta kontrak. Membuka Study tidak membuktikan Diagnostic/Roadmap selesai; jangan menyalin saran status complete tanpa data pendukung.
4. Lengkapi checkpoint benar/salah, already-completed receipt newly_completed:false tanpa XP ganda, progress gagal/unknown/retry dan duplicate click. Helper test saja belum menutup lifecycle.
5. Jalankan tes/build/coverage pada snapshot terpin, LSP dan docs/changelog; serahkan patch penuh serta manifest ke TASK-048/049.

**Definition of done:** Regresi RED→GREEN dan coverage kode baru ≥80%; lesson/receipt/checkpoint tidak bercampur, journey tidak fiktif; acceptance TASK-020 dipertahankan dan review/gate lengkap.

**Blocker/dependency:** Launcher CLI/PTY bermasalah; teman manusia dapat meneruskan pekerjaan sesuai scope tanpa redispatch berulang. Runtime tetap dibatasi clearance Bimo.

**Sumber:** brief dan komentar TASK-047; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-048"></a>

## TASK-048 — Review diff utuh kandidat web yang tertahan akses dan revisi aktif

**Status praktis:** In Progress; dua run investigasi gagal composer, belum ada verdict baru.

**Tujuan:** Code review independen full diff kandidat web stabil, terutama roadmap dan revisi diagnostic/Study.

**Lokasi kerja:** Candidate TASK-019/018/020, lalu delta penutupan TASK-016/042 dan tes terkait; gunakan tabel refs PLAN-COMPLETION.md.

**Yang sudah ada:** TASK-045 sudah memetakan hunk lama; jangan mengulang audit status tanpa membaca diff. TASK-021 kini Done/merged dan hanya konteks integrasi, bukan pekerjaan implementasi ulang.

### Yang harus dikerjakan

1. Mulai dari roadmap dbbcbdb: baca parent...candidate dan base...candidate lengkap, termasuk history; bedakan inherited source dari delta.
2. Periksa urutan server, denominator/zero guard, fokus/query/studyHref/mobile. Nilai revisi diagnostic di 37dca54, bukan hanya 4a431cd.
3. Review final Study setelah TASK-047 menghasilkan SHA stabil: lifecycle state, receipt/checkpoint, journey faktual serta regression yang membuktikannya.
4. Untuk dashboard/QA gunakan pemetaan TASK-045; nilai delta coverage dan notice baru, jangan meminta apply ulang hunk komposisi.
5. Terbitkan PASS/CHANGES/BLOCKED per exact SHA dengan severity, file:line, reproduksi/penjelasan dan fix konkret; akses terpotong/tidak terbaca tetap BLOCKED.

**Definition of done:** Laporan code gate independen yang dapat ditindaklanjuti, full diff terbaca dan batas tes jelas. Tidak edit source atau memberikan izin keamanan/rilis atas nama Bimo/Agus.

**Blocker/dependency:** Retry investigasi sekali sudah terpakai; jangan dispatch ketiga atau membuat tiket duplikat untuk mengakali batas. Review manual tetap memerlukan sumber dan SHA lengkap.

**Sumber:** brief dan komentar TASK-048; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

<a id="task-049"></a>

## TASK-049 — Verifikasi gap QA frontend kandidat terintegrasi dan bukti Under Review

**Status praktis:** In Progress; dua run gagal composer/overload, belum ada laporan QA baru.

**Tujuan:** Tutup gap QA frontend komposisi TASK-027/033/043 dan dashboard TASK-016/042.

**Lokasi kerja:** `docs/QA-TASK-033-frontend-foundation.md`, `docs/qa-task-033/integration-2026-10-12/`, tes/dashboard/App/Profile dan flow existing.

**Yang sudah ada:** Komposisi TASK-044 telah menghasilkan bukti snapshot; coverage dashboard lama masih di bawah 80%, source/SSR belum membuktikan hydration/browser.

### Yang harus dikerjakan

1. Pin snapshot aman baseline 59ebc369 + delta frontend terpilih dan manifest; cocokkan source sebelum run. Jangan memakai HEAD inherited sebagai pengganti.
2. Jalankan tes/build/coverage existing yang aman; evaluasi apakah tests menutup loading/empty/partial failure/target/logout notice. Jangan edit produk di tiket investigasi.
3. Validasi direct `/login?logged_out=1` tidak mengumumkan logout palsu setelah fix implementer; pisahkan logout lokal dari revoke server.
4. Kumpulkan bukti component/hydration/browser yang masih kurang sesuai izin runtime; integrasi backend dan E2E terintegrasi menunggu Bimo/Jono.
5. Susun matriks satu laporan lintas TASK-027/033/043/016/042, pisahkan backend pending manusia. Hasil produk yang gagal dikembalikan ke implementer dengan reproduksi.

**Definition of done:** Setiap acceptance memiliki PASS/FAIL/NOT RUN dan SHA, command/cwd, artefak serta batas metode. Tidak mengklaim seluruh Under Review siap merge hanya karena unit/build PASS.

**Blocker/dependency:** Batas retry investigasi sudah tercapai; coverage/notice belum otomatis tertutup dan clearance backend masih diperlukan.

**Sumber:** brief dan komentar TASK-049; detail keamanan/provenance lintas tiket di [PLAN-COMPLETION.md](PLAN-COMPLETION.md).
