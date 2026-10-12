# Handoff Backend — TASK-009 False Logout (untuk teman backend)

**Tanggal:** 8 Oktober 2026
**Penulis:** Bimo (Security Engineer)
**Tiket asal:** TASK-009 — Pertahankan sesi web dengan cookie HttpOnly dan logout di server
**Tiket asesmen:** TASK-028 (Adit, NEEDS CHANGES), TASK-030 (Bimo, BLOCKED HIGH), TASK-032 (gate kelanjutan frontend)
**Status merge kandidat:** TETAP BLOCKED — jangan merge/Approve kandidat lama
**Status frontend:** BOLEH LANJUT di baseline, terisolasi dari kandidat

Dokumen ini adalah handoff resmi issue TASK-009 untuk dikerjakan teman backend (penerus Sugeng).
Sugeng sudah di-stop dari implementasi; tidak ada SHA revisi setelah `7ffcdb5`.

---

## 1. Ringkasan eksekutif

Kandidat `7ffcdb5` (base dilaporkan `d83667c`, main saat review `6720ba1`) memiliki temuan
**HIGH — false logout**: `logout()` di `front-end/src/api.js` menelan kegagalan `POST auth/logout`
(CSRF 403 / 5xx / timeout / network error) lalu tetap membersihkan state lokal. Cookie refresh
HttpOnly belum di-blacklist dan belum dihapus, sehingga reload/bootstrap dapat memulihkan sesi.

Ini melanggar goal TASK-009: "logout mencabut kemampuan refresh sesi terkait".

**Yang harus dilakukan teman backend:**

1. Perbaiki `logout()` agar menunggu sukses server sebelum mengumumkan logout sukses.
2. Pastikan logout sukses me-blacklist refresh token dan menghapus cookie.
3. Tambahkan regression tests sesuai §5.
4. Rebase ke main terkini agar mencakup TASK-007 (throttle), TASK-008 (hosting fail-closed),
   TASK-015 (shell/UI), lalu ajukan SHA final ke Adit → Bimo → Jono/Jessica → Agus.

**Yang tidak boleh dilakukan:**

- Merge/Approve/cherry-pick kandidat `7ffcdb5` ke main.
- Menutup temuan HIGH hanya dari state lokal client.
- Mengklaim aman tanpa bukti runtime + review Adit + clearance Bimo.

---

## 2. Pin SHA dan sumber bukti

| Item | Nilai | Keterangan |
|---|---|---|
| Kandidat | `7ffcdb5` | Branch `task-009-pertahankan-sesi-web-dengan-cookie-httponly-dan`, stale terhadap main |
| Base | `d83667c` | Dilaporkan Adit TASK-028; Bimo tidak bisa verifikasi independen karena tool policy |
| Main saat review | `6720ba1` | Worktree investigasi; diff kandidat..HEAD = 73 file berbeda |
| Baseline frontend | `6720ba1` | `front-end/src/api.js:25-30` = logout lokal-only; `API_CONTRACT.md:30-48` = belum ada logout/revoke |

Sumber bukti primer:

- Komentar Herman di TASK-009 (2026-10-07): "`logout` in `api.js` swallows server errors.
  If the server logout fails, for example on a CSRF 403, the local session still clears
  but the cookie stays valid, so a reload would restore the session."
- Laporan Adit TASK-028 (2026-10-08, BLOCKED/NEEDS CHANGES) + 4 lampiran snapshot kandidat:
  `api.js`, `views.py`, `api.test.js`, `e2e/web-session.yaml`.
- Asesmen Bimo TASK-030 (2026-10-08, BLOCKED HIGH).
- RED terukur Sugeng di TASK-009: keempat kasus (CSRF 403, HTTP 503, timeout, network rejection)
  menunjukkan `logout()` resolve tanpa error (sebelum fix).

Batas verifikasi (jujur): `exec_command`/akses blob kandidat ditolak policy sebelum proses berjalan,
sehingga nomor baris kandidat dan reproduksi runtime independen berstatus SKIP/tool-blocked, bukan pass.
Temuan HIGH didasarkan pada review statis + laporan reviewer, bukan reproduksi runtime Bimo.

---

## 3. Temuan keamanan

### 3.1 HIGH — False logout / sesi refresh tetap hidup [BLOCKING MERGE]

- **Lokasi:** kandidat `front-end/src/api.js`, fungsi `logout()` (nomor baris kandidat belum terverifikasi;
  lihat lampiran TASK-028; di baseline `6720ba1` fungsi lokal ada di `front-end/src/api.js:25-30`).
