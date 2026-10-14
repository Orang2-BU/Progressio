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
| Shutdown normal | PASS; proses server dihentikan setelah dua request |
| Cleanup saat startup/request failure | NOT RUN |
| Next proxy terhadap fixture 8011 | NOT RUN pada smoke ini |
| PostgreSQL row locking/interleaving | NOT RUN; tidak ada PostgreSQL disposable yang tersedia |
| Redis cache/throttle lintas proses | NOT RUN; tidak ada Redis disposable yang tersedia |

Concurrency test `back-end/apps/assessments/test_concurrency.py` sengaja mensyaratkan PostgreSQL. SQLite mengabaikan `SELECT ... FOR UPDATE`; menjalankannya di SQLite tidak dapat membuktikan locking dan tidak dihitung PASS.

## Yang masih terbuka

- COMP-007 belum stabil, jadi runtime ini hanya smoke pada SHA komposisi parsial.
- Perlu PostgreSQL dan Redis disposable untuk interleaving deterministik, isolasi user, konsistensi mastery/XP, cache/throttle lintas proses, expiry/retry, dan destination guard.
- Perlu probe fail-closed untuk config local/hosted pada runtime bersih, serta Next proxy/startup-failure cleanup.
- Perlu merekonsiliasi acceptance QA TASK-027/029 dengan bukti yang terikat ke kandidat final.

Tidak ada file database persisten yang dibuat oleh fixture ini. COMP-009 belum PASS dan tidak menutup acceptance PostgreSQL/Redis.

## Perintah dan hasil

```text
python front-end/tests/backend_server.py --catalog        (candidate root; server started)
GET http://127.0.0.1:8011/api/v1/career-tracks/           HTTP 200
GET http://127.0.0.1:8011/api/v1/health/                  HTTP 200
Ctrl-C                                                       normal shutdown
```
