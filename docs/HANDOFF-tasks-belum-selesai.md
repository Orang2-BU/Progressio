# Handoff — Task yang belum selesai (turn 6 Okt 2026)

> Yang masih **In Progress dibiarkan jalan** — file ini hanya bekal lanjutan setelah turn ini.
> Dibuat oleh Cecep (orchestrator) setelah turn ini. Bahasa: Indonesia.

## Snapshot status

**Board (Kanban):**

- Done: TASK-001, TASK-002, TASK-003, TASK-004 (sudah merged ke `main` lokal).
- In Progress (belum selesai, biarkan): **TASK-006 (Sugeng), TASK-008 (Sugeng), TASK-014 (Agus)**.
- Backlog (belum mulai): TASK-005, TASK-007, TASK-009, TASK-010, TASK-011, TASK-012, TASK-013.

**Git saat file ini ditulis:**

- `main` lokal: `e693764` (merge TASK-003). Status: `ahead 3` dari `origin/main`, plus untracked `.sokudo/` (jangan di-commit).
- Worktree `.sokudo/worktrees/task-006-...`: bersih di `e693764` — **belum ada perubahan worker**.
- Worktree `.sokudo/worktrees/task-008-...`: branch `task-008-...` di `fe9b3d9` dengan **perubahan belum di-commit** (8 modified + 3 new, lihat di bawah). Base tertinggal 2 merge (TASK-002 `f7634ed`, TASK-003 `b2cc865`).
- Worktree `investigate-task-014-...`: di `e693764` (QA, tidak diharapkan ada perubahan aplikasi).

**Pola kegagalan dominan turn ini (bukan kegagalan kode):**
komentar worker berulang: `codex's composer dropped the start of the prompt — retry the message; if it repeats, restart codex. Nothing was submitted.`
Artinya prompt tidak terkirim ke model sama sekali. Kalau berulang di turn berikut: **restart Codex dulu**, baru dispatch ulang tiket yang sama (jangan buat tiket duplikat).

---

## TASK-008 — Pisahkan konfigurasi lokal dan hosting aman (Sugeng, In Progress)

**Goal:** aplikasi hosted fail-closed, tidak jalan diam-diam dengan default development.

**Progres terakhir yang tercatat:**
- Keputusan Sugeng: production wajib pilih provider AI/blockchain eksplisit; live provider wajib key/endpoint; mock tidak dipilih diam-diam; host list menolak `*` dan wildcard subdomain leading-dot.
- Temuan Sugeng: Compose hosted meneruskan SMTP ke backend+worker; suite backend SQLite 141/141 lulus; config Compose lokal+hosted tervalidasi dengan env sintetis (klaim worker, belum diverifikasi independen).
- Perubahan **ada tapi belum di-commit** di worktree `task-008-...`:
  - Modified: `.github/workflows/backend-tests.yml`, `.github/workflows/web-tests.yml`, `back-end/.env.example`, `back-end/README.md`, `back-end/config/settings.py`, `docker-compose.yml`, `front-end/check_api_contract.py`, `front-end/tests/backend_server.py`
  - New: `back-end/.env.production.example`, `back-end/apps/common/test_settings_profiles.py`, `docker-compose.hosted.yml`

**Blocker:** 5x+ kegagalan composer (prompt tidak terkirim). Pekerjaan terhenti sebelum commit/review.

**Yang tersisa dari acceptance:** startup negatif/positif profile production, `python manage.py check --deploy` dengan config sintetis, `docker compose config --quiet`, suite backend dari direktori `back-end`, diagnostik LSP.

**Langkah lanjut (turn berikut):**
1. Buka worktree `task-008-...` yang SAMA — jangan buat worktree baru, jangan timpa perubahan uncommitted. Baca `git status` + `git diff` dulu.
2. Verifikasi klaim worker: jalankan dari `back-end` (bukan root) suite backend + tes profil baru + `check --deploy` sintetis + `docker compose config --quiet`.
3. Commit hasil di branch task-008, biarkan kartu worker minta review. **Jangan merge manual `task-008-*` ke `main`** — penggabungan hanya via Approve di kartu.
4. Perhatikan base `fe9b3d9` tertinggal dari `main` (`f7634ed`, `b2cc865`). Serahkan keputusan rebase ke worker/pemilik tiket; jangan rebase paksa dari orchestrator.

**Jangan:** deploy, ubah secret pengguna, buka port layanan nyata, ambil implementasi throttle TASK-007.

---

## TASK-006 — E2E perjalanan demo + runbook (Sugeng, In Progress)

