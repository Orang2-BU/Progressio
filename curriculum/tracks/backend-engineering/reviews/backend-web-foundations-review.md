# Paket review kurikulum + kalibrasi rubrik — `backend-web-foundations` (satu competency)

- Track: `backend-engineering`, paket versi `0.1.0`, status **`draft`** (`version.yaml`, `curriculum.yaml` metadata).
- Scope: competency `competencies/backend-web-foundations.yaml` + 2 skill
  (`client-server-model`, `http-messages-and-semantics`) beserta assessment, grading,
  diagnostic, study-step, dan resource terkait.
- Tanggal paket: 2026-10-07. Audit acuan: commit `9d8ed8c` (5 Okt 2026) — file terkait
  tidak berubah sejak audit selain pekerjaan tiket ini (pengecekan via `git log` pada
  `curriculum/tracks/backend-engineering/` dan `back-end/apps/credentials/`).
- **Status paket ini: USULAN REVIEW, bukan sertifikasi.**
  Review manusia **belum dilakukan — PENDING**.
  Tidak ada flag `reviewed` yang diubah, tidak ada `passing_score`/`answer_key`/rubrik yang
  diubah, tidak ada credential final yang diterbitkan oleh paket ini.

## 0. Ringkasan untuk reviewer

1. Matriks §1 memetakan keempat observable behavior ke study step, butir assessment/rubrik,
   dan expected evidence. Semua perilaku terpetakan; dua gap penerapan ditandai
   (GAP-1, GAP-2) — keduanya soal penerapan, bukan hafalan.
2. Kalibrasi §2 memberi tiga evidence sintetis (kuat / lemah / borderline) dengan alasan skor
   per kriteria rubrik `http-messages-and-semantics-assessment` (bobot 30/30/25/15, lulus 70)
   plus satu contoh batas lulus kuis rules `client-server-model` (5/6 lulus, 4/6 gagal).
   Evidence ini **sintetis untuk kalibrasi reviewer** — bukan validasi keakuratan penilai,
   dan bukan hasil mock.
3. Ambiguitas dan usulan perubahan spesifik ada di §3. Setiap usulan mencantumkan dampak
   versi/migrasi dan **tanpa mengubah reviewed flag**.
4. Sumber, keputusan terbuka, dan checklist persetujuan ada di §4–§6.

## 1. Matriks observable behavior → study step → assessment/rubrik → expected evidence

Kompetensi mengklaim 4 observable behavior:

- OB1: "Traces a request from client to server and back."
- OB2: "Inspects an HTTP message."
- OB3: "Distinguishes method intent from URI naming."
- OB4: "Selects response status and headers that communicate the outcome."

Legenda tipe butir: **[H] hafalan/pengenalan**, **[P] penerapan** (memutuskan/memperbaiki pada kasus).

### OB1 — Traces a request from client to server and back

| Rantai | Isi |
|---|---|
| Study steps | `csm-s1` (baca `mdn-client-server`, gambar alur request browser→server→balik; checkpoint "which side initiates?" → `client`) **[H→P-ringan]**; `csm-s2` (baca `mdn-http-overview`, pilah bagian halaman server vs browser; checkpoint `stateless`) **[H]** |
| Assessment (rules) | `csm-1` inisiator = client **[H]**; `csm-4` tiap request ditangani independen **[H]**; `csm-6` peran DNS = resolve hostname→IP **[H, tangensial — lihat A2]** |
| Diagnostic | `csm-d1` stateless = tiap request membawa info yang dibutuhkan **[H]**; `csm-d2` menyembunyikan tombol admin ≠ proteksi, server tetap harus menolak **[P-ringan]** |
| Rubrik | Tidak ada (skill ini mode `rules`, bukan rubrik AI) |
| Expected evidence | `annotated-request-response-diagram` |
| Penilaian | Alur dasar terliput. Yang diuji kebanyakan **hafalan definisi**; satu-satunya penerapan adalah `csm-d2`/`csm-5` (enforcement di server). **GAP-1 (penerapan):** tidak ada butir yang meminta learner menelusuri *satu pertukaran konkret* (mis. beri request/response mentah lalu minta labeli client/server/resource/request/response + jelaskan independensi request). Study step `csm-s1` memerintahkan itu sebagai latihan, tetapi grading rules tidak menagihnya — evidence yang dijanjikan (`annotated-...-diagram`) tidak dinilai oleh kunci jawaban 6 soal. |

