# Handoff QA Backend — Jessica ke teman backend (dari Bimo, gate TASK-032)

**Tanggal:** 8 Oktober 2026
**Penulis:** Bimo (Security Engineer, gate TASK-032)
**Sumber:** TASK-014, TASK-025, TASK-027, TASK-029 + Adit TASK-031 BLOCKED + Bimo TASK-030 BLOCKED HIGH
**Status:** Backend QA tetap STOP/BLOCKED — diserahkan ke teman backend manusia. Bukan clearance, bukan Approve.
**Frontend QA non-backend:** tetap boleh lanjut Jessica di baseline (lihat §5).

Dokumen ini melengkapi `docs/HANDOFF-TASK-009-false-logout-backend.md` (false logout).
Teman backend meneruskan SEMUA item §2–§4. Jangan merge kandidat lama.

---

## 1. Pin SHA / baseline yang dipakai putusan ini

| Item | Nilai |
|---|---|
| Baseline frontend/curriculum yang boleh jalan | `6720ba1` — `front-end/src/api.js:25-30` logout lokal-only; `front-end/API_CONTRACT.md:30-48` belum ada logout/revoke; token memory-only, reload minta login ulang |
| Kandidat TASK-009 (Sugeng, STOP) | `7ffcdb5`, base `d83667c` — HIGH false logout masih terbuka, tanpa SHA revisi |
| Kandidat QA TASK-029 (Jessica, Under Review) | branch menunjuk `4b16009`; handoff lama menyebut `c477e55` → `9ac2ccc` → `371e1f8` — drift belum direview |
| Review Adit TASK-031 | **BLOCKED** — worktree review di baseline, shell/LSP ditolak, patch terpotong sebelum file keamanan; `4b16009` belum disahkan |
| Handoff TASK-009 | `docs/HANDOFF-TASK-009-false-logout-backend.md` (219 baris, sudah ada) |

Batas verifikasi Bimo: read-only, tanpa exec/E2E/runtime probe; klaim implementer dicatat sebagai klaim, bukan verifikasi independen.

---

## 2. Scope backend Jessica yang di-handoff (STOP untuk tim ini)

### 2.1 TASK-014 — Verifikasi konkurensi TASK-002 (Manok `f7634ed`)
- `back-end/apps/assessments/services.py`, `back-end/apps/learning/services.py` — lock user-first, `select_for_update`, mastery/competency/XP.
- Yang belum terbukti: interleaving deterministik PostgreSQL disposable (rendah-vs-tinggi, diagnostic-vs-assessment/lesson), isolasi antar user, mastery tidak turun, XP tidak hilang/berlipat, diagnostic tanpa XP.
- Jangan klaim SQLite membuktikan row-locking PostgreSQL. Timezone shim `GMT`/`USE_TZ=False` bila dipakai wajib dicatat sebagai batas.
- Fix/checklist untuk teman: TransactionTestCase koneksi terpisah + sinkronisasi deterministik; matriks pass/fail/skip + versi DB + command/cwd; defect produk → kembalikan ke implementer, bukan di-fix di tiket QA.

### 2.2 TASK-025 — QA batch (TASK-006/007/008/009 + TASK-014)
- Backend saja yang di-handoff: throttle `apps.accounts/apps.assessments/apps.ai/apps.verification` (429/retry/expiry/isolasi, shared cache/Redis lintas proses, trust proxy), hosting fail-closed (`config/settings.py`, `check --deploy`, Compose), sesi cookie TASK-009 (reload/logout/revoke/refresh paralel/CSRF/SSR/Bearer).
- E2E `e2e/progressio-demo.yaml` + runbook yang menyentuh runtime backend = ikut handoff. Batas heal 3x per flow per percakapan tetap berlaku; jangan rename untuk reset batas.
- Frontend-only dari batch ini (label mock/draft, shell) boleh Jessica lanjut di baseline — lihat §5.

### 2.3 TASK-027 — QA kandidat revisi TASK-006/007/015
- Porsi backend (throttle/hosting/sesi) = handoff. Porsi UI murni (selector unik, assertion draft/invalid, notice expired vs success, sidebar/focus) boleh lanjut di baseline setelah gate §5.
- Jangan redispatch investigasi lama yang gagal composer/shell; baca bukti yang ada dan nyatakan gap eksplisit.

