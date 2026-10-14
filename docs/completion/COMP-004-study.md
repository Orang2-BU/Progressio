# COMP-004 — Lifecycle Study

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Verdict: PASS untuk source/interaksi Study kandidat ini; tidak mencakup browser/device QA.

## Kandidat

- Branch: `task-047-fix-revisi-ruang-belajar-task-020-dan-lengkapi-b`
- SHA sesudah perubahan tes: `834d6ec` (`test: cover Study query lifecycle and late responses`)
- Base pembanding: merge-base dengan `main`, `323c4e936f7dd144c317077f967f7a2ea9e6505b`.
- Source fix Study yang diuji sebelumnya tetap ada pada commit branch `4c75066`; COMP-004 menambah tes regresi tanpa mengubah source produk.

## Verifikasi

| Command dari `front-end/` | Hasil |
| --- | --- |
| `node --test tests/study-flow.test.js tests/study-interactions.test.js` | 13/13 PASS |
| `npm test` | 64/64 PASS, 0 skip |
| `npm run coverage` | 64/64 PASS; aggregate JSX yang terpakai 72.13% |
| `npm run build` | PASS; Next.js membuat 13 route |
| `git diff --check` | PASS |

Coverage dari sourcemap JSX pada run final: `Study.jsx` 92.48% line, `StudyInteractions.jsx` 91.02% line. Changed-line hitung konservatif terhadap semua baris tambahan pada base terpin: Study `112/123` covered, interaction boundary `71/78` covered; total `183/201` (91.0%). Baris kosong/komentar tidak dikecualikan dari denominator, sehingga angka ini tidak dinaikkan dengan pengecualian.

Tes mengeksekusi React dan provider Next sungguhan dengan JSDOM/fetch fixture. Yang dibuktikan: selection tetap pada lesson yang baru selesai; busy/error/receipt lesson A tidak bocor ke B; query berubah membatalkan request lama; respons terlambat dan completion setelah unmount diabaikan; checkpoint benar/salah dan input/feedback terisolasi; duplicate click hanya mengirim sekali; completion `newly_completed:false` tidak memberi reward; error/unknown progress dapat diulang; response loss tidak otomatis replay; error/empty/loading, source broken, CTA assessment, dan journey yang tidak mengarang tahapan.

Tidak ada changelog/kontrak produk diubah karena commit task ini hanya menambah tes. Audit layout ukuran layar, keyboard, dua tab, SSR antarpengguna, runtime auth, serta browser/Sokudo tetap COMP-008/010. Tes ini tidak menggantikan QA browser.
