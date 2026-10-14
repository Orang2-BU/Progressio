# COMP-002 — Verifikasi keamanan dan dependency

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Verdict: **CHANGES secara keseluruhan; PASS terbatas hanya untuk scope yang disebut per baris**. Self-review oleh assistant yang diberi wewenang mengambil alih review.

## Hasil

| Scope | Kandidat | Bukti | Verdict |
| --- | --- | --- | --- |
| Backend provider AI/proof | `codex/bimo-transport-security`, `1e245a8` | `uvx --from pip-audit pip-audit -r requirements.txt`: tidak ada advisori. `manage.py test`: 198 lulus, 5 skip. `makemigrations --check --dry-run` dan `spectacular --fail-on-warn`: lulus. | PASS |
| Web auth/logout | `codex/completion-integration`, `48cca73` | Tes backend Accounts 23/23 dan suite penuh 200 lulus/5 skip pada SQLite; frontend 73/73, build 13 route, coverage lulus. Logout memakai SimpleJWT blacklist; refresh lama ditolak, kegagalan revoke mempertahankan sesi, request ganda berbagi promise. `makemigrations --check` dan OpenAPI `spectacular --fail-on-warn` pass; audit instalasi 0 advisory. | PASS untuk source/tes; access token lama tetap valid sampai expiry dan runtime demo belum diuji |
| Mobile auth/logout | `task-012-hubungkan-autentikasi-mobile-ke-api-dan-hilangka`, `85e8a43` | `flutter analyze --no-pub`: tanpa isu. `flutter test --no-pub`: 23/23 lulus. Logout mengembalikan `serverRevoked`; kegagalan server tetap membersihkan token lokal dan UI menampilkan bahwa pencabutan sesi server belum berhasil. | PASS untuk source/unit/widget tests |
| QA fixture | `task-029-implementasikan-bukti-regresi-dan-runbook-untuk`, `1c47590` | `python -m unittest qa.test_url_safety qa.test_service_cleanup qa.test_proxy_cleanup qa.test_fixture_isolation -v`: 9/9 lulus. Tes menolak host/userinfo/port yang bukan milik fixture, menyangga environment poisoned, dan mencoba semua cleanup setelah error sintetis. | PASS untuk regresi offline |

## Temuan dan perubahan

- **Sedang — provider HTTPS menerima port nonstandar.** Tes baru gagal sebelum fix untuk `https://ai.example.test:8443`; validator kini hanya menerima port implisit/443. Tes 9 transport lulus. Commit `1e245a8` juga memperbarui README kontrak port.
- **Tinggi — Django 5.1.15 rentan.** `pip-audit` menemukan 9 advisori; constraint diperbarui ke `Django>=5.2.18,<5.3`. Audit ulang: 0 advisori. Upgrade mengekspos incompatibility pada custom test runner (`SimpleTestCase._pre_setup` berubah jadi classmethod); runner kini mempertahankan descriptor/signature dan full suite lulus.
- Transport menolak URL credentialed HTTP, userinfo/fragment dan host di luar allowlist; redirect tidak diikuti sehingga Authorization tidak berpindah origin; exception provider tidak membocorkan refusal body. Tes transport/provider dan full backend suite lulus.
- Mobile tidak mempunyai jalur sukses simulasi pada repository/unit/widget path yang ditinjau. Logout API offline menandai revoke server gagal, bukan sukses.
- Web notice logout tidak dapat dipalsukan dengan `logged_out=1`; tes sumbernya ada pada candidate frontend tersebut.
- **HIGH / TASK-009 — ditutup pada source/tes, belum runtime.** Finding awal terkonfirmasi: `api.js` hanya menghapus state, backend contract tidak memiliki revoke, sementara UI/test source mengklaim konfirmasi server. Commit `48cca73` mengaktifkan `rest_framework_simplejwt.token_blacklist`, menambahkan `POST auth/logout` berbasis `TokenBlacklistView` dengan throttle, dan membuat client menunggu respons sebelum menghapus state. Tes membuktikan refresh yang sama ditolak setelah logout, access JWT yang telah terbit masih berlaku (maksimum 30 menit), kegagalan 503 mempertahankan sesi, dan double-click hanya mengirim satu revoke.
- Tes source-string palsu diganti tes perilaku pada API client dan backend. Aplikasi produksi harus menjalankan migrasi bawaan `token_blacklist` sebelum endpoint dipakai; `manage.py test` menerapkan migrasi pada DB test. Tidak ada migration database deployment yang dijalankan.
- Fixture membuat environment lokal/mock sebelum Django import, mengunci URL Redis/proxy ke loopback+port milik run, dan cleanup berupaya menghapus semua container/proses yang dibuat run.

## Batas verdict

Ini bukan clearance untuk `main` atau satu kandidat demo. Provider backend, fixture, dan endpoint revoke lulus terbatas pada SHA yang disebut; PostgreSQL/Redis runtime, web/Mobile terhadap backend aktif, browser/Sokudo, penerapan migrasi deployment, dan rehearsal belum diuji. Lima test backend yang skip tidak diklaim lulus. Tidak ada approval independen dari Bimo/Adit yang diklaim.
