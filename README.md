# Progressio

> **Turning Progress Into Proof.**
> Progressio is an AI-powered platform for turning progress into clear, measurable proof.

The repository contains a Next.js web client, a Django API, and a Flutter mobile client. Local demo credentials remain drafts; the mock runtime does not prove final credential validity or external blockchain anchoring. See [the demo runbook](docs/demo-runbook.md) for a disposable local rehearsal.

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
├── front-end/       # Next.js web client and browser-flow tests
├── Mobile/          # Flutter mobile client
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

Gunakan Python 3.12 dan virtualenv baru agar dependency backend terpasang
terisolasi dari Python sistem (PowerShell dari root repo):

```powershell
# Bootstrap sekali; .venv berada di back-end/ dan tidak perlu di-commit
python -m venv back-end/.venv
back-end/.venv/Scripts/python.exe -m pip install -r back-end/requirements.txt
$python = (Resolve-Path "back-end/.venv/Scripts/python.exe").Path
$env:APP_ENV = "local"
$env:DB_ENGINE = "sqlite"
$env:AI_PROVIDER = "mock"
$env:BLOCKCHAIN_PROVIDER = "mock"

# Backend dan pemeriksaan model/schema
Push-Location back-end
try {
    & $python manage.py test
    if ($LASTEXITCODE -ne 0) { throw "Django tests failed ($LASTEXITCODE)" }
    & $python manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw "Migration check failed ($LASTEXITCODE)" }
    $openapi = [System.IO.Path]::GetTempFileName()
    try {
        & $python manage.py spectacular --fail-on-warn --file $openapi
        if ($LASTEXITCODE -ne 0) { throw "OpenAPI validation failed ($LASTEXITCODE)" }
    } finally {
        Remove-Item $openapi -ErrorAction SilentlyContinue
    }
} finally {
    Pop-Location
}

# API probe and curriculum checks run from the repository root.
& $python front-end/check_api_contract.py
if ($LASTEXITCODE -ne 0) { throw "API contract probe failed ($LASTEXITCODE)" }
python -m unittest discover -s curriculum -t .
if ($LASTEXITCODE -ne 0) { throw "Curriculum tests failed ($LASTEXITCODE)" }

# Web (Node minimal 20.19 sesuai package.json)
cd front-end
npm ci
npm test
npm run build
```

`APP_ENV` wajib dipilih eksplisit (`local` atau `production`) agar Django tidak
menjalankan konfigurasi development secara diam-diam. Di POSIX, interpreter venv
adalah `back-end/.venv/bin/python`; set `APP_ENV=local` sebelum menjalankan
command di atas. Tetapkan
`AI_PROVIDER=mock` dan `BLOCKCHAIN_PROVIDER=mock` untuk menjalankan pemeriksaan
lokal tanpa provider eksternal. Probe kontrak memakai database SQLite in-memory
dan identitas sementara; tidak memerlukan token atau layanan eksternal. Workflow
web berjalan saat frontend, backend, kurikulum, atau workflow-nya berubah.

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

# Profil wajib untuk command Django lokal (atau salin .env.example ke .env)
$env:APP_ENV = "local"

# Jalankan migrations
python manage.py migrate

# Jalankan tests
python manage.py test

# Jalankan dev server
python manage.py runserver
```

`APP_ENV` wajib bernilai `local` atau `production`; profil local ditujukan untuk
development. Untuk deployment, lihat
[`docker-compose.hosted.yml`](docker-compose.hosted.yml) dan
[`back-end/.env.production.example`](back-end/.env.production.example). Isi
variabel dari contoh melalui secret manager sebelum menjalankan hosted stack.
Jalankan migrasi setelah stack aktif:

```sh
docker compose -f docker-compose.hosted.yml exec backend python manage.py migrate
```

---

## 📡 API Endpoints (Sprint 1)

Semua endpoint domain berada di bawah `/api/v1/`:

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Register user baru (`student` atau `recruiter`; admin tidak dapat dipilih publik) |
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
> Profil lokal menggunakan `django.core.mail.backends.console.EmailBackend` (isi email dicetak ke console). Email nonaktif secara default pada profil production. Jika fitur mulai mengirim email, aktifkan `ENABLE_EMAIL=True` dan konfigurasi SMTP host, username, password, serta alamat pengirim sebelum memakai fitur tersebut.

> [!NOTE]
> **Celery & Background Tasks:**
> Celery + Redis broker akan diintegrasikan pada Sprint berikutnya saat implementasi AI evaluation, Blockchain transaction, dan notifikasi otomatis.
