# Progressio

> **Turning Progress Into Proof.**
> Progressio is an AI-powered platform for turning progress into clear, measurable proof.

The hackathon MVP backend now supports an end-to-end vertical slice: server-graded diagnostic assessment, personalized skill graph, secure assessment scoring, evidence-backed credential issuance, cryptographic integrity anchoring, and public recruiter verification. Run `python manage.py import_curriculum` from `back-end/` to project the curriculum package into the database, or `python manage.py seed_demo` to do that and add demo accounts.

---

## 📁 Struktur Repo

```text
Progressio/
├── curriculum/      # Standar penilaian — SUMBER KEBENARAN, bukan turunan
│   ├── validator.py #   validator tanpa dependency, dipakai CI dan backend
│   ├── schemas/     #   kontrak tiap entitas (JSON Schema)
│   ├── tests/       #   suite validasi + fixture valid & invalid
│   └── tracks/      #   satu folder per career track
├── back-end/        # Django 5.1 + DRF — mesin yang mengukur
├── front-end/       # (belum diisi)
├── Mobile/          # (belum diisi)
└── docker-compose.yml
```

Aturan penting: **kurikulum adalah sumber kebenaran, database hanya proyeksinya.**
Track, competency, skill, lesson, dan assessment diisi lewat `import_curriculum`,
bukan lewat Django admin — perubahan manual akan tertimpa saat impor berikutnya.
Lihat [curriculum/README.md](curriculum/README.md).

---

## 🏗️ Backend Overview

Backend dibangun menggunakan **Django 5.1** + **Django REST Framework (DRF)** dengan dokumentasi **OpenAPI 3.0 (drf-spectacular)** dan database **PostgreSQL 15**.

### Django Apps Structure
```text
back-end/
├── apps/
│   ├── accounts/        # Custom User model (role: student, recruiter, admin), JWT Auth
│   ├── curriculum/      # Importer paket kurikulum -> model Django
│   ├── careers/         # CareerTrack model & API
│   ├── competencies/    # Competency, CompetencyPrerequisite & API
│   ├── skills/          # Skill, SkillPrerequisite (Skill Graph) & API
│   ├── learning/        # Lesson, StudyStep, progress, roadmap & API
│   ├── assessments/     # Assessment, Submission, Diagnostic & grading server-side
│   ├── credentials/     # Credential, Evidence, aturan kelayakan
│   ├── blockchain/      # Hash SHA-256 kanonik + anchoring proof
│   ├── verification/    # Verifikasi publik tanpa auth
│   ├── ai/              # Adapter AI (mock | openai)
│   └── common/          # TimestampMixin, HealthCheck API, seed_demo
├── config/              # Core settings, JWT, OpenAPI, and routing
└── Dockerfile           # Python 3.12 slim backend container
```

---

## 🧪 Menjalankan Test

```powershell
# Kurikulum (tanpa dependency, dari root repo)
python -m unittest discover -s curriculum -t .

# Backend
cd back-end
python manage.py test
```

---

## 🚀 Cara Menjalankan

### Opsi 1: Menggunakan Docker (Rekomendasi)
Dari root folder `Progressio/`:
```powershell
# Build dan jalankan seluruh service (PostgreSQL + Django Backend)
docker compose up --build -d

# Cek logs
docker compose logs -f backend

# Jalankan migration database
docker compose exec backend python manage.py migrate

# Jalankan unit tests
docker compose exec backend python manage.py test
```

Akses aplikasi:
- 📑 **Swagger UI (OpenAPI 3.0)**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- 📖 **Redoc UI**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- 🩺 **Health Check**: [http://localhost:8000/api/v1/health/](http://localhost:8000/api/v1/health/)
- 📄 **OpenAPI Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

---

### Opsi 2: Lokal / Native Python (Virtualenv)
Dari folder `back-end/`:
```powershell
cd back-end

# Aktifkan virtual environment
.\.venv\Scripts\activate

# Jalankan migrations
python manage.py migrate

# Jalankan tests
python manage.py test

# Jalankan dev server
python manage.py runserver
```

---

## 📡 API Endpoints (Sprint 1)

Semua endpoint domain berada di bawah `/api/v1/`:

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Register user baru (`student`, `recruiter`, `admin`) |
| `POST` | `/api/v1/auth/login` | Public | JWT Token obtain (`access` & `refresh`) |
| `POST` | `/api/v1/auth/refresh` | Public | JWT Token refresh |
| `GET` | `/api/v1/auth/me` | Bearer JWT | Profile user yang sedang login |
| `GET` | `/api/v1/career-tracks` | Public | List semua career track aktif |
| `GET` | `/api/v1/career-tracks/{id}` | Public | Detail career track & jumlah competency |
| `GET` | `/api/v1/competencies` | Public | List competency (bisa filter `?career_track={id}`) |
| `GET` | `/api/v1/competencies/{id}` | Public | Detail competency & jumlah skill |
| `GET` | `/api/v1/skills` | Public | List skill (bisa filter `?competency={id}`) |
| `GET` | `/api/v1/skills/{id}` | Public | Detail skill beserta prerequisite skill graph |
| `GET` | `/api/v1/skills/{id}/lessons` | Public | List materi/lesson untuk skill tertentu |
| `GET` | `/api/v1/lessons` | Public | List lesson (bisa filter `?skill={id}`) |
| `GET` | `/api/v1/lessons/{id}` | Public | Detail lesson |
| `GET` | `/api/v1/health/` | Public | Status health check API |
| `GET` | `/api/v1/learning-path?career_track={slug}` | Bearer JWT | Peta skill + status (mastered/available/locked) |
| `GET` | `/api/v1/roadmap?skill={slug}` | Bearer JWT | Rute terurut ke target pilihan user + sisa jam |
| `GET` | `/api/v1/skills/{slug}/study-plan` | Public | Study step: bagian mana yang dibaca dan apa yang dikerjakan |
| `POST` | `/api/v1/study-steps/{id}/checkpoint` | Bearer JWT | Cek jawaban checkpoint (dinilai server-side) |

---

## 📝 Catatan Penting & Roadmap

> [!IMPORTANT]
> **Email Backend:**
> Saat ini backend menggunakan `django.core.mail.backends.console.EmailBackend` untuk keperluan development (isi email akan dicetak ke console/log server). **Wajib diganti ke SMTP Provider production (seperti SendGrid, AWS SES, Mailgun) sebelum deployment live.**

> [!NOTE]
> **Celery & Background Tasks:**
> Celery + Redis broker akan diintegrasikan pada Sprint berikutnya saat implementasi AI evaluation, Blockchain transaction, dan notifikasi otomatis.
