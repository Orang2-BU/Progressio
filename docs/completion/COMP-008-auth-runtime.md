# COMP-008 — Auth web dan Mobile pada backend disposable

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Status: **IN PROGRESS — web browser auth/revoke PASS terbatas; Mobile belum diuji**. Run dijalankan assistant; bukan QA independen.

## Runtime yang dipin

- Candidate branch: `codex/completion-integration`, source SHA `48cca732318735dcf24a95580b8443415f26b6f9`.
- Django: `APP_ENV=local`, `DB_ENGINE=sqlite`, `AI_PROVIDER=mock`, `BLOCKCHAIN_PROVIDER=mock`, port `127.0.0.1:8000`.
- Next dev server: port `127.0.0.1:3000`; request melalui rewrite frontend `/api/v1/...` ke Django.
- User: akun sintetis `comp008demo`; bukan akun atau credential pengguna.
- `manage.py migrate --noinput` sukses, termasuk migrasi bawaan `token_blacklist` 0001–0013. Setelah run, kedua server dihentikan dan file SQLite tepat `back-end/db.sqlite3` di worktree kandidat dihapus. Tidak ada database pengguna yang disentuh.

## Hasil aktual

| Flow | Hasil |
| --- | --- |
| Register melalui Next proxy | 201 |
| Login username/password | 200; access + refresh tersedia di memori browser |
| `GET auth/me` dengan access | 200 |
| `POST auth/logout` dengan refresh | 200 |
| Refresh memakai refresh yang baru dicabut | 401 |
| Access token yang telah terbit sesudah logout | Masih mendapat 200 pada `auth/me`; TTL access 30 menit. Token client dihapus, namun JWT stateless yang tersalin tidak langsung dicabut. |

Verifikasi pendukung pada source SHA ini: backend `apps.accounts` 23/23; suite Django penuh 200 passed, 5 skipped; frontend `npm test` 73/73; `npm run build` berhasil (13 routes); `npm run coverage` berhasil (69.30% overall line, `App.jsx` 80.31%, `Profile.jsx` 76.41%); `makemigrations --check --dry-run` tanpa perubahan model; `spectacular --fail-on-warn` lulus.

## Yang belum dilakukan / batas

- Ini request smoke HTTP via Next proxy, bukan browser automation atau full UI journey. Sokudo tool tidak tersedia pada sesi; status historical Sokudo dicatat di COMP-006.
- Tidak ada `flutter` executable di PATH sesi; Mobile nyata (register/login/restore/secure storage/logout) belum dijalankan. Report unit/widget sebelumnya untuk kandidat terpisah bukan pengganti integration pada SHA ini.
- Web memakai Bearer token in-memory, bukan cookie HttpOnly. Tidak ada cookie/CSRF contract yang diuji; reload/tab baru memerlukan login kembali sesuai `API_CONTRACT.md`.
- 503/offline, timeout, request paralel lintas tab, origin/CSRF, expired refresh runtime, deployment PostgreSQL/Redis, dan SSR isolation masih menunggu COMP-010/009. Frontend unit tests meng-cover revoke failure dan double-click, tetapi bukan kegagalan runtime sebenarnya.
- Deployment harus menerapkan migrasi `token_blacklist` sebelum endpoint logout digunakan. Migrasi deployment dan production database tidak dijalankan.

## Follow-up browser regression pada kandidat `ff542e7`

Untuk menutup gap bahwa API smoke sebelumnya tidak mengklik tombol UI, dijalankan Microsoft Edge headless melalui Playwright 1.64.0 dengan backend `backend_server.py --catalog` (SQLite in-memory di 8011) dan Next proxy di 3000. Akun, email, dan password seluruhnya sintetis dan tidak dicatat.

| Browser flow | Hasil |
| --- | --- |
| Register melalui UI → login → dashboard | PASS; API register 201, login 200, `/me` 200 |
| Dashboard viewport 375/768/1440 | PASS terbatas; `document.scrollWidth` sama dengan lebar viewport pada semua ukuran |
| Logout sukses | PASS; endpoint 200, reuse refresh yang dicabut mendapat 401 |
| Logout 503 sintetis | PASS; error alert tampil, pengguna tetap di dashboard dan sesi tetap aktif; refresh masih 200 |
| Retry setelah 503 | PASS; retry ke backend nyata mendapat 200 dan navigasi kembali ke login |
| Browser page errors | 0 |

Critical defect ditemukan oleh smoke ini: `App.jsx` pada SHA `48cca73` memanggil setter logout yang tidak didefinisikan, sehingga klik Keluar crash sebelum request. Perbaikan dan regresi ada di `ff542e7`. Build/test frontend kemudian lulus.

## Keputusan

COMP-008 belum PASS. Web auth/revoke path kini dibuktikan melalui UI browser pada SQLite lokal. Uji Mobile nyata belum dapat dijalankan karena Flutter tidak ditemukan; timeout/offline nyata, reload, multi-tab/race, expiry, CSRF/origin, database deployment, dan skenario lain tetap terbuka. Ini bukan full COMP-010 browser QA atau clearance rilis.
