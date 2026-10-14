# Task penyelesaian Progressio

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Plan: [PLAN-COMPLETION.md](PLAN-COMPLETION.md).

Status awal paket ini adalah TODO, kecuali dependency browser yang diketahui BLOCKED. Tes lama yang sudah PASS menjadi titik awal; task baru belum dianggap selesai hanya karena dokumen ini dibuat. ID COMP adalah checklist lokal dan tidak membuat tiket baru di board.

## Pemetaan tiket asal

| Tiket asal | Paket penutupan |
| --- | --- |
| TASK-009 | COMP-002, COMP-007, COMP-008, COMP-010 |
| TASK-012 | COMP-002, COMP-008 |
| TASK-016 dan TASK-042 | COMP-003, COMP-005, COMP-007, COMP-010 |
| TASK-018 dan TASK-019 | COMP-003, COMP-006, COMP-007, COMP-010 |
| TASK-020 dan TASK-047 | COMP-003, COMP-004, COMP-007, COMP-010 |
| TASK-027 | COMP-009, COMP-010, COMP-011 |
| TASK-029 | COMP-002, COMP-009, COMP-010 |
| TASK-033, TASK-043, TASK-049 | COMP-003, COMP-010, COMP-011 |
| TASK-048 | COMP-007 |
| Keamanan upstream TASK-046 | COMP-002; laporan lama selesai, verdict terhadap kandidat baru masih harus dibuktikan |
| Plan 002–005 | COMP-010, COMP-011; gunakan implementasi branch yang sudah ada |

TASK-021 sudah merged. TASK-006/007/015 yang sudah Done adalah konteks QA, bukan implementasi ulang. TASK-014/022/025 tetap di luar paket implementasi ini; acceptance concurrency/QA yang diwarisi dipetakan pada COMP-009 tanpa membuka scope fitur baru.

## COMP-001 — Pin kandidat dan periksa lingkungan

Status: PASS. Prioritas: P0. Dependency: —. Bukti: [baseline kandidat dan lingkungan](docs/completion/baseline.md), commit setelah plan.

- [x] Inventaris main, worktree, base/final SHA, serta perubahan tracked/untracked; gunakan kandidat terbaru pada tabel plan sebagai titik awal.
- [x] Petakan delta yang sudah terwakili supaya patch dashboard/QA/Study tidak diterapkan dua kali. Tentukan manifest kandidat integrasi dan dependency source.
- [x] Periksa Node/Python/Flutter, dependency/lockfile, runner Sokudo, PostgreSQL/Redis disposable, serta alat coverage/dependency audit.
- [x] Catat availability dan error konkret. Untuk sumber yang belum dapat diakses, jangan mengklaim review selesai.

Selesai ketika manifest dan peta dependency tersimpan, source pengguna aman, serta blocker lingkungan mempunyai langkah pemulihan. Output: `docs/completion/baseline.md` atau manifest setara; commit dokumentasi bila ada perubahan.

## COMP-002 — Tutup keamanan upstream, auth, dan fixture

Status: PASS terbatas pada SHA kandidat; runtime/release tetap COMP-008/009/010. Bukti: [hasil audit keamanan](docs/completion/COMP-002-security.md) dan [review integrasi](docs/completion/COMP-007-integration-review.md). Prioritas: P0. Dependency: COMP-001. Tiket: TASK-046/009/029/012.

