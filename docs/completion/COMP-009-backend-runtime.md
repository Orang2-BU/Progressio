# COMP-009 — Fixture dan QA backend runtime

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Status: **PASS terbatas — fixture/proxy, PostgreSQL concurrency, Redis lintas proses, dan fail-closed lulus pada backend slice kandidat; bukan deployment/release clearance**. Run dijalankan assistant, bukan QA independen.

## Runtime yang dipin

- Candidate branch/worktree: `codex/completion-integration`, `../progressio-completion-integration`.
- Source SHA: `ff542e71d35c9ebbdedaaad5647d36c787928648`. Backend files are unchanged from earlier smoke SHA `48cca73`.
- PostgreSQL 16 and Redis 7 on Ubuntu WSL, local-only ports 5432/6379; dedicated DB/user and Redis DB 14 namespace. Synthetic auth values were not saved in the repository.
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
| `apps.assessments.test_concurrency` SQLite in-memory (baseline) | 2 sequential regression PASS; 5 PostgreSQL-only cases SKIPPED, not counted as PASS |
| PostgreSQL 16 disposable, `apps.assessments.test_concurrency` | PASS 7/7; test DB dibuat dan dihapus runner |
| Seluruh suite Django PostgreSQL | PASS 200/200, no skips, exit 0; semua 12 app labels disebut eksplisit. Tanpa labels Django hanya menemukan 18 test—jangan gunakan command ringkas itu untuk klaim full suite. |
| Redis 7 shared throttle lintas proses (8021 → 8022) | PASS: request pertama 401, proses kedua 429; kedua proses memakai Redis DB 14 + namespace khusus |
| Redis expiry/retry, rate 1/sec | PASS: 400 → 429 antarproses → 400 setelah 1,3 detik; tidak ada user akun yang dibuat |
| Health check API dengan PG+Redis aktif | HTTP 200 |
| Hosted settings sintetis valid dengan PostgreSQL+Redis | PASS import; `DEBUG=False`, database PostgreSQL, throttle cache `RedisCache` |
| Hosted settings tanpa shared Redis | PASS fail-closed, exit 1 dengan pesan `DEBUG=False requires a shared Redis throttle cache` |
| Port 3000/8011 setelah shutdown | PASS; tidak ada listener yang tersisa |
| PostgreSQL row locking/interleaving | PASS; suite penuh dan concurrency terarah dijalankan |
| Redis cache/throttle lintas proses | PASS untuk budget 429, expiry, dan retry sintetis |

Concurrency test `back-end/apps/assessments/test_concurrency.py` dijalankan benar-benar di PostgreSQL, sehingga `SELECT ... FOR UPDATE` dan barrier antar-koneksi terbukti. Hasil SQLite sebelumnya hanya regresi sequential; lima skip-nya bukan PASS.

## Yang masih terbuka

- Kandidat integrasi fitur masih CHANGES (COMP-007), tetapi backend runtime source yang diuji sama pada SHA `ff542e7`.
- PostgreSQL 16/Redis 7 dipasang pada Ubuntu WSL untuk run ini. Paket tetap terpasang; kedua service sudah disabled dan inactive. Tidak ada service/container pengguna yang dihentikan.
- Dedicated role/database `progressio_comp009_20261014` dihapus setelah test; Redis namespace khusus tidak memiliki key sisa. Server uji 8021/8022 dihentikan.
- Kasus cleanup yang diuji terbatas pada bind failure startup; cleanup pada exception request belum dijalankan.
- Full UI rehearsal, Mobile backend, deployment/provider credentials, dan approval release tetap terbuka pada COMP-008/010/011.

Fixture SQLite tetap memory-only; database PostgreSQL dedicated dibuang. COMP-009 PASS terbatas untuk backend QA/runtime lokal, bukan klaim hosting production atau full demo release.

## Pemetaan acceptance TASK-027/029

| Acceptance lama | Bukti sekarang | Status |
|---|---|---|
| TASK-027 concurrency progres, isolasi, XP/mastery | `test_concurrency` 7/7 dan Django suite 200/200 di PostgreSQL, SHA `ff542e7` | PASS |
| TASK-027 throttle 429, shared cache lintas proses, expiry/retry | Dua proses Django + Redis DB 14 namespace terpisah; HTTP 401/429/400 setelah expiry | PASS terbatas pada throttle login probe |
| TASK-027 destination/transport guard | `apps.common.test_http_transport` termasuk suite 200/200 | PASS tests; bukan probe provider produksi |
| TASK-029 fixture config/port, startup/proxy/shutdown, bind-failure cleanup | SQLite fixture 8011 + Next 3000; API HTTP 200; port collision exit 1 tanpa listener/DB sisa | PASS fixture smoke |
| TASK-029 env sanitizer/cleanup resource generik | Historical evidence `COMP-002-security.md`, QA SHA `1c47590`, unittest 9/9; folder QA tidak ada pada kandidat `ff542e7` | PASS historis saja; tidak diklaim rerun pada kandidat |

## Perintah dan hasil

```text
python front-end/tests/backend_server.py --catalog        (candidate root; server started)
GET http://127.0.0.1:8011/api/v1/career-tracks/           HTTP 200
GET http://127.0.0.1:8011/api/v1/health/                  HTTP 200
GET http://127.0.0.1:3000/api/v1/career-tracks/           HTTP 200, Backend Engineering
GET http://127.0.0.1:3000/api/v1/health/                  HTTP 200
Ctrl-C                                                       normal shutdown
Port probe 3000, 8011                                         no listener
$env:APP_ENV='local'; $env:DB_ENGINE='sqlite'; python back-end/manage.py test apps.assessments.test_concurrency -v 2
                                                             2 passed, 5 skipped (PostgreSQL-only), exit 0
$portGuard.Start(); python front-end/tests/backend_server.py --catalog
                                                             expected bind failure, exit 1; guard then stopped
$env:APP_ENV='production'; $env:DB_ENGINE='sqlite'; python back-end/manage.py check
                                                             exit 1, expected fail-closed ValueError
$env:APP_ENV='local'; $env:DB_ENGINE='postgresql'; python back-end/manage.py test apps.assessments.test_concurrency -v 2
                                                             PostgreSQL 7/7, exit 0
python back-end/manage.py test apps.common apps.accounts apps.curriculum apps.careers apps.competencies apps.skills apps.learning apps.assessments apps.credentials apps.verification apps.ai apps.blockchain -v 1
                                                             PostgreSQL 200/200, 0 skips, exit 0
POST login 8021 -> 401; POST same key 8022 -> 429; wait 1.3 sec; retry 8022 -> 400
Hosted settings: synthetic PostgreSQL+Redis import accepted; no Redis -> ImproperlyConfigured, exit 1
Cleanup: stop 8021/8022; drop dedicated database and role; stop/disable PG+Redis services
```
