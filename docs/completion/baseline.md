# COMP-001 — Baseline kandidat dan lingkungan

Tanggal pemeriksaan: 14 Oktober 2026 (Asia/Jakarta).

## Repository dan worktree

- Branch dokumentasi: `codex/completion-plan`, HEAD `4bfbaf4aaaac96537b0f6d3cad6441c98cef2ba7`.
- `main` dan `origin/main`: `ded12712636f01185c7c1ef49ff84b74796b528d`.
- Worktree root mempunyai `.sokudo/` untracked milik workspace; dipertahankan dan tidak dimasukkan ke commit.
- Worktree kandidat di bawah ini berstatus clean saat diperiksa.

| Area | Branch / HEAD | Merge base dengan main | Worktree |
| --- | --- | --- | --- |
| Security transport upstream | `codex/bimo-transport-security` / `dc1e0dff5d2d59da5bbcc9ffae3484483ff46368` | `ded12712636f01185c7c1ef49ff84b74796b528d` | `.sokudo/worktrees/bimo-transport-security` |
| Web session/backend | `codex/task-009-current-candidate` / `517979d57c2bda7bcfb4020f3b076975797fb39a` | `ded12712636f01185c7c1ef49ff84b74796b528d` | `.sokudo/worktrees/task-009-current-candidate` |
| Mobile auth | `task-012-hubungkan-autentikasi-mobile-ke-api-dan-hilangka` / `85e8a43f2e19d68c19df449a8a05b7bf9935aa54` | `323c4e936f7dd144c317077f967f7a2ea9e6505b` | `.sokudo/worktrees/task-012-hubungkan-autentikasi-mobile-ke-api-dan-hilangka` |
| QA fixture | `task-029-implementasikan-bukti-regresi-dan-runbook-untuk` / `1c4759077f493a78efeb963d71cd4d75574b1014` | `6720ba17f202ae8f0872e74611f06f6c83d8a17d` | `.sokudo/worktrees/task-029-implementasikan-bukti-regresi-dan-runbook-untuk` |
| Study/dashboard composition | `task-047-safe-candidate` / `36904a35c7ffcac40472f403bbfb0f57d720d104` | `59ebc369eff75dd063ca568322e0ca3cade23705` | `.sokudo/worktrees/task-047-safe-candidate` |
| Diagnostic safe candidate | `task-018-safe-candidate` / `fed4523d2b583bf9249bbd25c0ece9e5d12e801c` | `59ebc369eff75dd063ca568322e0ca3cade23705` | `.sokudo/worktrees/task-018-safe-candidate` |
| Roadmap safe candidate | `task-019-safe-candidate` / `92d1f20c0e740a2b2d44160d8ebbefbfe987b51a` | `59ebc369eff75dd063ca568322e0ca3cade23705` | `.sokudo/worktrees/task-019-safe-candidate` |
| Dashboard/profile recovery | `task-042-safe-ringkasan-profil` / `da3ae263e7acbf144f983b81721ab6d07b3fc0ad` | `59ebc369eff75dd063ca568322e0ca3cade23705` | `.sokudo/worktrees/task-042-pulihkan-kandidat-aman-ringkasan-dan-profil-untu` |
| QA composition | `task-043-safe-composition` / `de6adddb5c9b148d52eb6da78a48819214485c0d` | `59ebc369eff75dd063ca568322e0ca3cade23705` | `.sokudo/worktrees/task-043-pulihkan-kandidat-qa-aman-untuk-menutup-task-033` |

Merge base berbeda-beda. Jangan menganggap branch tersebut sebagai satu kandidat terpadu; COMP-007 harus memilih dan memeriksa full diff sebelum runtime integrasi.

## Alat yang ditemukan

| Alat | Hasil |
| --- | --- |
| Node.js | `v24.21.0` |
| npm | `11.19.0` |
| Python | `3.12.10` |
| Flutter | `3.41.9` pada `D:\flutter\bin\flutter.bat` |
| Dart | `3.11.5` |
| Sokudo E2E | Tidak ditemukan di tool sesi pada 14 Oktober 2026 |
| Docker CLI | Tidak ditemukan |
| PostgreSQL `psql` / `pg_isready` | Tidak ditemukan; test Django sebelumnya juga tidak menemukan server di `localhost:5432` |
| Redis CLI | Tidak ditemukan |
| `pip-audit` | Tidak ditemukan; `python -m pip_audit --version` berakhir dengan `No module named pip_audit` |
| Node DOM component test | Kandidat frontend saat pemeriksaan hanya memakai Node test runner dan React SSR helper; `jsdom`, `@testing-library/react`, `@testing-library/dom`, `happy-dom`, dan `react-test-renderer` tidak ditemukan |

Pemeriksaan ini hanya menginventarisasi executable dan dependency. Belum memasang tool, memulai service, menjalankan fixture, atau mengaudit versi dependency dalam COMP-001.

## Kandidat tes offline

Kandidat offline awal untuk frontend adalah `task-047-safe-candidate` beserta test helper-nya; diagnostic dan roadmap juga harus direkonsiliasi dari branch aman masing-masing. Backend accounts, Mobile, dan fixture memakai branch terpisah di tabel. Source Mobile mempunyai merge base lama; evaluasi dependency transport/backend sebelum integrasi.

Hasil tes yang sudah tersedia sebelum COMP-001: frontend 52/52 dan Next build pada kandidat Study composition; accounts 24/24 pada SQLite; Mobile analyze bersih dan 23/23; fixture 7/7. Hasil ini tidak dianggap hasil run baru dan tidak membuktikan acceptance browser/runtime yang belum dijalankan.

## Tindakan dependency

- COMP-002: periksa dependency aktual dan pasang alat audit Python pada environment terisolasi bila tidak mengubah dependency aplikasi.
- COMP-003: siapkan DOM runner sebagai dev-only dependency pada branch terisolasi, lalu buktikan React effects dan event berjalan.
- COMP-007: susun manifest integrasi baru setelah review base/diff, bukan dengan merge branch berbeda tanpa rekonsiliasi.
- COMP-009: siapkan PostgreSQL dan Redis milik run. Saat ini Docker/CLI tidak tersedia; tentukan cara penyediaan lokal yang aman sebelum klaim acceptance database.
- COMP-010: runner Sokudo belum tersedia. Uji ulang availability sebelum browser QA dan catat run ID jika berhasil.
