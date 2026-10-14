# COMP-009 — Fixture dan QA backend runtime

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Status: **IN PROGRESS — smoke fixture in-memory lulus; database/cache concurrency belum dijalankan**. Run dijalankan assistant, bukan QA independen.

## Runtime yang dipin

- Candidate branch/worktree: `codex/completion-integration`, `../progressio-completion-integration`.
- Source SHA: `48cca732318735dcf24a95580b8443415f26b6f9`.
- Command dari root kandidat: `python front-end/tests/backend_server.py --catalog`.
- Backend memakai SQLite `:memory:` dan bind hanya ke `127.0.0.1:8011`; `seed_demo` serta fixture katalog berjalan pada proses disposable.
- Environment Python 3.12. Tidak memakai database, credential, Docker volume, atau server milik pengguna.

## Hasil aktual

| Acceptance | Hasil |
| --- | --- |
| Startup, migrations, seed dan fixture katalog | PASS; server melaporkan disposable in-memory di `127.0.0.1:8011` |
| `GET /api/v1/career-tracks/` | HTTP 200, 591 byte |
| `GET /api/v1/health/` | HTTP 200, body `status=ok` |
| Next proxy `http://127.0.0.1:3000/api/v1/career-tracks/` -> fixture | HTTP 200; response berisi `Backend Engineering` |
| Next proxy `http://127.0.0.1:3000/api/v1/health/` | HTTP 200 |
| Shutdown normal | PASS; proses server dihentikan setelah dua request |
| Cleanup pada bind failure | PASS; listener port 8011 milik tes sendiri memaksa `PermissionError`, fixture keluar 1 dan tidak meninggalkan listener/DB |
| Production guard dengan environment sintetis (`APP_ENV=production`, `DB_ENGINE=sqlite`) | PASS terbatas; startup ditolak dengan `DB_ENGINE must be 'postgresql' when APP_ENV=production` (exit 1) |
| Port 3000/8011 setelah shutdown | PASS; tidak ada listener yang tersisa |
| PostgreSQL row locking/interleaving | NOT RUN; tidak ada PostgreSQL disposable yang tersedia |
| Redis cache/throttle lintas proses | NOT RUN; tidak ada Redis disposable yang tersedia |

Concurrency test `back-end/apps/assessments/test_concurrency.py` sengaja mensyaratkan PostgreSQL. SQLite mengabaikan `SELECT ... FOR UPDATE`; menjalankannya di SQLite tidak dapat membuktikan locking dan tidak dihitung PASS.

## Yang masih terbuka

- COMP-007 belum stabil, jadi runtime ini hanya smoke pada SHA komposisi parsial.
- Perlu PostgreSQL dan Redis disposable untuk interleaving deterministik, isolasi user, konsistensi mastery/XP, cache/throttle lintas proses, expiry/retry, dan destination guard.
- Perlu probe fail-closed untuk config hosted valid pada runtime bersih.
- Kasus cleanup yang diuji terbatas pada bind failure startup; cleanup pada exception request belum dijalankan.
- Guard production menolak SQLite terverifikasi; konfigurasi valid dengan PostgreSQL/provider nyata dan Redis belum diverifikasi.
- Perlu merekonsiliasi acceptance QA TASK-027/029 dengan bukti yang terikat ke kandidat final.

Tidak ada file database persisten yang dibuat oleh fixture ini. COMP-009 belum PASS dan tidak menutup acceptance PostgreSQL/Redis.

## Perintah dan hasil

```text
python front-end/tests/backend_server.py --catalog        (candidate root; server started)
GET http://127.0.0.1:8011/api/v1/career-tracks/           HTTP 200
GET http://127.0.0.1:8011/api/v1/health/                  HTTP 200
GET http://127.0.0.1:3000/api/v1/career-tracks/           HTTP 200, Backend Engineering
GET http://127.0.0.1:3000/api/v1/health/                  HTTP 200
Ctrl-C                                                       normal shutdown
Port probe 3000, 8011                                         no listener
$portGuard.Start(); python front-end/tests/backend_server.py --catalog
                                                             expected bind failure, exit 1; guard then stopped
$env:APP_ENV='production'; $env:DB_ENGINE='sqlite'; python back-end/manage.py check
                                                             exit 1, expected fail-closed ValueError
```