- [x] Audit dependency Node dan Python dengan advisory aktual; pasang alat audit lokal bila belum tersedia dan catat failure/coverage audit.
- [x] Review full diff transport AI/proof: HTTPS, origin/host/port/userinfo, redirect 301/302/303/multi-hop, Authorization, sanitasi error, dan validasi konfigurasi.
- [x] Mobile dan query notice ditinjau; web kini jelas menyebut logout lokal, tidak mengklaim token server dicabut.
- [x] Tambahkan endpoint revoke refresh token TASK-009, blacklist migration bawaan, kontrak OpenAPI dan regresi backend/frontend; refresh token lama ditolak, access token yang sudah terbit tetap valid hingga expiry.
- [x] Verifikasi fixture menolak environment pengguna, tujuan eksternal/userinfo/port bukan milik run, dan mencoba seluruh cleanup walaupun satu resource gagal.
- [x] Untuk defect yang masih terbuka, tulis regression RED, fix minimal, lalu GREEN; perbarui kontrak bila perilaku berubah.
- [x] Tulis verdict per temuan pada SHA final, metode, severity, dan scope yang belum diuji; lakukan review ulang source yang berubah.

Selesai ketika seluruh temuan relevan ditutup dengan bukti atau mempunyai blocker spesifik yang tetap terbuka. Verdict menentukan kandidat/runtime mana yang bisa dilanjutkan; PASS terbatas tidak berubah menjadi clearance seluruh main. Commit fix dan laporan dengan scope terpisah.

## COMP-003 — Tambahkan tes komponen dan coverage yang valid

Status: PASS (tooling/harness; bukan penutupan tiket UI). Prioritas: P0. Dependency: COMP-001. Bukti: [hasil harness dan coverage](docs/completion/COMP-003-coverage.md).

- [x] Siapkan lingkungan DOM dan tes interaksi React pada runner yang sesuai repo; tambahkan dev dependency yang diperlukan beserta lockfile.
- [x] Gunakan React asli dan provider Next, fixture jaringan, deferred response, cleanup per tes, serta query berdasarkan label/role.
- [x] Buktikan harness menjalankan effect, klik/input, update async, unmount, dan pergantian query; request tidak terduga harus menggagalkan tes.
- [x] Tambahkan command coverage yang dapat direproduksi dan memetakan hasil ke source JSX melalui sourcemap.
- [x] Ukur coverage terhadap base terpin: laporkan baris baru yang covered/eligible, persentase, serta pengecualian dengan alasan. Target >=80% kode baru pada tiket yang mensyaratkannya.

Selesai ketika harness dan laporan source coverage dapat dipercaya, tanpa mengganti state/hook React untuk meloloskan tes. Pisahkan hasil komponen dari SSR dan browser E2E. Commit tooling/test saja; ini tidak menutup browser QA.

## COMP-004 — Selesaikan lifecycle Study

Status: PASS pada kandidat Study terpin (browser/runtime tetap COMP-010). Prioritas: P0. Dependency: COMP-003. Tiket: TASK-020/047. Bukti: [regresi lifecycle Study](docs/completion/COMP-004-study.md).

- [x] Uji completion lesson A: pilihan tetap A setelah sukses kecuali pengguna memilih lesson lain.
- [x] Mulai completion A, pindah ke B, lalu selesaikan respons A; receipt/error/busy A tidak muncul pada B.
- [x] Uji checkpoint benar/salah, jawaban/feedback saat berpindah lesson, dan respons terlambat setelah unmount.
- [x] Uji duplicate click, response loss tanpa replay otomatis, already-completed dengan `newly_completed:false`, serta reward yang berasal dari receipt server.
- [x] Uji progress unavailable/unknown/retry, loading/error/empty, source aman/broken, dan CTA assessment.
- [x] Journey hanya menandai tahapan yang terbukti oleh data; lakukan fix jika tes menemukan defect.
- [x] Jalankan regresi, build, coverage kode baru, dan update changelog/kontrak yang terpengaruh.

Selesai ketika lifecycle interaktif dan isolasi state terbukti, seluruh kasus wajib PASS, serta coverage baru >=80%. Helper/SSR test saja tidak cukup. Commit fix bersama regresi yang relevan.

## COMP-005 — Selesaikan dashboard dan profil

Status: PASS untuk interaksi Dashboard/Profile kandidat TASK-042; revoke server tetap COMP-008. Prioritas: P0. Dependency: COMP-003. Tiket: TASK-016/042. Bukti: [regresi Dashboard/Profile](docs/completion/COMP-005-dashboard-profile.md).

