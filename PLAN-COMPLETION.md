# Plan penyelesaian Progressio

Tanggal: 14 Oktober 2026 (Asia/Jakarta). Status: **PLANNED**.

Daftar pekerjaan operasional ada di [TASKS-COMPLETION.md](TASKS-COMPLETION.md). Dokumen ini menggantikan `HANDOFF.md` di root untuk pekerjaan selanjutnya. [TASKS.md](TASKS.md) dipertahankan sebagai snapshot historis 13 Oktober; status lamanya perlu direkonsiliasi, bukan dipakai sebagai bukti kondisi terbaru. Task COMP di dokumen baru adalah paket eksekusi lokal yang dipetakan ke tiket asal, bukan tiket Kanban baru.

## Tujuan dan batas pekerjaan

Selesaikan gap implementasi, tes komponen, coverage, autentikasi runtime, fixture QA, review, dan rehearsal demo. Setiap task mempunyai hasil yang dapat diperiksa, commit sesuai scope, dan laporan PASS/FAIL/NOT RUN. Pembuatan dokumen ini tidak menjalankan tes baru, memperbaiki produk, menutup kartu, atau menggabungkan kandidat ke `main`.

Pekerjaan dilakukan pada kandidat terisolasi yang dipin ke SHA. Gunakan akun sintetis, database sementara, mock provider, dan port milik run. Integrasi ke `main`, push, deploy, serta penerbitan credential final bukan hasil otomatis dari plan ini. Pertahankan source pengguna yang belum di-commit.

## Titik awal dan bukti yang sudah tersedia

SHA di tabel berikut diperiksa kembali saat menyusun plan. Hasil tes berasal dari eksekusi sebelumnya dalam percakapan, bukan tes baru pada saat penulisan dokumen.

| Kandidat | Branch / SHA | Bukti dan batasnya |
| --- | --- | --- |
| Main | `main` / `ded12712636f01185c7c1ef49ff84b74796b528d` | TASK-021 sudah merged. Kandidat berikut berada pada branch terpisah. |
| Web session dan auth backend | `codex/task-009-current-candidate` / `517979d57c2bda7bcfb4020f3b076975797fb39a` | Accounts 24/24 lulus di SQLite. Frontend 55/55, build Next.js, dan probe 32 request tercatat pada kandidat sebelumnya dalam rangkaian ini; cocokkan SHA/source masing-masing sebelum menggunakannya untuk penutupan. |
| Mobile auth | `task-012-hubungkan-autentikasi-mobile-ke-api-dan-hilangka` / `85e8a43f2e19d68c19df449a8a05b7bf9935aa54` | Analyze bersih dan 23/23 tes lulus. Debug APK pernah berhasil dibuat; uji Mobile terhadap backend aktif belum dilakukan. |
| Fixture QA | `task-029-implementasikan-bukti-regresi-dan-runbook-untuk` / `1c4759077f493a78efeb963d71cd4d75574b1014` | 7/7 tes isolasi environment, URL, dan cleanup lulus. Runtime penuh, PostgreSQL, Redis lintas proses, serta E2E belum terbukti. |
| Frontend Study | `task-047-safe-candidate` / `36904a35c7ffcac40472f403bbfb0f57d720d104` | 52/52 tes dan build Next.js lulus. Belum membuktikan lifecycle interaktif dan coverage kode baru. |

Worktree kandidat berada di `.sokudo/worktrees/` dengan nama yang sesuai branch/task di atas; inventaris Git tetap wajib sebelum eksekusi. Kandidat diagnostic/roadmap dan pemulihan dashboard/QA juga sudah mempunyai branch; pilih delta yang diperlukan setelah membandingkan provenance, jangan menerapkan ulang patch lama.

Pengukuran native V8 pada kandidat Study melaporkan line coverage `Study.jsx` 7,45%, `Dashboard.jsx` 45,24%, `Profile.jsx` 80,20%, dan seluruh file 56,06%. Angka ini indikator gap tes, bukan bukti coverage baris baru. Loader JSX menggunakan transform Babel; validasi pemetaan sourcemap dan perhitungan changed-line coverage sebelum memakai angka untuk gate. Script `npm run coverage` belum tersedia pada kandidat tersebut.

PostgreSQL lokal `localhost:5432` tidak tersedia pada percobaan sebelumnya. SQLite digunakan untuk tes accounts; hasilnya tidak membuktikan row locking PostgreSQL. Flutter tersedia di `D:\flutter`, meskipun belum ada di PATH. Runner Sokudo E2E tidak tersedia pada pemeriksaan tool sesi sebelumnya. Audit dependency Python belum lengkap karena `pip-audit` belum tersedia.

