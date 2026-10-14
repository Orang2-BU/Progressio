# COMP-005 — Dashboard dan Profile

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Verdict: PASS untuk interaksi Dashboard/Profile dan kontrak yang tersedia pada kandidat TASK-042; browser dan revoke server tetap terpisah.

## Kandidat

- Branch: `task-042-safe-ringkasan-profil`
- SHA sesudah penambahan DOM regressions: `80d50fd` (`test: cover dashboard and profile interactions`)
- Base pembanding: merge-base dengan `main`, `59ebc369eff75dd063ca568322e0ca3cade23705`.
- Produk tidak berubah dalam task ini; commit menambah dev-only JSDOM/c8, test support, tes interaktif, serta lockfile.

## Verifikasi

Semua command dijalankan dari `front-end/`:

| Command | Hasil |
| --- | --- |
| `npm test` | 54/54 PASS, 0 skip |
| `npm run coverage` | 54/54 PASS; JSX line/statement aggregate 90.17% |
| `npm run build` | PASS; Next.js berhasil membuat 13 route |
| `npm audit` | 0 kerentanan pada 147 dependency yang dilaporkan npm |
| `git diff --check` | PASS |

Coverage sourcemap JSX: `Dashboard.jsx` 94.50%, `Profile.jsx` 100%. Hitung konservatif terhadap semua line tambahan sejak base: Dashboard `86/91` covered; Profile `114/114`; total `200/205` (97.56%). Baris non-eksekusi tidak dikeluarkan dari denominator.

React asli dan Next App Router providers dirender dalam JSDOM dengan fetch fixture/deferred responses. Tes membuktikan data target/progress/next step server-backed, akun tanpa target dan target invalid, loading/error/empty, progress/target/roadmap failure serta retry, pergantian query membatalkan respons lama, Profile loading/empty/populated/unavailable state, username/email/tanggal fallback, reload profil gagal tanpa menghapus identitas, serta event logout dan nama tombol yang accessible.

### Batas logout

Pada kandidat ini tombol Profile hanya mengakhiri sesi lokal dan copy-nya menyatakan token server tidak dicabut. Tidak ada request remote logout yang bisa gagal/di-retry pada jalur ini. Karena itu tes mengunci perilaku lokal yang jujur; blacklisting/revoke serta 403/503/timeout/retry wajib dituntaskan pada COMP-008 saat kandidat TASK-009 dan UI direkonsiliasi. Ini bukan klaim bahwa token server sudah dicabut.

Breakpoint 375/768/1440, keyboard, multi-tab, dan browser/Sokudo tetap COMP-010.