- [x] Uji akun baru, data terisi, loading/empty, progress gagal, target gagal, roadmap gagal, retry, respons usang, dan pergantian query.
- [x] Target hanya berasal dari query tervalidasi; tanpa target tampilkan Pilih target. Data identitas/XP/completion memakai server.
- [x] Uji username fallback/email kosong/tanggal tidak valid, fitur profil unavailable, serta refresh profil yang gagal tanpa mengarang sukses.
- [x] Uji notice logout dari event nyata, URL `logged_out=1` palsu, dan accessible name Keluar. Kandidat ini hanya mengakhiri sesi lokal secara eksplisit; revoke server/failure retry ada di COMP-008.
- [x] Ukur coverage kode baru >=80%, jalankan tes/build, dan perbarui copy/kontrak bila diperlukan.

Selesai ketika acceptance state/data dan coverage terpenuhi. Ukuran 375/768/1440, layout, tema, dan keyboard browser diselesaikan pada COMP-010.

## COMP-006 — Selesaikan diagnostic dan roadmap

Status: PASS untuk acceptance kandidat terpisah; integrasi/browser matrix lanjut COMP-007/010. Bukti: [laporan COMP-006](docs/completion/COMP-006-diagnostic-roadmap.md). Prioritas: P0. Dependency: COMP-003. Tiket: TASK-018/019.

- [x] Pin kandidat revisi terbaru secara terpisah; fix fokus/TDZ dinilai pada SHA kandidat yang sesuai.
- [x] Diagnostic DOM/Chrome: semua ID terkirim, Belum tahu string kosong, pilihan tidak submit otomatis, prev/next mempertahankan jawaban, submit lock, abort/query berubah, uncertain submit/recovery, latest 404/error/retry, serta konfirmasi keluar/fokus.
- [x] Hasil diagnostic memakai overall score/tanggal/skill/rekomendasi server; tidak membuat XP, durasi, histori, atau mastery baru dari asumsi (helper/DOM dan Chrome smoke).
- [x] Roadmap helper/DOM/Chrome: denominator unik, duplicate, zero guard, urutan server, selection, query target, dan studyHref.
- [x] Roadmap tanpa attempt diagnostic, skill cukup/empty, prerequisite belum cukup, loading/error/empty; tidak mengklaim locked/completion/credential di luar kontrak.
- [x] Jalankan tes/build/coverage pada dua kandidat dan commit defect/regresi yang terbukti; lihat laporan untuk acceptance yang masih terbuka.

Selesai ketika revisi final dan perilaku komponen terbukti. Panel roadmap pada 375px dan mode fokus diagnostic masih diuji di browser pada COMP-010.

## COMP-007 — Review final dan susun kandidat integrasi

Status: **CHANGES — kandidat parsial dipin, komposisi final tertahan konflik**. Bukti: [laporan COMP-007](docs/completion/COMP-007-integration-review.md). Prioritas: P0. Dependency: COMP-002/004/005/006. Tiket: TASK-048.

- [x] Inventaris history/base, file diff, serta overlap semua kandidat; petakan konflik integrasi.
- [x] Rekonsiliasi report terdahulu dan review langsung kandidat komposisi keamanan + Study.
- [ ] Selesaikan full source diff review untuk setiap kandidat dan review ulang semua finding pada satu SHA gabungan stabil.
- [x] Laporkan blocker integrasi yang tereproduksi dan perilaku commit yang perlu dipertahankan; perubahan gabungan wajib direview ulang.
- [x] Pin kandidat komposisi awal pada branch/worktree terpisah tanpa menimpa kandidat lama atau main.
- [x] Tulis verdict sementara per SHA/scope dan jelaskan bahwa ini self-review, bukan approval independen.