## Urutan dan dependency

| Urutan | Paket | Tujuan | Dependency |
| --- | --- | --- | --- |
| 1 | COMP-001 | Pin kandidat, manifest, dan cek alat/runtime | — |
| 2 | COMP-002 | Tutup temuan keamanan transport, auth, dan fixture | COMP-001 |
| 3 | COMP-003 | Siapkan tes komponen dan coverage source yang benar | COMP-001 |
| 4 | COMP-004 | Buktikan/perbaiki lifecycle Study | COMP-003 |
| 5 | COMP-005 | Tutup gap dashboard/profil | COMP-003 |
| 6 | COMP-006 | Tutup diagnostic/roadmap | COMP-003 |
| 7 | COMP-007 | Review full diff dan pin kandidat integrasi | COMP-002, COMP-004, COMP-005, COMP-006 |
| 8 | COMP-008 | Uji auth web dan Mobile terhadap backend disposable | COMP-007 |
| 9 | COMP-009 | Jalankan fixture, PostgreSQL/Redis, dan QA backend | COMP-007 |
| 10 | COMP-010 | Jalankan matriks browser pada kandidat integrasi | COMP-008, COMP-009, runner tersedia |
| 11 | COMP-011 | Verifikasi sumber, rehearsal, dan laporan penutupan | COMP-010; pemeriksaan URL bisa disiapkan lebih awal |

Kerjakan sesuai urutan. Pemeriksaan ketersediaan runner/PostgreSQL/Redis dilakukan sejak COMP-001 supaya masalah lingkungan ditemukan sebelum tahap terakhir. Ketika sebuah dependency eksternal terhambat, lanjutkan task lain yang dependency-nya sudah terpenuhi dan catat penyebab konkret.

## Strategi implementasi dan verifikasi

### Tes komponen dan coverage

Tambahkan lingkungan DOM untuk tes komponen bila dependency sekarang belum memadai, misalnya JSDOM dan React Testing Library sebagai dev dependency pada branch task. Pertahankan runner Node bila memungkinkan. Tes harus menjalankan React asli, effect, interaksi pengguna, dan respons async; SSR markup tetap menjadi tes terpisah. Mock dilakukan pada batas jaringan/data dan gunakan provider Next yang sesuai, tanpa mengganti hook React untuk memaksa state.

Gunakan network fixture/deferred response untuk membuktikan race, retry, dan pembatalan. Untuk defect, reproduksi RED sebelum fix lalu GREEN sesudahnya; fitur yang sudah benar cukup diberi regresi bermakna tanpa sengaja merusak source. Ukur coverage source dengan sourcemap yang benar, laporkan file-level serta changed-line coverage dari base yang dipin. Target tiket: minimal 80% baris kode baru, ditambah kasus perilaku wajib; jangan mengecualikan kode produk hanya untuk meloloskan angka.

### Keamanan dan runtime

Rekonsiliasi tujuh temuan audit lama terhadap SHA baru: redirect AI yang membawa Bearer, AI key melalui HTTP, transport proof serupa, body provider di exception, konfigurasi provider, sukses Mobile simulasi, dan notice logout dari query. Tambahkan pemeriksaan false logout serta isolasi environment/guard URL/cleanup fixture. Audit dependency Node/Python dan simpan hasil aktual, termasuk paket atau alat yang gagal diperiksa.

Setelah source kandidat dan fixture terkait direview, gunakan runtime disposable dengan konfigurasi eksplisit: `APP_ENV=local`, SQLite sementara untuk auth, provider mock, tanpa mewarisi Redis/Celery/email/key pengguna. PostgreSQL dan Redis dibuat sebagai resource terpisah milik run untuk acceptance khusus keduanya. Baca launcher sebelum menjalankannya; cleanup mencoba seluruh resource milik run dan melaporkan kegagalan.

### Browser, review, dan pelaporan

Runner browser yang direncanakan adalah Sokudo sesuai flow proyek. Temukan tool, validasi flow, lalu jalankan pada runtime/SHA yang dicatat. Ketersediaan runner harus dibuktikan; YAML valid, HTTP 200, tes komponen, dan build tidak menggantikan hasil browser. Jika tool tidak tersedia, task browser tetap BLOCKED dengan pemeriksaan terakhir dan tindakan pemulihan yang diperlukan. Kegagalan alat tidak menghentikan pekerjaan komponen atau runtime yang independen.