- **Backend terkait:** kandidat `back-end/apps/accounts/views.py` + `urls.py`
  (blacklist, penghapusan cookie, CSRF protection — line belum terverifikasi).
- **Reproduksi:**
  1. Login hingga browser memegang refresh cookie HttpOnly yang valid.
  2. Paksa `POST auth/logout` mengembalikan CSRF 403, 5xx, timeout, atau network rejection.
  3. Picu logout dari UI web.
  4. Client membersihkan `tokens`/state lokal dan tampak anonim, padahal server tidak mem-blacklist
     token dan tidak mengirim `Set-Cookie` penghapusan.
  5. Reload. Bootstrap sesi memakai cookie yang masih valid dan memulihkan akun.
- **Dampak:** indikasi logout palsu di perangkat bersama; refresh token yang bocor tetap dapat dipakai
  sampai expiry (access 30 menit, refresh 7 hari per kontrak). Melanggar acceptance TASK-009.
- **Referensi:** OWASP Session Management Cheat Sheet (invalidasi sesi di server),
  Django CSRF docs (request cookie-authenticated wajib CSRF header),
  Simple JWT blacklist (menolak refresh berikutnya).

### 3.2 MEDIUM — Gate bukti backend belum terverifikasi

- **Lokasi:** kandidat `back-end/apps/accounts/views.py`, `urls.py`.
- **Isu:** blacklist token, `Set-Cookie` penghapusan (atribut/path harus sama), CSRF reject tanpa side effect,
  dan penolakan refresh lama belum dibuktikan independen.
- **Fix:** tunjukkan test backend yang memeriksa keempat hal itu + cantumkan file:line pada SHA final.

### 3.3 Baseline `6720ba1` (untuk frontend, bukan temuan baru)

- `front-end/src/api.js:25-30`: `logout()` hanya membersihkan memori — jujur sebagai logout lokal-only.
- `front-end/API_CONTRACT.md:30-48`: "Belum ada endpoint logout/revoke token... Logout frontend
  menghapus sesi lokal, bukan mencabut JWT."
- Artinya baseline TIDAK mengandung klaim revokasi palsu. Frontend yang bekerja di baseline
  tidak mewarisi defect HIGH kandidat, selama tidak mengambil kode kandidat `7ffcdb5`.

---

## 4. Fix konkret yang diminta (untuk teman backend)

### 4.1 Frontend `logout()` — jangan umumkan sukses sebelum server sukses

Prinsip: tunggu respons server; gagal = UI "logout gagal/belum selesai", sukses = blacklist + hapus cookie.

```js
// Pola yang diminta (sesuaikan dengan struktur api.js aktual di SHA revisi):
export async function logoutServer() {
  const res = await fetch(base + 'auth/logout', {
    method: 'POST',
    credentials: 'include', // cookie HttpOnly
    headers: { 'X-CSRFToken': getCsrfToken() },
  });
  if (!res.ok) throw new ApiError('Logout gagal. Sesi server belum dicabut.', res.status);
  version += 1;
  tokens = null;
  refreshing = null;
  publish(null, 'logout');
}

// Caller UI wajib:
// try { await logoutServer(); showLogoutSuccess(); }
// catch (e) { showLogoutGagalDanTawarkanRetry(); /* jangan klaim sesi tercabut */ }
```

- Propagasi 403/5xx/timeout/network error ke caller/UI, jangan `catch`-telan lalu `publish(null)`.
- Pertahankan generation/version guard untuk late refresh, tapi jangan menganggapnya revokasi server.
- Audit seluruh caller `logout()` dan pola `catch/finally` yang menghapus sesi setelah request gagal.

### 4.2 Backend logout sukses — blacklist + hapus cookie

- Blacklist refresh token yang disajikan (Simple JWT token_blacklist atau store setara).
- Kirim `Set-Cookie` penghapusan dengan nama/path/domain/SameSite/Secure yang SAMA dengan saat set.
- Lindungi endpoint cookie-authenticated dengan `csrf_protect` + origin check.
- Buktikan refresh memakai cookie lama setelah logout sukses → `401`.
- Pertahankan: web refresh cookie-only, Bearer eksplisit di `/auth/login/bearer` untuk Mobile,
  throttle TASK-007 pada login/register/refresh/logout, CORS/CSRF fail-closed TASK-008.

---

## 5. Regression tests wajib (TDD: RED dulu, lalu GREEN)

