# COMP-002 — Verifikasi keamanan dan dependency

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Verdict: PASS terbatas per kandidat/SHA, self-review oleh assistant yang diberi wewenang untuk mengambil alih review.

## Hasil

| Scope | Kandidat | Bukti | Verdict |
| --- | --- | --- | --- |
| Backend provider AI/proof | `codex/bimo-transport-security`, `1e245a8` | `uvx --from pip-audit pip-audit -r requirements.txt`: tidak ada advisori. `manage.py test`: 198 lulus, 5 skip. `makemigrations --check --dry-run` dan `spectacular --fail-on-warn`: lulus. | PASS |
| Web auth/logout | `task-047-fix-revisi-ruang-belajar-task-020-dan-lengkapi-b`, `cd21348` | `npm audit`: 0 kerentanan dari 147 paket. Regresi `forged logout query parameter cannot show a success notice` ikut suite 59/59. Logout sukses bergantung pada event API, bukan query URL. | PASS untuk source/regresi |
| Mobile auth/logout | `task-012-hubungkan-autentikasi-mobile-ke-api-dan-hilangka`, `85e8a43` | `flutter analyze --no-pub`: tanpa isu. `flutter test --no-pub`: 23/23 lulus. Logout mengembalikan `serverRevoked`; kegagalan server tetap membersihkan token lokal dan UI menampilkan bahwa pencabutan sesi server belum berhasil. | PASS untuk source/unit/widget tests |
| QA fixture | `task-029-implementasikan-bukti-regresi-dan-runbook-untuk`, `1c47590` | `python -m unittest qa.test_url_safety qa.test_service_cleanup qa.test_proxy_cleanup qa.test_fixture_isolation -v`: 9/9 lulus. Tes menolak host/userinfo/port yang bukan milik fixture, menyangga environment poisoned, dan mencoba semua cleanup setelah error sintetis. | PASS untuk regresi offline |

## Temuan dan perubahan

- **Sedang — provider HTTPS menerima port nonstandar.** Tes baru gagal sebelum fix untuk `https://ai.example.test:8443`; validator kini hanya menerima port implisit/443. Tes 9 transport lulus. Commit `1e245a8` juga memperbarui README kontrak port.
- **Tinggi — Django 5.1.15 rentan.** `pip-audit` menemukan 9 advisori; constraint diperbarui ke `Django>=5.2.18,<5.3`. Audit ulang: 0 advisori. Upgrade mengekspos incompatibility pada custom test runner (`SimpleTestCase._pre_setup` berubah jadi classmethod); runner kini mempertahankan descriptor/signature dan full suite lulus.
- Transport menolak URL credentialed HTTP, userinfo/fragment dan host di luar allowlist; redirect tidak diikuti sehingga Authorization tidak berpindah origin; exception provider tidak membocorkan refusal body. Tes transport/provider dan full backend suite lulus.
- Mobile tidak mempunyai jalur sukses simulasi pada repository/unit/widget path yang ditinjau. Logout API offline menandai revoke server gagal, bukan sukses.
- Web notice logout tidak dapat dipalsukan dengan `logged_out=1`; tes sumbernya ada pada candidate frontend tersebut.
- Fixture membuat environment lokal/mock sebelum Django import, mengunci URL Redis/proxy ke loopback+port milik run, dan cleanup berupaya menghapus semua container/proses yang dibuat run.

## Batas verdict

Ini bukan clearance untuk `main` atau satu kandidat integrasi: keempat source berada pada branch/base yang berbeda. PostgreSQL/Redis runtime, web/Mobile terhadap backend aktif, browser/Sokudo, dan rehearsal belum diuji; task COMP-007/008/009/010 tetap mengatur scope itu. Lima test backend yang skip tidak diklaim lulus. Tidak ada approval independen dari Bimo/Adit yang diklaim.
