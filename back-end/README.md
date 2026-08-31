# Progressio Backend Service

> **Turning Progress Into Proof.**
> Hackathon MVP backend architecture for the Progressio platform built with **Django 5.1**, **Django REST Framework**, **OpenAPI 3.0 (drf-spectacular)**, **PostgreSQL 15**, **Redis 7**, **Celery 5**, an **AI integration layer**, and **cryptographic credential proofs**.

## Current MVP behavior

- Diagnostic questions and answer keys are stored server-side. Submissions update the student's skill graph without awarding artificial XP.
- Quiz scores are calculated from private server-side answer keys. Clients cannot submit or override a score.
- Coding challenges can use `AI_PROVIDER=openai` through the OpenAI Responses API, or the explicit deterministic `mock` provider for offline demos.
- Credentials require both a competency score of at least 70 and a completed passing assessment.
- A credential is marked `issued` only after its SHA-256 proof is anchored successfully.
- Public verification recomputes the credential hash, checks provider confirmation, and checks revocation status.
- `BLOCKCHAIN_PROVIDER=mock` is an offline development simulator. Use `BLOCKCHAIN_PROVIDER=http` with an external on-chain signer service for a real network integration.

The mock providers are intentionally labeled development behavior and must not be presented as live OpenAI or blockchain transactions.

## Demo setup

```powershell
# Native Python (from back-end/)
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
$env:DB_ENGINE = "sqlite"
python manage.py migrate
python manage.py seed_demo
python manage.py test
python manage.py runserver
```

`seed_demo` is idempotent and creates one Backend Engineering track, four skills, eight diagnostic questions, lessons, prerequisites, and one JWT/RBAC coding challenge.

New MVP endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/v1/diagnostics/{career_track_id}` | Get diagnostic questions without answer keys |
| `POST` | `/api/v1/diagnostics/{career_track_id}/submit` | Server-grade diagnostic answers |
| `GET` | `/api/v1/diagnostics/latest?career_track={id}` | Get the student's latest diagnostic result |
| `POST` | `/api/v1/assessments/{id}/submit` | Server-grade a quiz or evaluate a challenge |
| `POST` | `/api/v1/credentials/issue` | Issue only after eligible progress and a passing submission |
| `GET` | `/api/v1/verify/{credential_id}` | Public status and cryptographic integrity verification |

---

## 🧭 Project Status & Sprint Roadmap (MVP FOUNDATION IMPLEMENTED)

```
[x] Sprint 1: Backend Foundation (SELESAI)
 │
 ├──▶ [x] Sprint 2: Learning Engine & Progress Tracking (SELESAI)
 │     │
 │     └──▶ [x] Sprint 3: Credential System & Verification (SELESAI)
 │           │
 │           └──▶ [x] Sprint 4: External-service adapters, Celery + Redis (MVP)
```

---

### ✅ Sprint 1 — Backend Foundation
- [x] **Authentication & Role System** (`apps/accounts`): Custom `User` model (`student`, `recruiter`, `admin`), JWT Auth (`/register`, `/login`, `/refresh`, `/me`).
- [x] **Career Tracks** (`apps/careers`): Model `CareerTrack` & CRUD endpoints.
- [x] **Competencies** (`apps/competencies`): Model `Competency` & filtering per career track.
- [x] **Skill Graph** (`apps/skills`): Model `Skill`, `SkillPrerequisite` (graph prasyarat), & endpoint materi per skill.
- [x] **Learning Base** (`apps/learning`): Model `Lesson` (`video`, `article`, `exercise`, `reading`).
- [x] **Database & OpenAPI**: PostgreSQL 15 + Swagger UI / Redoc.

---

### ✅ Sprint 2 — Learning Engine & Progress Tracking
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

---

### ✅ Sprint 3 — Credential System & Verification
- [x] **Credentials & Evidence** (`apps/credentials/`):
  - Model `Credential` (`UUID id`, `user`, `competency`, status: `draft`, `issued`, `revoked`, `score`, `issued_at`, snapshot metadata).
  - Model `Evidence` (`credential`, `submission`, `github_url`, `file_url`, `demo_url`, `notes`).
  - `CredentialService`: Validasi kelayakan penerbitan (skor minimal $\ge 70\%$), issuance credential, dan snapshot packaging.
  - Endpoints:
    - `GET /api/v1/credentials` (list credential milik user yang login).
    - `GET /api/v1/credentials/{id}` (detail credential & bukti portofolio).
    - `POST /api/v1/credentials/issue` (issue credential baru dengan attaching evidence).
- [x] **Public Verification API** (`apps/verification/`):
  - `GET /api/v1/verify/{credential_id}`: **Public endpoint (tanpa login)** untuk recruiter/perusahaan memvalidasi keaslian sertifikat & portfolio evidence.

---

### ✅ Sprint 4 — External Services & Background Workers
- [x] **Background Tasks with Celery & Redis**:
  - Container **Redis 7 Alpine** (`progressio_redis`) sebagai message broker.
  - Container **Celery Worker** (`progressio_celery_worker`) untuk background job async.
- [x] **AI Integration Layer** (`apps/ai/`):
  - Clean Architecture: `View ➔ Service ➔ AI Adapter ➔ Provider`.
  - Built-in `MockAIAdapter` (untuk testing & dev offline) + `OpenAIAdapter` (live via `OPENAI_API_KEY`).
  - Endpoints:
    - `POST /api/v1/ai/skill-gap-analysis` (analisis gap kompetensi vs Career Track target).
    - `GET /api/v1/ai/recommendations` (rekomendasi belajar personal).
    - Background task evaluasi asesmen otomatis.
- [x] **Blockchain Integration Layer** (`apps/blockchain/`; mock locally, external signer required for a live chain):
  - Model `BlockchainCredential` (`credential_hash` SHA-256, `transaction_hash`, `network`, `verified`, `revoked`).
  - Privacy by Design: **Hanya hash SHA-256 yang disimpan on-chain** (tidak ada PII / data pribadi siswa).
  - Terintegrasi langsung dengan Public Verification API `/api/v1/verify/{id}`.
- [x] **Testing & Docs**: automated Django test suite covering the MVP flow. Run it in your environment before every commit.

---

## 🛠️ Panduan Menjalankan Backend (Docker)

Dari root folder `Progressio/`:
```powershell
# Build dan jalankan seluruh 4 service (Postgres, Redis, Django Backend, Celery Worker)
docker compose up --build -d

# Cek logs worker atau backend
docker compose logs -f celery_worker
docker compose logs -f backend

# Jalankan migrasi database
docker compose exec backend python manage.py migrate

# Jalankan seluruh unit testing (51 tests)
docker compose exec backend python manage.py test
```

---

## 📖 Dokumentasi API Live

- 📑 **Swagger UI (Interactive)**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- 📖 **Redoc UI**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- 🩺 **Health Check**: [http://localhost:8000/api/v1/health/](http://localhost:8000/api/v1/health/)
- 📄 **OpenAPI 3.0 Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)
