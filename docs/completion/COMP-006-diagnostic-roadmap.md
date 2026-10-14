# COMP-006 — Diagnostic dan Roadmap

Tanggal eksekusi: 14 Oktober 2026 (Asia/Jakarta). Status: **PASS untuk acceptance COMP-006 pada kandidat terpisah**. Browser matrix lengkap tetap COMP-010.

## Kandidat dan perubahan

Kandidat yang ditinjau terpisah karena bukan satu riwayat Git yang kompatibel:

| Scope | Base | Final | Branch/worktree | Commit eksekusi |
| --- | --- | --- | --- | --- |
| Diagnostic | `59ebc369eff75dd063ca568322e0ca3cade23705` | `8cc9638c9fdad53bd9ee8d5199240dc7800b172e` | `task-018-safe-candidate` / `.sokudo/worktrees/task-018-safe-candidate` | `f5b8f1f`, `e5edafb`, `c8988d2`, `8cc9638` |
| Roadmap | `59ebc369eff75dd063ca568322e0ca3cade23705` | `2c4c5abd5dd8768056e59297d1a549a4f39081dc` | `task-019-safe-candidate` / `.sokudo/worktrees/task-019-safe-candidate` | `2c4c5ab` |

Tidak ada merge ke `main` atau asumsi bahwa kedua branch dapat digabung langsung.

## Bukti

- Diagnostic component DOM: 4/4 lulus (navigasi/jawaban persisten, “Belum tahu” sebagai `""`, tidak submit otomatis, response loss tidak replay, submit lock, dan abort request ketika query target berubah).
- Regression menemukan defect di `src/api.js`: parser response bersama membuang semua JSON array sukses, termasuk daftar soal diagnostic. Fix mempertahankan array untuk respons sukses sementara normalisasi error tetap dilakukan. Test API membuktikan daftar array dipertahankan.
- Regression browser kedua menemukan defect di `Diagnostic.jsx`: mode hasil memberikan object attempt ke penghitung progres yang mengharapkan array soal, sehingga halaman hasil crash (`questions.filter is not a function`). Guard berdasarkan mode result ditambahkan dan diuji di DOM/browser.
- Diagnostic component DOM: 5/5 lulus; mencakup navigasi/jawaban persisten, “Belum tahu” sebagai `""`, tidak submit otomatis, response loss tidak replay, submit lock, abort saat target berubah, dan render attempt server.
- Diagnostic seluruh suite: 61/61 lulus; `npm run coverage` lulus, `Diagnostic.jsx` 77.11% line, `diagnostic.js` 91.66%, dan `api.js` 96%. Fix API dan render-result tercakup test langsung.
- Roadmap component DOM: 3/3 lulus untuk render urutan server, pemilihan detail/prasyarat/study URL, roadmap kosong tanpa klaim credential, retry error, serta abort query lama.
- Roadmap seluruh suite: 38/38 lulus; coverage sourcemap `Roadmap.jsx` 100% line; Next production build lulus (13 route).
- Kedua kandidat `npm run build` lulus. Coverage berjalan melalui c8 dengan source map inline; file coverage diabaikan Git. `git diff --check` bersih sebelum commit.
- Browser smoke lokal: Chrome headless sistem di viewport 390×844; Next dev server kandidat Diagnostic pada port 3106; semua API dimock dengan respons sintetis; tidak memakai profil/browser state pengguna. Assertion lulus: dialog menerima fokus dan mengembalikannya ke tombol pemicu; payload submit `{answers:{1:"yes",2:""}}`; hasil server `50 / 100`; 503 retry pulih; latest 404 menampilkan empty-state; Roadmap menampilkan 2 langkah dan link `/study?track=10&learn=4`. Playwright Core hanya dipasang sementara (`npm install --no-save --package-lock=false`), script smoke dihapus setelah run, lockfile tidak berubah.

## Acceptance yang belum clear

- E2E browser dengan backend sebenarnya belum clear; smoke Chrome menggunakan mock API. Layanan pada port 3000/3133/8000/8011/5432/6379 tidak sedang listen saat diperiksa.
- Matriks viewports 375/768/1440, tema, reduced-motion, keyboard penuh, dua-tab/session, serta flow backend/assessment/credential end-to-end menunggu COMP-010.
- Kandidat Diagnostic dan Roadmap masih branch terpisah. Integrasi/review diff gabungan adalah COMP-007, belum dilakukan.

## Bukti Sokudo yang ditemukan di `.sokudo/`

Inventaris memiliki 16 `result.json`; seluruh run tercatat `failed`. Run assessment `2b80c4f9-31e6-49e4-838e-42829a478580` (7 Okt) lolos login dan assertion halaman Assessment, kemudian gagal `scrollUntilVisible` pada target evidence; screenshot menunjukkan viewport sudah di bagian bawah form sementara target berada di atas. Run `af83846b-caa8-4a65-a55e-7c836e95a9e9` (12 Okt) gagal assertion halaman setelah login; screenshot menunjukkan notice respons API tak dapat dibaca. Dua run `progressio-demo` gagal pada `launchApp` karena URL runtime tidak tersedia. Run-run ini bukti gagal/diagnostik, bukan PASS.

## Perintah dan hasil

`npm test`, `npm run coverage`, `npm run build` dijalankan dari folder `front-end` masing-masing worktree; semuanya exit code 0 pada final SHA tabel. Diagnostic 61 pass, Roadmap 38 pass. Smoke Chrome lokal exit 0 dengan assertion di atas. Upaya JSDOM fokus dialog sebelumnya tidak stabil; hasil tidak dipakai karena kemudian fokus diuji langsung di Chrome.

Review dilakukan oleh assistant (self-review, bukan review independen Bimo/Adit). Tidak ada browser run ID atau screenshot.

## Keputusan

Pekerjaan dan regresi COMP-006 telah committed pada kandidat masing-masing dan acceptance paket ini PASS. Kandidat masih terpisah; lanjutkan ke COMP-007 untuk review full diff dan keputusan kandidat integrasi. Full browser/backend rehearsal tetap acceptance COMP-010/011.
