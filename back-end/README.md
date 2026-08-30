# Progressio Backend Service

> **Turning Progress Into Proof.**
> Backend architecture for the Progressio MVP built with **Django 5.1**, **Django REST Framework**, **OpenAPI 3.0 (drf-spectacular)**, and **PostgreSQL 15**.

---

## 🧭 Project Status & Sprint Roadmap

Berdasarkan spesifikasi teknis di `progressio-backend-spec.md`, berikut roadmap pengerjaan backend:

```
[x] Sprint 1: Backend Foundation (SELESAI)
 │
 ├──▶ [x] Sprint 2: Learning Engine & Progress Tracking (SELESAI)
 │     │
 │     └──▶ [x] Sprint 3: Credential System & Verification (SELESAI)
 │           │
 │           └──▶ [ ] Sprint 4: External Services (AI, Blockchain, Celery) (NEXT)
```

---

### ✅ Sprint 1 — Backend Foundation (Status: SELESAI)
- [x] **Authentication & Role System** (`apps/accounts`): Custom `User` model (`student`, `recruiter`, `admin`), JWT Auth (`/register`, `/login`, `/refresh`, `/me`).
- [x] **Career Tracks** (`apps/careers`): Model `CareerTrack` & CRUD endpoints.
- [x] **Competencies** (`apps/competencies`): Model `Competency` & filtering per career track.
- [x] **Skill Graph** (`apps/skills`): Model `Skill`, `SkillPrerequisite` (graph prasyarat), & endpoint materi per skill.
- [x] **Learning Base** (`apps/learning`): Model `Lesson` (`video`, `article`, `exercise`, `reading`).
- [x] **Database & OpenAPI**: PostgreSQL 15 + Swagger UI / Redoc + 34 unit tests lolos 100%.

---

### ✅ Sprint 2 — Learning Engine & Progress Tracking (Status: SELESAI)
- [x] **Assessments & Submissions** (`apps/assessments/`):
  - Model `Assessment` (`quiz`, `challenge`, `project`, passing score, max score).
  - Model `Submission` (State Machine: `draft` ➔ `submitted` ➔ `evaluating` ➔ `completed`).
  - Endpoints: `GET /api/v1/assessments`, `GET /api/v1/assessments/{id}`, `POST /api/v1/assessments/{id}/submit`.
- [x] **Progress & XP Tracking** (`apps/learning/`):
  - Model `SkillProgress` (`user`, `skill`, `mastery`, `xp`, `confidence`, `last_assessed_at`).
  - Model `CompetencyProgress` (`user`, `competency`, `score`, `confidence`, `last_updated`).
  - Model `LessonCompletion` (`user`, `lesson`, `completed_at`).
  - Endpoints:
    - `GET /api/v1/learning-path` (algoritma graph prerequisite skill: `locked`, `available`, `in_progress`, `mastered`).
    - `GET /api/v1/progress` (overview total XP, completed lessons, skill & competency progresses).
    - `POST /api/v1/lesson/{id}/complete` (trigger event: `LessonCompleted` ➔ +50 XP & update mastery).
- [x] **Domain Event Handlers**:
  - `LessonCompleted`: Auto award XP & recalculate skill mastery.
  - `AssessmentPassed`: Auto update skill mastery (up to 100%), +100 XP, dan sinkronisasi skor rata-rata competency.
- [x] **Testing & Docs**: 38/38 unit tests lolos 100% di PostgreSQL container.

---

### ✅ Sprint 3 — Credential System & Verification (Status: SELESAI)
- [x] **Credentials & Evidence** (`apps/credentials/`):
  - Model `Credential` (`UUID id`, `user`, `competency`, status: `draft`, `issued`, `revoked`, `score`, `issued_at`, snapshot metadata).
  - Model `Evidence` (`credential`, `submission`, `github_url`, `file_url`, `demo_url`, `notes`).
  - `CredentialService`: Validasi kelayakan penerbitan (skor minimal 70%), issuance credential, dan snapshot packaging.
  - Endpoints:
    - `GET /api/v1/credentials` (list credential milik user yang login).
    - `GET /api/v1/credentials/{id}` (detail credential & bukti portofolio).
    - `POST /api/v1/credentials/issue` (issue credential baru dengan attaching evidence).