### 2.4 TASK-029 — Regresi + runbook (kandidat `4b16009`, Adit BLOCKED)
- File yang belum clearance: `front-end/tests/backend_server.py:19`, `front-end/check_api_contract.py:16` (pewarisan Redis/Celery env), `qa/test_proxy.py:12` (guard loopback/userinfo/port), `qa/run_services.py:135` (cleanup berhenti di gagal pertama).
- Ada artifact RED/GREEN sekunder di lampiran TASK-029, tetapi Adit belum verifikasi terhadap `4b16009` (SHA drift dari `371e1f8`).
- Untuk teman bila menyentuh automation: sanitizer env SEBELUM import Django (`APP_ENV=local`, `DB_ENGINE=sqlite`, `AI_PROVIDER=mock`, `BLOCKCHAIN_PROVIDER=mock`, DB `:memory:`, tolak warisi `REDIS_URL`/Celery user); guard tolak loopback/userinfo/port milik run; cleanup coba semua owned resource lalu agregasi error; serahkan SATU SHA final + full diff `6720ba1...SHA` + history → Adit re-review → Bimo clearance. Tanpa Redis/data pengguna, tanpa E2E/QA non-keamanan untuk gate ini.

---

## 3. Yang TIDAK boleh dilakukan teman sebelum clearance

- Merge/Approve/cherry-pick `7ffcdb5` atau `4b16009` ke main.
- Menutup HIGH false logout atau HIGH fixture hanya dari state lokal / artifact sekunder.
- Memakai Redis/data pengguna, provider berbayar, atau secret nyata di tes.
- Mengklaim PostgreSQL/Redis/E2E lulus bila skipped/tidak deterministik.

---

## 4. Checklist penutupan untuk teman backend (urut)

1. Rebase ke main terbaru (cakup TASK-007/008/015) agar kandidat stale tidak lepas dari throttle/proxy/cookie.
2. Tutup false logout TASK-009: `logout()` tunggu sukses server; gagal = UI "logout gagal" + sesi dipertahankan untuk retry; sukses = blacklist + `Set-Cookie` hapus (atribut sama); buktikan refresh lama → 401, late-refresh/dua-tab aman, reload sukses/gagal sesuai handoff TASK-009 §5 (7 kasus).
3. Tutup fixture QA §2.4 dalam SATU SHA final; Adit re-review (APPROVED) → Bimo clearance.
4. Tutup konkurensi §2.1 + throttle/hosting §2.2 dengan bukti runtime disposable (bukan klaim).
5. Ajukan SHA final ke Adit → Bimo → E2E/Jessica → Agus. Tanpa lompat gate.

---

## 5. Yang boleh Jessica lanjutkan (non-backend, di baseline saja)

- QA UI murni di `front-end/` + `curriculum/`: fondasi TASK-015, label mock/draft TASK-003, sidebar hanya `/ /catalog /credentials /profile`, flow tanpa active item, `/verify/[id]` tanpa sidebar, focus/keyboard, light/dark, responsive 375/768/1440, reduced motion.
- Syarat isolasi: kerja di baseline `6720ba1`; jangan ubah `back-end/`, `Mobile/`, throttle/hosting/cookie; jangan ambil kode kandidat `7ffcdb5`/`4b16009`; jangan klaim sesi persisten/revoke server; tombol logout = lokal-only; copy "reload memerlukan login ulang".
- Setiap temuan produk backend → laporkan (severity + file:line + reproduksi + fix usulan), jangan di-fix di tiket QA.
- Reviewer tetap Adit (kode) + Jessica (QA); Herman/Owi bukan reviewer. Hasil worker tetap Approve/Discard user.

---

## 6. Kanban — hapus dari papan harus via UI (Bimo tidak hapus)

Alat sesi Bimo tidak menyediakan hapus tiket, dan pembuatan kolom serah-terima ditolak policy board. Maka:

- Owner via UI Kanban: hapus/arsipkan kartu backend murni bila memang tidak dikerjakan tim ini — kandidat: **TASK-010, TASK-023** (sudah dicatat Cecep), plus bila owner setuju: **TASK-014, TASK-025, TASK-027** setelah dokumen ini + artifact TASK-029 diamankan teman. **TASK-029 jangan dihapus** sampai SHA final jelas (menahan bukti `4b16009` + lampiran); biarkan Under Review sebagai referensi teman.
- Alternatif bila ragu hapus: biarkan di Backlog dengan komentar "Scope backend — diserahkan ke teman manusia, tim STOP" agar audit trail tidak hilang.
- Link `TASK-009 blocks TASK-016/017` sudah dilepas Bimo sebelumnya agar UI tidak tertahan; merge/rilis backend tetap BLOCKED.