Owner telah mendelegasikan pekerjaan review kode/keamanan yang sebelumnya ditangani Adit/Bimo kepada assistant dalam percakapan ini. Catat pelaksana dan metode review sebenarnya; jangan menulis approval atas nama orang lain atau menyebut self-review sebagai review independen. Verdict lama dinilai terhadap source terbaru, bukan dijadikan larangan tanpa evaluasi ulang. Keputusan merge/kartu dan hasil QA tetap dicatat terpisah dari verdict teknis.

## Semantik produk yang wajib dijaga

- Identitas, XP, completion, dan hasil assessment berasal dari kontrak server. Streak, level, lencana, atau heatmap yang belum tersedia tidak dibuat dari angka contoh desain.
- Checkpoint memberi feedback sementara, tidak autosave dan tidak memberi XP. Completion lesson tidak berarti lulus assessment; repeat completion tidak menghasilkan reward ganda.
- Diagnostic tidak memberi XP. Belum tahu dikirim sebagai jawaban string kosong, berbeda dari soal yang belum dijawab. Hasil attempt terbaru tidak boleh menurunkan mastery tersimpan.
- Roadmap mengikuti urutan/status server. Ambang roadmap/mastery bukan ambang lulus assessment. Membuka Study tidak otomatis membuktikan Diagnostic/Roadmap selesai.
- Credential demo tetap draft dan invalid/unverified/unanchored. Pertahankan TASK-021; jangan mengimplementasikannya ulang.
- Sidebar aktif hanya pada Ringkasan, Pilih target, Credential, dan Profil; public verification tanpa sidebar. Fitur profil yang endpoint-nya belum ada tetap unavailable. OTP/reset/Google Mobile juga unavailable sampai kontraknya ada.
- Materi ditautkan ke penerbit. Reachability URL dan lisensi umum tidak membuktikan hak menyalin konten; pertahankan attribution dan status lisensi yang belum diverifikasi.

## Definition of done dan commit

Setiap task selesai ketika acceptance terpenuhi pada source terpin dan mempunyai bukti sesuai jenisnya. Simpan base/final SHA, branch/worktree, daftar file, command/cwd, exit code, pass/fail/skip, coverage beserta metode, dan artefak yang relevan. Catat diagnostik editor/LSP bila tersedia; ketidaktersediaannya dilaporkan terpisah.

Commit tiap perubahan source/test/docs yang sudah diverifikasi dengan scope kecil. Periksa staged diff dan jangan sertakan secret, `.sokudo/`, build output, atau data runtime. Tes yang sekadar dijalankan ulang tanpa perubahan tidak membutuhkan commit kosong. Laporan investigasi/review dapat di-commit sebagai dokumentasi tanpa memasukkan fix produk yang belum diuji. Ulangi tes setelah source berubah atau muncul kegagalan yang relevan.

Produk siap demo ketika satu kandidat integrasi lulus tes terkait, uji auth runtime, acceptance PostgreSQL/Redis yang masih diwajibkan, matriks browser, pemeriksaan sumber, dan rehearsal sampai public draft verification. Task yang belum dieksekusi tetap terbuka. Status kartu resmi diperbarui melalui board; dokumen lokal ini tidak mengubah status board dengan sendirinya.

## Referensi yang tetap dipertahankan

- [Kontrak API](front-end/API_CONTRACT.md), [spec backend](progressio-backend-spec.md).
- [Defect false logout](docs/HANDOFF-TASK-009-false-logout-backend.md), [QA backend](docs/HANDOFF-JESSICA-backend-QA.md), dan [QA fondasi](docs/QA-TASK-033-frontend-foundation.md) sebagai bukti historis, dengan SHA/batas lama direkonsiliasi.
- [Matriks demo](docs/demo-test-matrix.md), [runbook](docs/demo-runbook.md), [review sumber](docs/source-review.md).
- [Plan demo lama](plans/README.md) dan [instruksi Mobile](Mobile/docs/AGENTS.md). Plan 001 tercatat DONE; Plan 002–005 masih memerlukan bukti browser/sumber/rehearsal, walaupun branch implementasinya sudah ada.

Penghapusan yang diminta hanya `HANDOFF.md` di root. Dokumen pendukung bernama HANDOFF di `docs/` tetap menjadi referensi defect dan QA; informasi operasional penting root telah dipindahkan ke plan ini.