Selesai ketika kandidat stabil dan keputusan review dapat diaudit. Review yang didelegasikan owner dapat dikerjakan assistant, tetapi tidak boleh ditulis sebagai approval orang lain. Commit laporan; integrasi ke main/keputusan kartu adalah langkah terpisah.

## COMP-008 — Uji auth web dan Mobile dengan backend disposable

Status: **IN PROGRESS — web revoke smoke pass; Mobile Flutter/runtime belum tersedia**. Bukti: [laporan COMP-008](docs/completion/COMP-008-auth-runtime.md). Prioritas: P0. Dependency: COMP-007 (masih CHANGES). Tiket: TASK-009/012.

- [x] Bootstrap backend kandidat dengan local config, SQLite sementara, mock provider, port milik run, dan akun sintetis; migrasi blacklist diterapkan. Web saat ini Bearer in-memory, bukan cookie HttpOnly; Mobile menggunakan Bearer.
- [x] Smoke web/API via Next proxy: register, login, `/me`, logout refresh blacklist, reuse refresh ditolak, akses token lama masih valid hingga expiry.
- [ ] Uji web 503/timeout/network, origin/CSRF, refresh paralel/race dan expiry pada runtime; logout failure hanya diuji di frontend test.
- [ ] Mobile nyata: register -> login username -> /auth/me -> restart/restore -> logout; pastikan secure storage dan server revoke sesuai kontrak.
- [x] Backend accounts tests, full Django suite, OpenAPI, frontend suite/build/coverage dijalankan pada candidate SHA; Flutter analyze/test/build belum dapat dijalankan karena Flutter tidak ditemukan di PATH.
- [ ] Uji Mobile 400/401/offline, refresh gagal/paralel, storage failure dan logout copy. OTP/reset/Google tetap unavailable.

Selesai ketika integrasi runtime terbukti. Dua tab, reload browser, dan isolasi SSR antarpengguna dilengkapi pada COMP-010. APK build/unit test saja tidak membuktikan integrasi Mobile.

## COMP-009 — Tutup fixture dan QA backend runtime

Status: **IN PROGRESS — fixture in-memory + endpoint smoke lulus; PostgreSQL/Redis belum tersedia**. Bukti: [laporan COMP-009](docs/completion/COMP-009-backend-runtime.md). Prioritas: P0. Dependency: COMP-007 (masih CHANGES). Tiket: TASK-029/027.

- [x] Jalankan fixture backend in-memory `--catalog` pada port 8011; validasi migrasi/seed, `/career-tracks/` dan `/health/` HTTP 200, startup dan shutdown normal. Proxy Next, cleanup saat failure, dan isolasi konkurensi masih terbuka.
- [ ] Sediakan PostgreSQL disposable; uji koneksi terpisah dengan interleaving deterministik, mastery tidak turun, XP tidak hilang/ganda, dan isolasi user. Catat skip sebagai NOT RUN.
- [ ] Sediakan Redis disposable; buktikan cache/throttle lintas proses, 429/retry/expiry, dan destination guard. Jangan mewarisi instance pengguna.
- [x] Probe guard mode production dengan environment sintetis `APP_ENV=production`, `DB_ENGINE=sqlite`; startup ditolak sebelum Django berjalan. Probe hosted dengan PostgreSQL/provider nyata masih terbuka.
- [ ] Petakan acceptance QA backend lama ke bukti baru dan simpan run ID/SHA/environment/exit/artefak/cleanup.

Selesai ketika acceptance runtime mempunyai hasil nyata atau blocker spesifik tetap terbuka. Hasil SQLite tidak menutup row locking PostgreSQL. Commit fixture/test/runbook yang berubah, tanpa artefak runtime atau secret.

## COMP-010 — Browser QA kandidat integrasi

Status: **BLOCKED untuk matriks penuh — tool Sokudo tidak diekspos pada sesi; `.sokudo/` menyimpan 16 run historis yang semuanya gagal**. Prioritas: P0. Dependency: COMP-008/009 dan runner tersedia. Tiket: TASK-027/033/043/049; acceptance browser semua fitur terkait.

