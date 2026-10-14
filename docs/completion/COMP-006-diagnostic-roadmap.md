# COMP-006 — Diagnostic dan Roadmap

Tanggal eksekusi: 14 Oktober 2026 (Asia/Jakarta). Status: **IN PROGRESS; belum memenuhi semua acceptance**.

## Kandidat dan perubahan

Kandidat yang ditinjau terpisah karena bukan satu riwayat Git yang kompatibel:

| Scope | Base | Final | Branch/worktree | Commit eksekusi |
| --- | --- | --- | --- | --- |
| Diagnostic | `59ebc369eff75dd063ca568322e0ca3cade23705` | `c8988d2bfcdfd1e05440362de0385949ecfd0c86` | `task-018-safe-candidate` / `.sokudo/worktrees/task-018-safe-candidate` | `f5b8f1f`, `e5edafb`, `c8988d2` |
| Roadmap | `59ebc369eff75dd063ca568322e0ca3cade23705` | `2c4c5abd5dd8768056e59297d1a549a4f39081dc` | `task-019-safe-candidate` / `.sokudo/worktrees/task-019-safe-candidate` | `2c4c5ab` |

Tidak ada merge ke `main` atau asumsi bahwa kedua branch dapat digabung langsung.

## Bukti

- Diagnostic component DOM: 4/4 lulus (navigasi/jawaban persisten, “Belum tahu” sebagai `""`, tidak submit otomatis, response loss tidak replay, submit lock, dan abort request ketika query target berubah).
- Regression menemukan defect di `src/api.js`: parser response bersama membuang semua JSON array sukses, termasuk daftar soal diagnostic. Fix mempertahankan array untuk respons sukses sementara normalisasi error tetap dilakukan. Test API membuktikan daftar array dipertahankan.
- Diagnostic seluruh suite: 59/59 lulus; `npm run coverage` lulus, `Diagnostic.jsx` 76.76% line dan `api.js` 96%. Fix API yang berubah diuji langsung; tidak ada perubahan line pada `Diagnostic.jsx`.
- Roadmap component DOM: 3/3 lulus untuk render urutan server, pemilihan detail/prasyarat/study URL, roadmap kosong tanpa klaim credential, retry error, serta abort query lama.
- Roadmap seluruh suite: 38/38 lulus; coverage sourcemap `Roadmap.jsx` 100% line; Next production build lulus (13 route).
- Kedua kandidat `npm run build` lulus. Coverage berjalan melalui c8 dengan source map inline; file coverage diabaikan Git. `git diff --check` bersih sebelum commit.

## Acceptance yang belum clear

- Focus trap/return-focus dialog exit Diagnostic belum terbukti. Upaya JSDOM untuk fokus dialog menyebabkan proses test hang dan alokasi buffer habis; test tidak disimpan sebagai PASS. Runner browser tidak tersedia saat dicek ulang; daftar tool sesi tidak menemukan browser/Playwright/Sokudo tool.
- DOM error/retry/empty/404 pada semua state Diagnostic dan hasil terbaru belum diuji penuh sebagai alur pengguna; kontrak helper/API/SSR memiliki tes terkait, tetapi itu bukan pengganti lifecycle komponen browser.
- Query-abort dan link/selection Roadmap lulus di JSDOM, tetapi keyboard/focus visual dan layout mobile menunggu COMP-010.
- Kandidat Diagnostic dan Roadmap masih branch terpisah. Integrasi/review diff gabungan adalah COMP-007, belum dilakukan.

## Perintah dan hasil

`npm test`, `npm run coverage`, `npm run build` dijalankan dari folder `front-end` masing-masing worktree; semuanya exit code 0 pada final SHA tabel. Diagnostic 59 pass, Roadmap 38 pass. Tidak ada test failure yang tersisa. Fokus dialog JSDOM dihentikan karena harness tidak stabil, dicatat sebagai belum clear—not product PASS/FAIL.

Review dilakukan oleh assistant (self-review, bukan review independen Bimo/Adit). Tidak ada browser run ID atau screenshot.

## Keputusan

Pekerjaan yang aman telah committed di kandidat masing-masing. COMP-006 tetap **IN PROGRESS**, bukan PASS, sampai state Diagnostic yang tersisa dibuktikan dengan harness/browser yang stabil atau ada keputusan scope eksplisit. COMP-007 menunggu dependency COMP-006 clear.