### OB2 — Inspects an HTTP message

| Rantai | Isi |
|---|---|
| Study steps | `hms-s1` (baca `mdn-http-messages`, anotasi request nyata: start line, headers, body; checkpoint "bagian mana membawa status code?" → `status line`) **[H→P-ringan]** |
| Assessment (AI) | `http-messages-and-semantics-assessment` (debugging-task: "Correct the request or response and explain the changes"); expected evidence `corrected-request-response` + `rationale`; mastery "Method, status, headers and body align with the stated operation and outcome" **[P]** |
| Rubrik (AI, bobot) | K1 identifikasi fault secara presisi (30) **[P]**; K2 diagnosis merujuk semantik method/status yang benar (30) **[P]**; K3 fix menyelesaikan fault tanpa merusak perilaku lain (25) **[P]**; K4 penalaran tertelusur ke sumber otoritatif (15) **[P]** |
| Diagnostic | `hms-2` (malformed body → kelas `4xx`) **[P-ringan]** |
| Expected evidence | `corrected-request-response`, `rationale` |
| Penilaian | Satu-satunya perilaku yang dinilai murni lewat **penerapan** — bagus. **GAP-2 (ketertelusuran):** paket tidak mem-pin *instance fault* yang dikerjakan learner (prompt hanya "Correct the request or response"). Reviewer tidak bisa memverifikasi apa yang sebenarnya dilihat learner, dan dua learner bisa dinilai atas fault berbeda dengan tingkat sulit berbeda. Kalibrasi §2 memakai satu fault kanonis **usulan** (bukan isi paket) agar reviewer bisa menilai; adopsi fault kanonis adalah keputusan D1. |

### OB3 — Distinguishes method intent from URI naming

| Rantai | Isi |
|---|---|
| Study steps | `hms-s3` (baca RFC 9110 `#name-idempotent-methods`, jelaskan kenapa retry PUT aman tapi POST belum tentu; checkpoint "satu method idempotent tapi tidak safe" → `PUT`) **[H]** |
| Assessment (AI) | K2 rubrik (semantik method) **[P]** |
| Diagnostic | `hms-1` (idempotent = `PUT`, bukan `POST`) **[H]** |
| Expected evidence | `rationale` (bagian method dari debugging task) |
| Penilaian | Konsep idempotensi diajarkan sebagai **hafalan** (checkpoint + diagnostik sama-sama tanya definisi). Penerapannya hanya implisit di K2 rubrik ("pilih method yang semantiknya cocok") tanpa skenario pemilihan yang eksplisit di paket (mis. "operasi transfer dana yang ter-retry harus memakai method apa dan kenapa?"). **Ditandai gap penerapan parsial** — tertutup *jika* fault kanonis memuat kesalahan method (usulan D1 mencakup itu), terbuka jika tidak. Tidak ada butir soal URI-naming vs method-intent secara harfiah (mis. `GET /deleteUser` yang salah memakai method) — reviewer memutuskan apakah perlu ditambah (D4). |

### OB4 — Selects response status and headers that communicate the outcome

| Rantai | Isi |
|---|---|
| Study steps | `hms-s2` (baca referensi status MDN, tentukan status untuk: resource dibuat, body malformed, path hilang; checkpoint `201`) **[H→P-ringan]** |
| Assessment | Rules: `csm-3` (path tidak ada → `404`, bukan 200-kosong atau tanpa respons) **[H]**; AI: K2+K3 rubrik (status/headers/body selaras operasi & outcome) **[P]** |
| Diagnostic | `hms-2` (`4xx` untuk body malformed) **[P-ringan]**; `hms-3` (`201` = resource baru dibuat) **[H]** |
| Expected evidence | `corrected-request-response` (bagian status/headers), `rationale` |
| Penilaian | Fondasi hafalan (kode-kode umum) + penerapan di rubrik AI. Batas 201-vs-200 dan kelengkapan header (`Location`, `Content-Type`) adalah titik sensitif kalibrasi — lihat evidence C §2 dan ambiguitas A5/A7. |

