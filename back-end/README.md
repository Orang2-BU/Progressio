# Progressio Backend Service

> **Turning Progress Into Proof.**
> Backend architecture for the Progressio MVP built with **Django 5.1**, **Django REST Framework**, **OpenAPI 3.0 (drf-spectacular)**, and **PostgreSQL 15**.

---

## 🧭 Project Status & Sprint Roadmap

Berdasarkan spesifikasi teknis di `progressio-backend-spec.md`, berikut roadmap pengerjaan backend:

```
[x] Sprint 1: Backend Foundation (SELESAI)
 │
 ├──▶ [ ] Sprint 2: Learning Engine & Progress Tracking (NEXT)
 │     │
 │     └──▶ [ ] Sprint 3: Credential System & Verification
 │           │
 │           └──▶ [ ] Sprint 4: External Services (AI, Blockchain, Celery)
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

### ⏳ Sprint 2 — Learning Engine & Progress Tracking (Status: UPCOMING)
Fokus pada sistem penilaian, submission, perhitungan progress, dan XP user:

1. **Assessments & Submissions** (`apps/assessments/`):
   - Model `Assessment` (Types: `quiz`, `challenge`, `project`, passing score, max score).
   - Model `Submission` (State Machine: `draft` ➔ `submitted` ➔ `evaluating` ➔ `completed`).
   - Endpoints:
     - `GET /api/v1/assessments` & `GET /api/v1/assessments/{id}`
     - `POST /api/v1/assessments/{id}/submit`
2. **Progress & XP Tracking** (`apps/learning/`):
   - Model `SkillProgress` (`user`, `skill`, `mastery`, `xp`, `confidence`, `last_assessed_at`).
   - Model `CompetencyProgress` (`user`, `competency`, `score`, `confidence`, `last_updated`).
   - Endpoints:
     - `GET /api/v1/learning-path` (rekomendasi path belajar berdasarkan graph skill)
     - `GET /api/v1/progress` (overview progress belajar dan XP user)
     - `POST /api/v1/lesson/{id}/complete` (trigger event: `LessonCompleted` ➔ tambah XP & recalculate)
3. **Domain Event Handlers**:
   - `LessonCompleted`: Update XP & Skill Progress.
   - `AssessmentPassed`: Update Skill Progress & Competency Score, check eligibility credential.

---

### ⏳ Sprint 3 — Credential System & Verification (Status: UPCOMING)
Fokus pada penerbitan sertifikat kompetensi dan verifikasi publik:

1. **Credentials & Evidence** (`apps/credentials/`):
   - Model `Credential` (`user`, `competency`, status: `draft`, `issued`, `revoked`, score, `issued_at`).
   - Model `Evidence` (`submission`, `github_url`, `file_url`, `demo_url`, notes portofolio).
   - Endpoints:
     - `GET /api/v1/credentials` (list credential milik user)
     - `GET /api/v1/credentials/{id}` (detail credential)
     - `POST /api/v1/credentials/issue` (issue credential baru jika passing score tercapai)
2. **Public Verification API** (`apps/verification/`):
   - `GET /api/v1/verify/{credential_id}`: **Public endpoint (tanpa autentikasi)** agar recruiter/perusahaan bisa memvalidasi keaslian sertifikat & portofolio kandidat.
3. **Credential Generator**:
   - Engine generate snapshot metadata JSON & persiapan payload PDF/Hash.

---

### ⏳ Sprint 4 — External Services & Background Workers (Status: UPCOMING)
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
