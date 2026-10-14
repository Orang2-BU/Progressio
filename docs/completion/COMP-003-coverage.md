# COMP-003 — DOM harness dan JSX coverage

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Scope: validasi test tooling/harness; ini tidak menyatakan fitur Dashboard/Profile/Diagnostic/Roadmap atau browser QA selesai.

## Kandidat dan perubahan

- Branch `task-047-fix-revisi-ruang-belajar-task-020-dan-lengkapi-b`, hasil setelah perubahan tooling: `cd21348`.
- DOM interaction harness yang sudah ada memakai React/ReactDOM sungguhan, provider Next App Router, JSDOM, fixture `fetch`, promise tertunda, event pengguna, accessible label/role helper, dan cleanup/unmount per test.
- Commit tooling `cd21348` menambah dev dependency `c8` + lockfile, command `npm run coverage`, sourcemap inline pada transform Babel, dan ignore output `front-end/coverage/`.
- Coverage dijalankan pada JSX source (laporan menyebut file `.jsx` dan line source), bukan SSR markup saja. Helper merender komponen asli; tidak mengganti React hooks/state.

## Verifikasi

Semua command dijalankan di `front-end/` kandidat tersebut:

| Command | Hasil |
| --- | --- |
| `npm run coverage` | exit 0; 59 passed, 0 failed; coverage seluruh JSX yang terpakai 71.19% statements/lines |
| Coverage `Study.jsx` | 87.86% lines; branch 79.41%; function 81.81% |
| Coverage `StudyInteractions.jsx` | 91.02% lines; branch 89.47%; function 100% |
| Coverage `Dashboard.jsx` | 45.23% lines — gap perilaku masih terbuka di COMP-005 |
| Coverage `Profile.jsx` | 80.19% lines — belum cukup membuktikan semua state acceptance COMP-005 |
| `npm run build` | exit 0; Next 16.3.8, seluruh 13 route berhasil dibuat |
| `npm audit` | exit 0; 0 vulnerability; 147 dependency terinventaris (93 dev, 38 optional termasuk overlap npm metadata) |
| `git diff --check` | exit 0 |

Jalankan `npm run coverage` kembali untuk menghasilkan `coverage/coverage-final.json`; artefak diabaikan Git dan bukan bukti browser/E2E.

## Batas coverage

Coverage aggregate 71.19% bukan target kelulusan aplikasi. Target >=80% berlaku per kode baru dari tiap tiket terhadap base-nya. Garis kode berubah yang memenuhi target belum dihitung formal karena perubahan Dashboard/Diagnostic/Roadmap berada pada branch berbeda; klaim per tiket dilanjutkan pada COMP-004/005/006 setelah pinning base dan diff. JSX yang tidak terimpor pada suite tidak dimasukkan ke laporan run ini. Test React interaktif membuktikan Study effect/event/update asynchronous dan cleanup, tetapi pergantian route query/unmount-late-response perlu ditutup sebagai acceptance Study.
