# Tugas lanjutan demo — 16 Oktober 2026

Dokumen ini mencatat pekerjaan yang belum selesai untuk demo. Jangan menandai proyek siap rilis hanya berdasarkan build dan unit test; kandidat UI masih perlu komposisi dan rehearsal end-to-end.

## P0 — Stabilkan kandidat integrasi

- [x] Tetapkan baseline kerja dari `main` pada SHA `989e0a3`: auth/security dan Study telah dipadukan; test frontend 73/73 dan production build 13 route lulus.
- [x] Perbaiki logout pada halaman Profile yang sebelumnya memanggil setter error yang tidak didefinisikan; tambahkan regresi assertion dan validasi dengan suite frontend 73/73 + build.
- [x] Integrasikan slice Dashboard/Profile yang aman: hasil progress/target tetap independen saat error/cancel, username dinormalisasi, dan ringkasan/pengaturan memakai rail responsif; suite 75/75 + build 13 route lulus.
- [x] Integrasikan slice Diagnostic secara selektif dan perbaiki API client yang sebelumnya menormalisasi respons JSON array menjadi `{}`; regression interaksi 5/5, suite frontend 81/81, build 13 route.
- [x] Rekonsiliasi slice aman Dashboard/Profile TASK-042, Diagnostic TASK-018, dan Roadmap TASK-019 secara selektif; branch kandidat lama tidak digabung utuh karena membawa perubahan di luar scope.
- [x] Roadmap menampilkan langkah interaktif, prasyarat, cakupan mastery roadmap, dan empty-state tanpa klaim credential; suite frontend 85/85 + build 13 route lulus.
- [x] Setelah tiap slice dipadukan, jalankan test frontend, build production, dan review diff slice; backend/provider security tidak diubah dan server-confirmed logout tetap diuji.
- [x] Perbarui COMP-007 dan matrix dengan bukti pada SHA `ca39c3a`; clearance integrasi/release tetap CHANGES sampai rehearsal penuh.

## P0 — Rehearsal browser end-to-end

- [x] Mulai runtime bersih: disposable SQLite backend `--catalog` + Next proxy; `/api/v1/ready/`, catalog, dan 9 halaman Next memberi HTTP 200. Ini startup/API smoke, bukan browser interaction.
- [ ] Jalankan alur catalog → pilih target → diagnostic → result → roadmap → study/checkpoint/completion → assessment → draft credential → public verification tanpa login.
- [ ] Verifikasi register/login/logout/revoke, refresh replay, kegagalan jaringan/server dan retry; lanjutkan skenario reload, dua tab, refresh paralel/expiry, serta isolasi sesi.
- [ ] Cek viewport mobile/tablet/desktop, keyboard/fokus, loading/empty/error, navigasi sidebar, dan lifecycle Study.
- [x] Catat hasil PASS/NOT RUN, batas browser, SHA, dan konfigurasi runtime di `docs/demo-test-matrix.md`.

## P1 — Mobile dan sumber demo

- [x] Cek Flutter SDK/runtime; `flutter` tidak tersedia di PATH, dicatat sebagai blocker dan Mobile tidak diklaim teruji.
- [ ] Uji Mobile register/login/restore/logout, secure storage, offline/401/refresh gagal, dan kegagalan storage.
- [ ] Buka sumber materi yang benar-benar dipakai saat demo pada browser operator. Reachability bukan bukti lisensi; pertahankan `license_verified=false` sampai diverifikasi.

## Kriteria selesai

- Kandidat memiliki satu SHA yang sudah melalui review diff penuh dan test yang relevan.
- Rehearsal fitur utama tercatat tanpa blocker P0; seluruh status mock/draft dan fitur yang tidak tersedia dijelaskan kepada presenter.
- Mobile yang belum bisa diuji tetap dilaporkan sebagai belum terverifikasi, bukan PASS.