- [x] **Public Verification API** (`apps/verification/`):
  - `GET /api/v1/verify/{credential_id}`: **Public endpoint (tanpa login)** untuk recruiter/perusahaan memvalidasi keaslian sertifikat & portfolio evidence.
- [x] **Testing & Docs**: 44/44 unit tests lolos 100% di PostgreSQL container.

---

### ⏳ Sprint 4 — External Services & Background Workers (Status: NEXT)
Fokus pada integrasi AI, Blockchain, task async, dan production infra:

1. **Background Tasks with Celery & Redis**:
   - Menambahkan container **Redis** sebagai message broker.
   - Setup **Celery worker** untuk pekerjaan async: AI Evaluation, PDF Generation, Blockchain Minting, Notifikasi.
2. **AI Integration Adapter** (`apps/ai/`):
   - Clean Architecture: View ➔ Service Layer ➔ AI Adapter ➔ LLM API.
   - AI Skill Gap Analysis, Learning Path Recommendations, Automated Assessment Evaluation.
3. **Blockchain Integration Layer** (`apps/blockchain/`):
   - Model `BlockchainCredential` (`credential_hash`, `transaction_hash`, `network`, `verified`, `revoked`).
   - Hashing SHA-256 (hanya menyimpan hash pembuktian, *bukan* data pribadi siswa).
   - Adapter untuk interaksi dengan smart contract / blockchain node.
4. **Production Email & Notifications**:
   - Mengganti `django.core.mail.backends.console.EmailBackend` dengan SMTP Provider (SendGrid/AWS SES/Resend).

---

## 🛠️ Panduan Menjalankan Backend

### Prasyarat
- Docker Desktop aktif (atau Python 3.12 + PostgreSQL lokal).

### 1. Jalankan Menggunakan Docker (Rekomendasi)
Dari root folder `Progressio/`:
```powershell
# Jalankan seluruh service (PostgreSQL & Backend)
docker compose up -d

# Jalankan migrasi database
docker compose exec backend python manage.py migrate

# Jalankan seluruh unit testing (34 tests)
docker compose exec backend python manage.py test

# Cek logs real-time
docker compose logs -f backend
```

### 2. Jalankan Lokal (Native Python)
Dari folder `back-end/`:
```powershell
# Masuk folder & aktifkan virtualenv
cd back-end
.\.venv\Scripts\activate

# Install dependensi
pip install -r requirements.txt

# Jalankan migrasi & testing
python manage.py migrate
python manage.py test

# Jalankan server lokal
python manage.py runserver
```

---

## 📖 Dokumentasi API Live

Saat backend berjalan:
- 📑 **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- 📖 **Redoc UI**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- 🩺 **Health Check**: [http://localhost:8000/api/v1/health/](http://localhost:8000/api/v1/health/)
- 📄 **OpenAPI 3.0 Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

---

## 🏛️ Struktur Arsitektur Bersih (Clean Architecture)

```text
back-end/
├── apps/
│   ├── accounts/        # User, Roles, JWT Auth
│   ├── careers/         # Career Tracks
│   ├── competencies/    # Competencies
│   ├── skills/          # Skills & Skill Graph Prerequisites
│   ├── learning/        # Lessons, Learning Path & Progress
│   ├── assessments/     # Assessments & Submissions (Sprint 2)
│   ├── credentials/     # Credentials & Evidence (Sprint 3)
│   ├── verification/    # Public Verification API (Sprint 3)
│   ├── ai/              # AI Service Adapters (Sprint 4)
│   ├── blockchain/      # Blockchain Proof Adapters (Sprint 4)
│   └── common/          # TimestampMixin, Health Check, Shared Utils
├── config/              # Django settings, JWT, URLs, WSGI/ASGI
├── Dockerfile           # Python 3.12 slim container
└── requirements.txt     # Python dependencies
```
