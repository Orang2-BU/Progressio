# Kontrak API frontend — Fase 0

Audit 29 September 2026, baseline `caf83e6` (working tree awal bersih).
Sumber: URL, serializer, view, service, dan settings di `back-end/`.
OpenAPI tersedia di `/api/schema/`, Swagger di `/api/docs/`.
Dokumen ini membedakan perilaku saat ini dan perubahan yang masih dibutuhkan.

## Konvensi integrasi

- Base path: `/api/v1/`; origin backend dikonfigurasi saat implementasi frontend.
- JSON untuk request/response. Gunakan path persis di tabel, termasuk slash akhir.
  Jangan mengandalkan redirect untuk POST.
- ID katalog, lesson, assessment, submission, diagnostic: integer. Credential: UUID.
  Roadmap, learning-path filter, dan study-plan memakai slug sebagaimana tabel.
- `P<T>` = `{count, next, previous, results: T[]}`, ukuran halaman default 20,
  query `?page=2`. Selalu tangani `next`; jangan menganggap halaman pertama lengkap.
- `A<T>` = array biasa. Endpoint APIView umumnya mengembalikan objek biasa.
- Tanggal berupa string ISO; skor dapat berupa float dan submission score bisa null.
- Jangan lampirkan token kedaluwarsa pada request publik: autentikasi tetap berjalan
  meskipun endpoint memakai `AllowAny`.

## Autentikasi dan sesi

| Method / path | Request | Respons sukses |
|---|---|---|
| POST `auth/register` | username, email, password, password_confirm, role opsional | 201 profil, tanpa token |
| POST `auth/login` | username, password | 200 `{access, refresh}` |
| POST `auth/refresh` | refresh | 200 `{access}` |
| GET `auth/me` | Bearer access | 200 `{id, username, email, role, date_joined}` |

Login memakai username, bukan email. Registrasi publik menolak role admin;
student/recruiter diperbolehkan. Access berlaku 30 menit, refresh 7 hari;
refresh tidak dirotasi. Belum ada endpoint logout/revoke token, reset password,
atau edit profil. Logout frontend nanti menghapus sesi lokal, bukan mencabut JWT.

Rencana client: satu refresh bersama untuk request bersamaan yang mendapat 401,
coba ulang satu kali setelah refresh sukses; refresh gagal mengakhiri sesi.
Jangan refresh berulang untuk login gagal. Penyimpanan token belum diimplementasikan:
gunakan access di memori; sesi persisten dengan cookie HttpOnly memerlukan dukungan
backend/BFF dan konfigurasi CSRF/cookie tersendiri. CORS saat ini dikonfigurasi melalui
`CORS_ALLOWED_ORIGINS`; tetapkan origin web yang digunakan saat integrasi.

## Halaman → endpoint aktual

Seluruh GET di tabel mengembalikan 200 kecuali dinyatakan lain.
`Privat` berarti IsAuthenticated, bukan pembatasan role student.

| Halaman | Method / path | Akses | Kontrak penting |
|---|---|---|---|
| Pilih target | GET `career-tracks/`, `career-tracks/{id}` | Publik | list P; id, slug, title, description, is_active; detail competency_count |
| Pilih competency | GET `competencies/?career_track={id}`, `competencies/{id}` | Publik | list P; career_track ID, slug, title, description, order; detail skill_count |
| Pilih skill | GET `skills/?competency={id}`, `skills/{id}` | Publik | list P; competency ID, slug, difficulty, estimated_learning_minutes; detail prerequisites, lesson_count |
| Diagnostic | GET `diagnostics/{track_id}` | Privat | A; id, skill, skill_title, prompt, options[{value,label}], order |
| Kirim diagnostic | POST `diagnostics/{track_id}/submit` | Privat | 201 DiagnosticAttempt; semua ID soal wajib ada |
| Hasil terakhir | GET `diagnostics/latest?career_track={id}` | Privat | objek attempt; 404 jika belum ada; ada bug multi-attempt (G1) |
| Dashboard | GET `progress` | Privat | total_xp, completed_lessons_count, competencies[], skills[] |
| Peta skill | GET `learning-path?career_track={slug}` | Privat | A; skill_id, skill_slug, status, mastery, xp, missing_prerequisites[] |
| Roadmap | GET `roadmap?skill={slug}` atau `?competency={slug}` atau `?career_track={slug}` | Privat | tepat satu target; target, total_steps, remaining_minutes, remaining_hours, already_satisfied[], steps[] |
| Materi | GET `lessons?skill={id}`, `skills/{id}/lessons`, `lessons/{id}` | Publik | kedua list P; content_url, content_type, duration, provider, license, license_url, attribution_required, link_status |
| Study plan | GET `skills/{slug}/study-plan` | Publik | P; id, lesson, order, prompt, checkpoint_question, estimated_minutes, study_url, provider, license |
| Checkpoint | POST `study-steps/{id}/checkpoint` | Privat | 200 `{correct, feedback}`; tidak menyimpan completion atau XP |
| Selesai lesson | POST `lesson/{id}/complete` | Privat | tanpa body; 200 status, lesson_id, lesson_title, xp_earned, newly_completed, current_skill_mastery, current_skill_xp |
| Assessment | GET `assessments/?skill={id}`, `assessments/{id}` | Publik | list P; detail instructions, objective, expected_evidence, mastery_criteria, questions, estimated_minutes |
| Submission | POST `assessments/{id}/submit` | Privat | 201 submission; penilaian sinkron dalam request |
| Daftar credential | GET `credentials/?status=issued&competency={id}` | Privat | P milik user; id UUID, competency, status, score, issued_at |
| Terbitkan credential | POST `credentials/issue` | Privat | 201 detail; penolakan kelayakan 400 |
| Detail credential | GET `credentials/{uuid}` | Privat | hanya pemilik; metadata, evidences, is_valid, verification_url |
| Verifikasi recruiter | GET `verify/{uuid}` | Publik | credential_id, status, is_valid, integrity_verified, integrity_reason, student_name, evidences, blockchain_proof |