**Goal:** buktikan alur UI akun sintetis → verifikasi draft di runtime lokal bersih + runbook operator.

**Progres terakhir:** 6 komentar worker, **semuanya kegagalan composer** — tidak ada satu pun eksekusi/flow yang dihasilkan. Worktree bersih di `e693764`. Flow `e2e/progressio-demo.yaml` belum ada, `docs/demo-test-matrix.md` dan runbook belum diperbarui.

**Blocker:** murni infra composer (prompt tidak terkirim). Dependensi logis sudah unblocked: TASK-001, TASK-003, TASK-004 Done.

**Langkah lanjut (turn berikut):**
1. Kalau composer masih jatuh: restart Codex dulu, baru dispatch ulang TASK-006 (satu tiket, jangan duplikat).
2. Worker mulai dari `e2e_list_flows`, runtime mock `front-end/tests/backend_server.py --catalog` + Next.js sesuai `front-end/README.md`, akun disposable.
3. Simpan flow di `e2e/progressio-demo.yaml` (dialek: header `url` wajib + `---` + steps `launchApp/openLink/tapOn/inputText/assertVisible/takeScreenshot/back`), `e2e_validate` sebelum simpan, `e2e_run` untuk bukti. Maks 3 upaya heal per flow.
4. Credential tetap draft/invalid, tidak di-anchor; screenshot tanpa token/password/data nyata.

---

## TASK-014 — QA independen TASK-002 (Agus, In Progress)

**Goal:** verifikasi independen hasil konkurensi TASK-002 (Manok). Deliverable **laporan QA, bukan perubahan aplikasi**.

**Progres terakhir:**
- Agus mencatat: diff target 2 service + 1 file tes; sinkronisasi tes pakai Barrier (menyamakan awal thread, belum tentu mengendalikan interleaving baca/tulis) — perlu pemeriksaan lanjutan.
- Blocker lingkungan QA: `shell ditolak kebijakan lingkungan` (termasuk `git worktree list`, `python --version`) → **belum ada hasil tes independen**; klaim 141/141 SQLite/PostgreSQL masih milik Manok.
- Konteks penting: TASK-002 (`f7634ed`) sudah merged ke `main` lokal; QA harus menyebut SHA yang diuji dan memberi rekomendasi tindak lanjut, bukan minta Approve ulang atas yang sudah merged.

**Langkah lanjut (turn berikut):**
1. Awali dengan cek kemampuan shell read-only singkat. Kalau masih ditolak: catat konkret + hentikan (jangan retry tanpa batas), laporkan butuh restart/perbaikan izin Codex.
2. Kalau shell bisa: uji dari snapshot terisolasi di SHA target, suite dari direktori `back-end`: `python manage.py test apps.assessments apps.learning` di SQLite + PostgreSQL disposable; buktikan tes konkurensi benar-benar jalan (tidak skipped); cek mastery tidak turun, competency konsisten, XP tidak hilang/berlipat, diagnostic tanpa XP, isolasi antar pengguna.
3. Bedakan di laporan: hasil eksekusi sendiri vs inspeksi vs klaim Manok. Jangan ubah worktree Manok/main, jangan merge/rebase/cherry-pick/push/Approve.

---

## Backlog — belum mulai (untuk setelah 3 di atas)

- **TASK-005 (high):** samakan validasi/snapshot/reward task Celery AI dengan jalur HTTP. Baru dikerjakan setelah TASK-002 stabil.
- **TASK-007 (high):** throttle auth + endpoint mahal. Gate sebelum akses publik; butuh setelah TASK-008.
- **TASK-009/010/011/012/013 (low = tahap lanjutan):** sesi cookie HttpOnly; antrean AI; recovery proof timeout; auth Mobile nyata; paket review kurikulum. TASK-011 wajib sebelum credential final diandalkan; TASK-013 menghasilkan bahan review, bukan status `reviewed` otomatis.

**Urutan saran:** selesaikan 008 → 006 → 014, lalu 005 → 007, baru tahap low sesuai fokus produk.

---

## Aturan yang tetap berlaku turn berikut

1. Jangan merge manual branch `task-*` ke `main` — hanya via Approve kartu.
2. Perintah Django selalu dari direktori `back-end` (perintah dari root hanya menemukan 18 tes vs 129 tes).
3. Jangan commit `.sokudo/`, venv, secret, atau data pengguna.
4. Jangan deploy / aktifkan provider berbayar / terbitkan credential final.
5. File ini selesai dibaca kalau turn berikut bisa dispatch ulang 006/008/014 tanpa tanya ulang konteks.