### Keterkaitan learning outcomes (skill) — semua tercakup, tidak ada outcome yatim

- `client-server-model`: "Identify client, server, request, response and resource" → OB1; "Explain why HTTP requests are independently interpretable" → OB1 (`csm-4`, `csm-d1`).
- `http-messages-and-semantics`: "Interpret a request line, headers and body" → OB2; "Select a method and status code whose semantics match an operation" → OB3+OB4; "Construct a response that distinguishes success from client error" → OB4 (`hms-2`).

## 2. Kalibrasi rubrik — tiga evidence sintetis + satu contoh batas kuis

Konteks penilaian: rubrik `grading/http-messages-and-semantics-assessment.yaml`
(mode `ai`, `review_status: draft`, `passing_score: 70`, `max_score: 100`).
K1=30, K2=30, K3=25, K4=15.

Karena paket tidak mem-pin fault instance (GAP-2), kalibrasi memakai **fault kanonis usulan**
agar skor bisa dibandingkan. Fault kanonis (usulan, belum bagian paket):

> Operasi: `POST /users` membuat user baru dengan body JSON valid.
> Respons yang diberikan ke learner (salah): `200 OK` tanpa header `Location`,
> tanpa `Content-Type`, body `{"ok": true}`.
> Perbaikan yang diharapkan: status `201 Created` + `Location: /users/{id}` +
> `Content-Type: application/json` + body representasi user; alasan merujuk
> semantik 201 (resource baru dibuat) dan peran header; method POST dipertahankan
> karena operasinya create non-idempoten (bukan diganti PUT).

Ketiga evidence di bawah adalah **sintetis, ditulis untuk kalibrasi ini** —
bukan keluaran mock dan tidak dipakai sebagai klaim akurasi penilai AI/rules.

### Evidence A — kuat (harus lulus)

Jawaban learner: menunjukkan tepat dua fault (status 200 seharusnya 201 karena resource
baru dibuat; header `Location` dan `Content-Type` hilang), menjelaskan kenapa POST tetap
benar (create tidak idempoten, retry tidak aman) dengan rujukan pasal RFC 9110 §15.3.2
dan halaman status MDN, lalu menulis respons terkoreksi lengkap yang tidak mengubah
body valid menjadi rusak.

| Kriteria (bobot) | Skor | Alasan |
|---|---|---|
| K1 identifikasi presisi (30) | 28 | Kedua fault ditunjuk baris-per-baris; kurang 2 karena tidak menyebut body `{"ok": true}` minim sebagai observasi eksplisit |
| K2 semantik method/status (30) | 28 | 201-vs-200 dan POST-dipertahankan dijelaskan benar; kurang 2 karena nomor pasal RFC untuk idempotensi tidak disebut |
| K3 fix tanpa merusak (25) | 24 | Respons terkoreksi lengkap dan operasional; kurang 1 karena tidak menyatakan retry-safety secara eksplisit |
| K4 tertelusur ke sumber (15) | 14 | Rujukan pasal + halaman spesifik, bisa diverifikasi; kurang 1 karena tidak ada kutipan baris |
| **Total** | **94 → LULUS** | Jarak 24 poin di atas batas; contoh "jelas lulus" untuk kalibrasi atas |

### Evidence B — lemah (harus gagal)

Jawaban learner: mengganti body menjadi `{"success": true, "message": "user created"}`
tetapi membiarkan `200 OK` tanpa header; mengusulkan "lain kali pakai PUT agar idempoten";
alasan hanya "supaya frontend tahu sukses", tanpa rujukan sumber.

| Kriteria (bobot) | Skor | Alasan |
|---|---|---|
| K1 (30) | 10 | Fault sebenarnya (status + header) tidak teridentifikasi; hanya mengecat ulang body |
| K2 (30) | 8 | Klaim PUT-untuk-create salah secara semantik (mengacaukan idempotensi dengan create); 200-vs-201 tidak dibahas |
| K3 (25) | 8 | Fault tidak terselesaikan; perubahan kosmetik body; saran PUT justru merusak semantik operasi |
| K4 (15) | 3 | Tidak ada sumber; "supaya frontend tahu" bukan semantik HTTP |
| **Total** | **29 → GAGAL** | Jarak 41 poin di bawah batas; contoh "jelas gagal" untuk kalibrasi bawah |