Simpan pasangan ID dan slug dari katalog; jangan hardcode ID seed.
Gunakan parent ID dari katalog untuk menentukan track dari target skill.
Roadmap step memuat skill_id/slug, competency_title, difficulty, estimated_minutes,
mastery, prerequisites (slug[]), is_target, order.
Tidak ada penyimpanan target pilihan user di backend. Untuk MVP, target dapat
diwakili di URL halaman web; lintas perangkat memerlukan endpoint preferensi.

## Payload dan respons kunci

Diagnostic memakai ID database soal sebagai key string. Contoh ini ilustrasi;
ambil ID dan opsi dari GET, serta sertakan seluruh soal yang diterima:

```json
{"answers":{"41":"guard","42":"while"}}
```

Respons attempt: `id, career_track, career_track_title, overall_score,
skill_scores, recommended_skill_ids, completed_at`.
Tiap skill_scores: `skill_id, skill_title, score, correct_answers, total_questions`.
Diagnostic yang diulang mempertahankan mastery tertinggi, bukan menggantinya
dengan skor terakhir; hasil attempt dan progress dapat berbeda.

Kuis memakai ID string dari `assessment.questions`, bukan ID database diagnostic:

```json
{"content":{"answers":{"csm-1":"client","csm-2":"db"}}}
```

Challenge/project memakai JSON evidence, contoh form yang kompatibel dengan mock:

```json
{"content":{"code":"...","readme":"...","test_output":"...","repository_summary":"...","files":{"openapi.yaml":"..."}}}
```

`content` masih DictField bebas (default `{}`), batas 200.000 byte dari
JSON UTF-8 yang diserialisasi Python. Bentuk per tipe belum divalidasi ketat.
Top-level `score` ditolak 400. Belum ada upload multipart, eksekusi kode sandbox,
atau pengambilan isi repository otomatis; URL saja bukan isi evidence.
Jawaban kuis yang hilang dinilai salah, bukan otomatis error validasi.

Respons submission: `id, assessment, assessment_title, user, user_username,
status, content, score, feedback, submitted_at, is_passed, created_at, updated_at`.
Jangan polling: belum ada endpoint GET submission. Jangan retry otomatis POST
ketika timeout karena request sebelumnya mungkin sudah tersimpan.
Skor dinilai di server; `max_score` dibaca dari detail assessment.

```json
{"answer":"jawaban checkpoint"}
```

Checkpoint membandingkan string setelah trim dan casefold; bukan penilaian AI.
Nilai salah tetap HTTP 200 dengan `correct:false`.

```json
{"competency_id":3,"submission_id":12,"github_url":"https://github.com/example/project","demo_url":"","file_url":"","notes":"Bukti proyek"}
```

Hanya competency_id wajib. submission_id opsional/null; harus milik user,
lulus, completed, dan sesuai competency. Jika dihilangkan backend memilih
submission lulus terbaik. Credential issued yang sudah ada dikembalikan lagi
dengan HTTP 201, sehingga status 201 tidak selalu berarti record baru.
URL publik frontend harus berbentuk `/verify/{uuid}`. Set `PUBLIC_WEB_URL` di backend;
jika kosong, verification_url mengarah ke API JSON.

Verifikasi dapat HTTP 200 namun `is_valid:false`. Perlakukan status revoked,
`proof_missing`, `hash_mismatch_or_unconfirmed`, dan `verified` secara berbeda;
HTTP 404 untuk UUID tidak ditemukan. Respons publik tidak mengekspos student_email.

## Error dan tampilan client

Belum ada envelope error tunggal. Tangani semuanya:

```json
{"detail":"Pesan kegagalan"}
```

```json
{"password_confirm":["Passwords do not match."],"non_field_errors":["..."]}
```

