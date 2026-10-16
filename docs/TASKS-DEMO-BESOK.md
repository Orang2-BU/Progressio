# Tugas lanjutan demo — 16 Oktober 2026

Dokumen ini mencatat pekerjaan yang belum selesai untuk demo. Jangan menandai proyek siap rilis hanya berdasarkan build dan unit test; kandidat UI masih perlu komposisi dan rehearsal end-to-end.

## P0 — Stabilkan kandidat integrasi

- [x] Tetapkan baseline kerja dari `main` pada SHA `989e0a3`: auth/security dan Study telah dipadukan; test frontend 73/73 dan production build 13 route lulus.
- [x] Perbaiki logout pada halaman Profile yang sebelumnya memanggil setter error yang tidak didefinisikan; tambahkan regresi assertion dan validasi dengan suite frontend 73/73 + build.
- [x] Integrasikan slice Dashboard/Profile yang aman: hasil progress/target tetap independen saat error/cancel, username dinormalisasi, dan ringkasan/pengaturan memakai rail responsif; suite 75/75 + build 13 route lulus.
- [x] Integrasikan slice Diagnostic secara selektif dan perbaiki API client yang sebelumnya menormalisasi respons JSON array menjadi `{}`; regression interaksi 5/5, suite frontend 81/81, build 13 route.
- [ ] Rekonsiliasi delta Dashboard/Profile TASK-042, Diagnostic TASK-018, dan Roadmap TASK-019. Hindari cherry-pick kandidat lama secara utuh: beberapa branch safe-composition menghapus file backend, dokumentasi, dan test di luar scope.
- [ ] Setelah tiap komponen dipadukan, jalankan test frontend, build production, dan review diff penuh. Pastikan backend/provider security dan server-confirmed logout tetap utuh.
- [ ] Perbarui `docs/completion/COMP-007-integration-review.md` dan status COMP-007/008/010/011 hanya dengan hasil pada SHA kandidat final.

## P0 — Rehearsal browser end-to-end

- [ ] Mulai dari runtime bersih dengan fixture/backend yang terdokumentasi.
- [ ] Jalankan alur catalog → pilih target → diagnostic → result → roadmap → study/checkpoint/completion → assessment → draft credential → public verification tanpa login.
- [ ] Verifikasi register/login/logout/revoke, refresh replay, kegagalan jaringan/server dan retry; lanjutkan skenario reload, dua tab, refresh paralel/expiry, serta isolasi sesi.
- [ ] Cek viewport mobile/tablet/desktop, keyboard/fokus, loading/empty/error, navigasi sidebar, dan lifecycle Study.
- [ ] Simpan hasil per acceptance (PASS/FAIL/NOT RUN), log/screenshot aman, serta SHA dan konfigurasi runtime di `docs/demo-test-matrix.md`.

## P1 — Mobile dan sumber demo

- [ ] Pastikan Flutter SDK/runtime tersedia; jika tidak, catat blocker dan jangan menyebut Mobile teruji.
- [ ] Uji Mobile register/login/restore/logout, secure storage, offline/401/refresh gagal, dan kegagalan storage.
- [ ] Buka sumber materi yang benar-benar dipakai saat demo pada browser operator. Reachability bukan bukti lisensi; pertahankan `license_verified=false` sampai diverifikasi.

## Kriteria selesai

- Kandidat memiliki satu SHA yang sudah melalui review diff penuh dan test yang relevan.
- Rehearsal fitur utama tercatat tanpa blocker P0; seluruh status mock/draft dan fitur yang tidak tersedia dijelaskan kepada presenter.
- Mobile yang belum bisa diuji tetap dilaporkan sebagai belum terverifikasi, bukan PASS.