1. Logout CSRF 403 → `logout()` reject, UI menampilkan gagal, tidak ada status sukses palsu.
2. Logout HTTP 503 → sama seperti di atas.
3. Logout timeout / network rejection → sama, sesi lokal tidak dipresentasikan sebagai tercabut.
4. Logout sukses → cookie terhapus, refresh cookie lama → 401, reload tetap anonim.
5. Reload setelah logout GAGAL → membuktikan sesi dapat pulih (inilah alasan UI wajib warning).
6. Late refresh race + dua tab: respons refresh yang datang terlambat tidak boleh menghidupkan
   sesi yang sudah logout, dan tidak menimpa hasil logout.
7. Regresi integrasi: throttle TASK-007, hosting/CSRF TASK-008, shell/session notice TASK-015.

Target coverage minimal 80% untuk kode baru (Testing Standards tim).
Perintah yang harus dicatat dengan cwd + pass/fail/skip nyata:

```bash
# dari front-end/
npm test
npm run build
# dari back-end/
python manage.py test apps.accounts
# probe kontrak terbaru + LSP untuk file yang diubah + E2E Sokudo (hanya via e2e_* tools)
```

Jangan print secret/token/PII di log. Jika menemukan secret ter-expose, laporkan jenis/lokasi saja
dan eskalasi rotasi ke owner (jangan rotasi sendiri).

---

## 6. Integrasi yang wajib dipertahankan (jangan regresi)

- **TASK-007 throttle:** login/register/refresh (dan route auth baru termasuk logout/bearer bila sesuai)
  tetap terkena rate-limit; pakai shared cache untuk profil hosted.
- **TASK-008 hosting:** `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS` fail-closed tetap otoritatif;
  Secure cookie/CSRF/session transport sesuai profil; jangan trust proxy global tanpa topologi.
- **TASK-015 fondasi UI:** perilaku sesi/shell, auth guard, notice sesi, routing/sidebar/focus tidak regresi.
- **Mobile:** jalur Bearer eksplisit tetap ada; jangan memaksa cookie web ke Mobile.
- **Access token yang sudah terbit:** tetap hidup sampai expiry 30 menit (keputusan Gatot yang dicatat Sugeng);
  yang dicabut adalah kemampuan refresh sesi terkait.

---

## 7. Mengapa frontend boleh lanjut sementara merge tetap BLOCKED

- **Merge kandidat = BLOCKED** sampai HIGH di atas fix + bukti + Adit re-review + clearance Bimo.
  Ini tidak bisa dicabut dari laporan ini. Mencabutnya tanpa fix melanggar Security-first tim.
- **Frontend boleh lanjut** dengan syarat ketat: kerjakan di baseline `6720ba1` saja,
  jangan ambil kode kandidat `7ffcdb5`; jangan klaim revokasi server/sesi persisten di UI
  (kontrak baseline §3.3); TASK-016/017 dilepas dari blokir TASK-009 agar tidak tertahan
  oleh backend yang sudah diserahkan ke manusia.
- Gate berikutnya untuk SHA final backend: Adit (kode) → Bimo (security) → Jono E2E / Jessica QA → Agus (rilis).

---

## 8. Langkah lanjut untuk teman backend (checklist serah terima)

- [ ] Baca TASK-009 (brief + seluruh komentar), TASK-028 (laporan + 4 lampiran), TASK-030 (asesmen Bimo).
- [ ] Pin ulang main/baseline aktual; jangan asumsikan main = kandidat.
- [ ] Terapkan fix §4 di atas main terkini (rebase/integrasi TASK-007/008/015, bukan merge paksa).
- [ ] Tulis/jalankan regression tests §5; catat SHA final + command/cwd + hasil.
- [ ] Perbarui `API_CONTRACT.md`/docs/changelog yang terverifikasi (tanpa placeholder, tanpa duplikasi).
- [ ] Serahkan SHA final ke Adit untuk re-review; jangan minta clearance Bimo sebelum Adit selesai.
- [ ] Jika butuh kredensial/env produksi: minta ke owner; jangan hardcode secret.

Pertanyaan untuk owner sebelum mulai: di mana worktree/branch kandidat `7ffcdb5` tersimpan sekarang,
dan apakah perubahan staged/konflik merge rate-limit yang dilaporkan Sugeng masih ada?
Jangan menghapus perubahan parsial sebelum diinventarisasi.

---

## 9. Lampiran dan rujukan

- TASK-009 komentar Herman (cookie/CSRF/logout/blacklist/Mobile) + RED Sugeng (4 kasus logout).
- TASK-028 laporan Adit + snapshot `api.js`, `views.py`, `api.test.js`, `web-session.yaml`.
- TASK-030 asesmen Bimo + referensi OWASP/Django/SimpleJWT.
- File baseline yang dibaca untuk laporan ini: `front-end/src/api.js`, `front-end/API_CONTRACT.md`.