- 400: error field atau aturan bisnis; tampilkan dekat input atau di ringkasan form.
- 401: kredensial/token salah atau tidak ada; alur refresh sesuai bagian sesi.
- 403: izin/CSRF; jangan mengulang refresh terus-menerus.
- 404: record tidak ditemukan, bukan milik user, atau belum ada diagnostic.
- 5xx/network/timeout: pertahankan input; jangan berasumsi body selalu JSON.
  Error provider AI belum diterjemahkan ke kontrak 503 yang konsisten.
- Loading, hasil kosong, dan error harus dibedakan. Kosong pada diagnostic GET
  juga bisa berarti track tidak ditemukan/tidak aktif (query list mengembalikan []).
- Semua skor/feedback dianggap data server; render teks aman, jangan HTML mentah.
- Kunci `grading_config`, `correct_answer`, dan `checkpoint_answer` tidak boleh
  dikirim sebagai bagian data frontend atau diambil langsung dari paket kurikulum.

## Gap backend dan kriteria penerimaan

Perubahan berikut adalah backlog, belum diimplementasikan dalam Fase 0.

| ID / prioritas | Temuan dan sumber | Dampak / kriteria selesai |
|---|---|---|
| G1 / sebelum hasil diagnostic | `assessments/diagnostic_views.py`: latest memakai get_object_or_404(queryset), yang menjalankan get(), bukan first() | Dua attempt memicu MultipleObjectsReturned; pilih terbaru dengan urutan deterministik; 0→404, 1/2+→200 terbaru; uji isolasi user/track |
| G2 / sebelum hasil assessment persisten | `assessments/urls.py`: tidak ada GET submission | Tambahkan list/detail milik user; refresh halaman dapat memuat hasil; user lain mendapat 404 |
| G3 / sebelum badge selesai belajar | `learning/serializers.py`: progress hanya jumlah completed lesson, tanpa ID; checkpoint tidak persisten | Ekspos completed lesson IDs/status per user; UI tidak menebak completion dari mastery; tentukan apakah checkpoint perlu disimpan |
| G4 / sebelum UI eligibility | `credentials/urls.py`: eligibility hanya service internal | Tambahkan endpoint read-only dengan eligible, alasan, kebutuhan yang belum terpenuhi; jangan mencoba issue hanya untuk mengecek |
| G5 / sebelum credential final | `credentials/services.py`: rata-rata >=70 + satu assessment lulus; lesson bisa memberi 70 mastery | Tetapkan skill wajib dan evidence lulus per skill; draft/mock tidak menerbitkan credential final; uji jalur penolakan |
| G6 / sebelum label penguasaan | `learning/services.py`: roadmap satisfied >=70, learning-path mastered >=85 | Satukan kebijakan atau beri arti status yang berbeda secara eksplisit; uji 69.9/70/84.9/85; aktivitas membaca bukan bukti assessment |
| G7 / sebelum mode demo/final | `curriculum/importer.py` hanya memperingatkan draft; serializer submission/proof tidak mengirim provider/review status | Ekspos provenance yang stabil, termasuk fallback; UI bisa membedakan mock/live/draft tanpa menebak dari tx hash atau feedback |
| G8 / sebelum halaman standar | Serializer katalog tidak mengekspos learning_outcomes, observable_behaviors, versi; verifikasi publik tidak memuat snapshot standar | Ekspos field publik yang diperlukan; recruiter melihat versi dan kriteria saat penerbitan, bukan standar terbaru |
| G9 / sebelum submit provider nyata | Submission bebas, sinkron, tanpa idempotency dan error provider konsisten | Validasi evidence per tipe; normalkan failure; retry tidak membuat submission/XP ganda; GET hasil untuk recovery |
| G10 / sebelum generated API client | learning-path filter tidak dianotasi; checkpoint 200 tidak memiliki response schema; JSONField questions/skill_scores masih generik | Lengkapi OpenAPI dan error utama; cocokkan generated types dengan respons runtime |

Tambahan: AI skill-gap HTTP endpoint hanya menerima career_track_id walaupun
service internal mendukung target lebih sempit. Roadmap sudah mendukung skill
dan competency sehingga fitur AI ini bukan blocker alur utama frontend.
Status `locked` saat ini ditampilkan oleh learning-path; endpoint completion/
submission tidak menggunakannya sebagai kontrol akses prasyarat.

## Uji dan keputusan handoff

Jalankan `check_api_contract.py` sesuai README. Probe memeriksa auth/refresh,
envelope pagination, ID/slug routing, roadmap invalid target, kerahasiaan grading,
penolakan client score, kuis sinkron, serta latest diagnostic sebelum/sesudah
dua attempt. Data dibuat di SQLite in-memory. OpenAPI dihasilkan ulang dari kode,
tanpa snapshot besar yang mudah basi.

Fase 1 auth dan fondasi UI dapat dimulai memakai kontrak ini. G1/G2/G3/G4 perlu
diselesaikan sebelum alur hasil dan progress dinyatakan lengkap; G5/G7/G8 sebelum
credential final ditampilkan. Tidak ada klaim bahwa frontend penuh atau deployment
sudah diuji. Provider nyata dan browser belum diuji dalam audit ini.