- [x] Periksa ulang discovery/akses runner. Tool tidak tersedia di sesi; artefak historis membuktikan runner pernah berjalan tetapi run gagal di runtime/login/scroll. Lihat laporan COMP-006.
- [ ] Pin runtime/fixture/source, validasi flow existing, selector unik, dan kemampuan runner; jangan menyebut validasi YAML sebagai run PASS.
- [ ] Uji viewport 375/768/1440, light/dark, reduced motion, keyboard/fokus, loading/empty/error/retry, sidebar, dan public verification.
- [ ] Uji logout success/failure/expired, reload, dua tab, refresh paralel/race, isolasi sesi, dan SSR lintas pengguna.
- [ ] Uji lifecycle Study, roadmap selection/panel mobile, diagnostic recovery/exit, mock/draft label, serta state dashboard/profil.
- [ ] Simpan run ID, screenshot/log yang aman, dan matriks per acceptance PASS/FAIL/NOT RUN; kembalikan defect ke task implementasi lalu uji ulang perubahan relevan.

Selesai ketika seluruh baris wajib mempunyai hasil aktual yang lolos pada kandidat final. Untuk runner yang masih unavailable, task tetap BLOCKED; pekerjaan independen dapat dilanjutkan. Jangan mengklaim tes DOM sebagai browser E2E.

## COMP-011 — Sumber, rehearsal, dan laporan akhir

Status: TODO. Prioritas: P0. Dependency: COMP-010; persiapan sumber/runbook bisa dimulai lebih awal. Plan lama: 002/003/004/005.

- [ ] Periksa ulang 13 sumber dan URL yang dulu 503; bedakan status reachability, redirect/canonical, dan lisensi. Jangan mengubah klaim reuse tanpa bukti.
- [ ] Pastikan sumber yang digunakan dalam demo terbuka di browser operator; pertahankan label mock/draft dan failed attempt sesuai respons server.
- [ ] Mulai dari runtime bersih dan lakukan rehearsal catalog -> diagnostic -> result -> roadmap -> study/checkpoint/completion -> rules/mock assessment -> draft credential -> public verification tanpa login.
- [ ] Buktikan credential draft invalid/unverified/unanchored, tidak ada reward ganda, dan restart database in-memory dijelaskan di runbook.
- [ ] Update `docs/demo-test-matrix.md`, `docs/demo-runbook.md`, `docs/source-review.md`, serta indeks plan berdasarkan hasil aktual pada SHA final.
- [ ] Laporkan task berhasil, commit, acceptance terbuka, blocker/pemilik/tindakan berikut, dan keputusan integrasi yang masih diperlukan. Rekonsiliasi kartu asal ketika akses board tersedia.

Selesai ketika rehearsal penuh lulus, sumber demo terbukti, dokumentasi sesuai runtime, dan tidak ada acceptance wajib yang disembunyikan. Commit dokumentasi setelah verifikasi; jangan menandai Plan 002–005 DONE sebelum done criteria masing-masing terpenuhi.

## Format laporan per task

```text
Task COMP / tiket asal:
Status: TODO | IN PROGRESS | PASS | FAIL | BLOCKED
Scope selesai dan acceptance terbuka:
Base SHA / final SHA / branch / worktree:
File berubah / commit:
Command / cwd / environment / exit code:
Hasil pass / fail / skip / NOT RUN:
Coverage source dan kode baru / metode:
Review / pelaksana / batas independensi:
Run ID / artefak / cleanup:
Blocker konkret / tindakan berikut / pemilik:
```

Task dengan source/test/docs yang berubah di-commit setelah verifikasi relevan lulus. Tes ulang tanpa perubahan tidak membutuhkan commit kosong. Penghapusan `HANDOFF.md` root dan pembuatan plan/task ini merupakan perubahan dokumentasi; source aplikasi tidak diubah dalam langkah ini.
