# Progressio

> **Turning Progress Into Proof.**
> Progressio is an AI-powered platform for turning progress into clear, measurable proof.

---

## 🏗️ System Architecture & Backend Overview

Backend dibangun menggunakan **Django 5.1** + **Django REST Framework (DRF)** dengan dokumentasi **OpenAPI 3.0 (drf-spectacular)** dan database **PostgreSQL 15**.

### Django Apps Structure
```text
back-end/
├── apps/
│   ├── accounts/        # Custom User model (role: student, recruiter, admin), JWT Auth
│   ├── careers/         # CareerTrack model & API
│   ├── competencies/    # Competency model & API (filterable by career_track)
│   ├── skills/          # Skill, SkillPrerequisite (Skill Graph) & API
│   ├── learning/        # Lesson model & API (filterable by skill)
│   └── common/          # TimestampMixin, HealthCheck API, shared utils
├── config/              # Core settings, JWT, OpenAPI, and routing
└── Dockerfile           # Python 3.12 slim backend container
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

---

## 📝 Catatan Penting & Roadmap

> [!IMPORTANT]
> **Email Backend:**
> Saat ini backend menggunakan `django.core.mail.backends.console.EmailBackend` untuk keperluan development (isi email akan dicetak ke console/log server). **Wajib diganti ke SMTP Provider production (seperti SendGrid, AWS SES, Mailgun) sebelum deployment live.**

> [!NOTE]
> **Celery & Background Tasks:**
> Celery + Redis broker akan diintegrasikan pada Sprint berikutnya saat implementasi AI evaluation, Blockchain transaction, dan notifikasi otomatis.