### Evidence C — borderline (keputusan reviewer paling dibutuhkan)

Jawaban learner: memperbaiki status menjadi `201 Created` dengan penjelasan 201-vs-200 yang
benar dan rujukan halaman status MDN, tetapi **tidak menambahkan `Location`** ("body sudah
berisi id, jadi client bisa membangun URL sendiri"); `Content-Type` ditambahkan.
Tidak membahas method.

| Kriteria (bobot) | Skor | Alasan |
|---|---|---|
| K1 (30) | 22 | Fault status tertangkap presisi; kehilangan header `Location` tidak dianggap fault oleh learner |
| K2 (30) | 20 | Semantik 201 benar; semantik method tidak dibahas (fault kanonis memang tidak menguji method — lihat D1) |
| K3 (25) | 15 | Respons berfungsi untuk client yang toleran, tetapi melanggar ekspektasi 201 + `Location` untuk create; apakah ini "menyelesaikan fault" adalah keputusan D2 |
| K4 (15) | 8 | Rujukan MDN benar tetapi umum (halaman, bukan bagian); tidak ada rujukan RFC |
| **Total** | **65 → GAGAL (5 poin di bawah 70)** | Tepat di bawah batas. Jika reviewer memutuskan `Location` wajib untuk lulus, skor ini benar sebagai gagal-tipis dan menunjukkan batas bekerja. Jika reviewer memutuskan `Location` opsional (cukup 201 + body), K3 naik ke ~20 dan total menjadi ~70 — lulus-tipis. **Inilah titik kalibrasi yang harus diputuskan manusia (D2), bukan oleh penilai.** |

### Contoh batas kuis rules (`client-server-model`, 6 soal, lulus 70)

- 5/6 benar = 83,3 → LULUS; 4/6 benar = 66,7 → GAGAL. Satu soal mengubah hasil.
  Kombinasi yang gagal-tipis dan perlu perhatian: learner yang benar semua kecuali
  `csm-5` (enforcement otorisasi di server) tetap lulus 83 — padahal itu satu-satunya
  butir keamanan. Reviewer memutuskan apakah butir keamanan boleh dikompensasi
  butir lain (D5).

## 3. Ambiguitas soal/answer key dan batas passing score — usulan spesifik

Semua usulan di bawah ini **tidak diterapkan di paket ini** — mereka menunggu keputusan
reviewer. Dampak versi/migrasi dicantumkan agar keputusan bisa dieksekusi tanpa menebak.
Tidak ada usulan yang mengubah `review_status` menjadi `reviewed`.

- **A1 — Instance fault debugging-task tidak di-pin (GAP-2).**
  Usulan: tambah lampiran `task_instance` (fault kanonis §2 atau setara) sebagai data
  grading terpisah, bukan mengubah prompt assessment yang sudah ada.
  Dampak: butuh field baru di skema grading → `schema_version` dipertimbangkan naik;
  minimal `curriculum_version` naik `0.1.0 → 0.2.0` (tetap `draft`) agar snapshot
  `evaluation.curriculum_version` lama tidak tercampur dengan yang baru (eligibility
  mem-pin versi). Tanpa perubahan ini, skor AI antar-learner tidak sebanding.
- **A2 — `csm-6` (DNS) di luar cakupan skill.**
  Resource skill ini hanya `mdn-client-server` + `mdn-http-overview`; tidak ada materi
  DNS. Usulan: hapus butir atau pindahkan ke skill jaringan tersendiri.
  Dampak: `0.1.0 → 0.1.1` atau `0.2.0` (tetap draft); kunci jawaban ikut diperbarui;
  tidak ada migrasi credential (belum ada issuance final di atas draft).
- **A3 — `csm-2` mengasumsikan pengetahuan SSR.**
  "in a server-side rendered application" adalah konteks yang tidak diajarkan di
  resource skill. Usulan ubah menjadi "in a database-backed page" tanpa mengubah
  kunci (`db`). Dampak: edit prompt saja; versi patch/minor draft.
- **A4 — Batas 70 pada kuis 6 soal terlalu kasar.**
  4/6 (66,7) gagal vs 5/6 (83,3) lulus — satu soal menentukan; butir keamanan
  (`csm-5`) bisa dikompensasi. Usulan (pilih satu, D5): (a) tambah ≥2 butir penerapan
  (total 8, tiap butir 12,5); (b) beri bobot ganda pada `csm-5`; atau
  (c) dokumentasikan bahwa 70 pada 6 soal diterima dengan risiko ini.
  Dampak: (a)/(b) mengubah `max_score`/`passing_score` → versi minor draft + sinkron
  `assessments/` ↔ `grading/` (validator menegakkan kesamaan `passing_score` dan
  `estimated_minutes`).
- **A5 — K4 "traceable to an authoritative source" belum operasional.**
  Usulan: syaratkan rujukan setingkat bagian (RFC § / judul bagian MDN), bukan
  "per MDN" generik; tentukan K4=0 bila tidak ada rujukan yang bisa diverifikasi.
  Dampak: klarifikasi panduan penilai; versi minor draft. Evidence C menunjukkan
  K4 generik vs spesifik bernilai 8 vs 14 — perbedaan yang bisa melewatkan batas.
- **A6 — "Independently interpretable" vs "independently handled" tercampur.**
  `csm-4` (konkurensi: dua user sekaligus) dan `csm-d1` (statelessness: request
  membawa konteksnya) menguji dua ide berbeda dengan kata yang mirip.
  Usulan: tulis ulang `csm-4` agar menyebut konkurensi eksplisit, atau pecah menjadi
  dua butir. Dampak: edit prompt; versi patch/minor draft.
- **A7 — Nuansa 201-vs-200 belum diputuskan.**
  Praktik nyata kadang memakai `200 OK` + representasi untuk create. Rubrik saat ini
  ("status … align with the stated operation") tidak menyatakan apakah itu lulus.
  Usulan: tetapkan untuk operasi create pada fault kanonis bahwa `201` + `Location`
  adalah jawaban lulus (keputusan D2), dan catat pengecualian yang diizinkan.
  Dampak: panduan penilai; versi minor draft.

## 4. Sumber primer / bukti sumber yang masih perlu diperiksa

Rujukan hak-pakai: `docs/source-review.md` (audit 2026-10-05). Fakta yang dipakai ulang
dari sana: `check_links` run 2 `ok=17 moved=0 broken=0` (HTTP-only, header-only);
`mdn-client-server` sempat `broken` transien di run 1 lalu HEAD+GET 200 saat re-probe;
**semua 13 resource `license_verified: false`** — tidak ada yang diubah review itu.
Prinsip yang dipegang paket ini: **HTTP 200 = akses terbuka, bukan izin pakai-ulang.**

| Resource (skill cakupan) | URL | Status paket | Yang masih harus diperiksa reviewer |
|---|---|---|---|
| `mdn-client-server` | https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview | `CC-BY-SA-2.5`, `license_verified: false`, atrib. wajib | Konfirmasi per-konten sebelum menyalin teks apa pun (contoh kode MDN berlisensi terpisah); konten Learn MDN direstrukturasi berkala — cek ulang sebelum presentasi |
| `mdn-http-overview` | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | `CC-BY-SA-2.5`, `license_verified: false` | Sama seperti di atas; link-only sampai ada bukti per-konten |
| `mdn-http-messages` | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages | `CC-BY-SA-2.5`, `license_verified: false` | Sama; halaman anatomi pesan — kandidat kutipan K4, perlu anchor bagian yang stabil |
| `mdn-http-status` | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status | `CC-BY-SA-2.5`, `license_verified: false` | Sama; pastikan kode yang dirujuk (201/400/404) sesuai revisi halaman saat review |
| `rfc-9110` | https://www.rfc-editor.org/rfc/rfc9110.html | `IETF-Trust`, `license_verified: false` | Batasan kutipan/publikasi-ulang teks RFC di luar lisensi terbuka biasa; cek metadata obsoleted-by/updated-by sebelum presentasi; `hms-s3` memakai anchor `#name-idempotent-methods` — verifikasi anchor masih valid |

Catatan: `mdn-http-methods` mendukung skill `api-contract-design` (di luar cakupan paket
ini) — tidak dinilai di sini. Penggunaan Progressio atas semua sumber di atas adalah
**tautan keluar (link-only)**; tidak ada materi penerbit yang disalin ke paket ini.

## 5. Keputusan reviewer yang dibutuhkan

- **D1.** Adopsi fault kanonis §2 (atau fault pengganti yang setara sulitnya) sebagai
  `task_instance` resmi. Tanpa ini, GAP-2 tetap terbuka dan skor AI tidak sebanding.
- **D2.** Apakah `Location` pada respons 201-create **wajib untuk lulus** (maka Evidence C
  = 65 gagal-tipis, benar) atau opsional bila body memuat id (maka C ≈ 70 lulus-tipis)?
- **D3.** Ambang K4: apakah rujukan generik "per MDN" cukup untuk sebagian poin, atau
  harus setingkat bagian untuk poin penuh dan nol bila tak terverifikasi?
- **D4.** Apakah butir "method intent vs URI naming" harfiah (mis. `GET /deleteUser`)
  perlu ditambah, atau cakupan K2 saat ini cukup untuk OB3?
- **D5.** Batas kuis: terima 70/6-soal apa adanya, tambah butir, atau beri bobot ganda
  pada `csm-5` (otorisasi sisi-server)?
- **D6.** Nasib `csm-6` (DNS): hapus, pindahkan, atau tambah materi DNS ke resource skill?
- **D7.** Redaksi `csm-2` (SSR → "database-backed") dan `csm-4` (konkurensi eksplisit):
  setujui redaksi usulan atau tulis redaksi sendiri?
- **D8.** Keputusan versi: naikkan `0.1.0 → 0.2.0` (tetap `draft`) untuk setiap perubahan
  A1–A7 yang diadopsi, agar snapshot `evaluation.curriculum_version` tidak tercampur?
  (Direkomendasikan: ya.)

## 6. Checklist persetujuan (semua PENDING)

- [ ] PENDING — Reviewer menyetujui matriks §1 (atau meminta pemetaan ulang OB yang dipersengketakan).
- [ ] PENDING — Reviewer mengunci jawaban D1–D8 dengan keputusan terdokumentasi (nama + tanggal).
- [ ] PENDING — Perubahan A1–A7 yang disetujui diterapkan sebagai PR terpisah dengan bump
  versi draft (`0.1.0 → 0.2.0` bila ada perubahan penilaian) — **bukan di paket ini**.
- [ ] PENDING — Verifikasi lisensi per-konten (§4) selesai sebelum materi apa pun disalin;
  sampai saat itu tetap link-only + atribusi.
- [ ] PENDING — Kalibrasi antar-reviewer: dua reviewer menilai Evidence A/B/C secara
  independen dan selisih total ≤ 10 poin sebelum rubrik dipakai formatif.
- [ ] PENDING — **Status `draft` dipertahankan.** Flip ke `reviewed` hanya oleh keputusan
  reviewer yang terdokumentasi, setelah semua kotak di atas tercentang — bukan oleh
  paket ini. Tes `apps.credentials` (13 tes, lulus 2026-10-07) dan guard
  `back-end/apps/credentials/services.py:34-36` (versi aktif + track reviewed +
  evidence reviewed non-mock + provider nyata) tetap menjadi penolak issuance final
  untuk paket draft.

## 7. Verifikasi paket ini

- `python -m unittest discover -s curriculum -t .` → 18 tes lulus (paket review berupa
  direktori `reviews/` di luar folder yang divalidasi `validator.py`, jadi tidak
  memengaruhi validasi).
- `python back-end/manage.py test apps.credentials` (sqlite/mock) → 13 tes lulus;
  guard issuance final tidak diubah.
- File yang ditambah: `curriculum/tracks/backend-engineering/reviews/backend-web-foundations-review.md`
  (file ini). File yang diubah: tidak ada — khususnya `version.yaml`,
  `curriculum.yaml`, seluruh `grading/`, `assessments/`, dan
  `back-end/apps/credentials/services.py` **tidak disentuh**.
