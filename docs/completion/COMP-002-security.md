# COMP-002 — Verifikasi keamanan dan dependency

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Verdict: **CHANGES secara keseluruhan; PASS terbatas hanya untuk scope yang disebut per baris**. Self-review oleh assistant yang diberi wewenang mengambil alih review.

## Hasil

| Scope | Kandidat | Bukti | Verdict |
| --- | --- | --- | --- |
| Backend provider AI/proof | `codex/bimo-transport-security`, `1e245a8` | `uvx --from pip-audit pip-audit -r requirements.txt`: tidak ada advisori. `manage.py test`: 198 lulus, 5 skip. `makemigrations --check --dry-run` dan `spectacular --fail-on-warn`: lulus. | PASS |
| Web auth/logout | `codex/completion-integration`, `8c46ce1` | Audit instalasi 0 advisory; suite 71/71/build/coverage pass. Review source menemukan `api.js:25-30` hanya membersihkan state/token lokal; tidak ada request revoke, dan `API_CONTRACT.md:36` menyatakan endpoint logout/revoke belum ada. UI diperbaiki agar notice hanya mengklaim logout lokal; tes membuktikan tidak ada request server. | CHANGES — klaim UI dikoreksi; pencabutan token server belum tersedia |
| Mobile auth/logout | `task-012-hubungkan-autentikasi-mobile-ke-api-dan-hilangka`, `85e8a43` | `flutter analyze --no-pub`: tanpa isu. `flutter test --no-pub`: 23/23 lulus. Logout mengembalikan `serverRevoked`; kegagalan server tetap membersihkan token lokal dan UI menampilkan bahwa pencabutan sesi server belum berhasil. | PASS untuk source/unit/widget tests |
| QA fixture | `task-029-implementasikan-bukti-regresi-dan-runbook-untuk`, `1c47590` | `python -m unittest qa.test_url_safety qa.test_service_cleanup qa.test_proxy_cleanup qa.test_fixture_isolation -v`: 9/9 lulus. Tes menolak host/userinfo/port yang bukan milik fixture, menyangga environment poisoned, dan mencoba semua cleanup setelah error sintetis. | PASS untuk regresi offline |

## Temuan dan perubahan

- **Sedang — provider HTTPS menerima port nonstandar.** Tes baru gagal sebelum fix untuk `https://ai.example.test:8443`; validator kini hanya menerima port implisit/443. Tes 9 transport lulus. Commit `1e245a8` juga memperbarui README kontrak port.
- **Tinggi — Django 5.1.15 rentan.** `pip-audit` menemukan 9 advisori; constraint diperbarui ke `Django>=5.2.18,<5.3`. Audit ulang: 0 advisori. Upgrade mengekspos incompatibility pada custom test runner (`SimpleTestCase._pre_setup` berubah jadi classmethod); runner kini mempertahankan descriptor/signature dan full suite lulus.
- Transport menolak URL credentialed HTTP, userinfo/fragment dan host di luar allowlist; redirect tidak diikuti sehingga Authorization tidak berpindah origin; exception provider tidak membocorkan refusal body. Tes transport/provider dan full backend suite lulus.
- Mobile tidak mempunyai jalur sukses simulasi pada repository/unit/widget path yang ditinjau. Logout API offline menandai revoke server gagal, bukan sukses.
- Web notice logout tidak dapat dipalsukan dengan `logged_out=1`; tes sumbernya ada pada candidate frontend tersebut.
- **HIGH / TASK-009 belum selesai — logout web tidak mencabut refresh token di server.** Pada `codex/completion-integration` sebelum fix, `front-end/src/App.jsx:175` dan `Profile.jsx:55` menampilkan keberhasilan sesudah `await logout(...)`, tetapi `front-end/src/api.js:25-30` adalah fungsi sinkron yang hanya menaikkan versi, menghapus token di memori, dan mem-publish state; tidak ada fetch/revoke. `front-end/API_CONTRACT.md:36` mengonfirmasi endpoint belum ada. Reproduksi statis dikonfirmasi tes baru `local logout clears client state without calling a server endpoint`. Commit `8c46ce1` menghapus klaim server sukses dan menampilkan notice `Logout lokal: ... server belum mengonfirmasi pencabutan token.` Ini mitigasi klaim menyesatkan, **bukan** implementasi revoke. Risiko: refresh token yang pernah terekspos tetap dapat valid sampai kedaluwarsa/revoke mekanisme lain.
- Tes lama `logout redirects only after server confirmation...` hanya mencocokkan source string `await logout(...)`; tidak menguji adanya request HTTP. Tes diganti dengan assert lokal-only dan tes tanpa network.
- Fixture membuat environment lokal/mock sebelum Django import, mengunci URL Redis/proxy ke loopback+port milik run, dan cleanup berupaya menghapus semua container/proses yang dibuat run.

## Batas verdict

Ini bukan clearance untuk `main` atau satu kandidat demo. Provider backend dan fixture lulus terbatas pada SHA di atas; **web server-side logout/revocation tetap belum diimplementasikan**, sehingga TASK-009 dan COMP-008 harus tetap terbuka. PostgreSQL/Redis runtime, web/Mobile terhadap backend aktif, browser/Sokudo, dan rehearsal belum diuji; lima test backend yang skip tidak diklaim lulus. Tidak ada approval independen dari Bimo/Adit yang diklaim.
