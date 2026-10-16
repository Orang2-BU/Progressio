# Progressio

> **Turning Progress Into Proof.**

Progressio adalah platform yang mengubah progres belajar menjadi bukti yang terukur dan bisa diverifikasi. Pengguna (student) mengikuti jalur karier, menjawab diagnostic, belajar materi per skill, mengerjakan assessment, lalu — jika memenuhi syarat — mendapatkan **credential** yang bisa diverifikasi publik lewat hash SHA-256.

Aturan intinya: **kurikulum adalah sumber kebenaran, database hanya proyeksinya.** Penilaian (skor, kunci jawaban, rubrik) dijalankan di server, bukan di klien.

> ⚠️ **Status: MVP hackathon.** Mode `mock` untuk AI dan blockchain hanya simulasi offline untuk demo. Credential dari mode mock belum menjadi bukti valid secara eksternal, dan belum ada anchoring blockchain sungguhan.

---

## 📑 Daftar Isi

- [Fitur](#-fitur)
- [Struktur Repo](#-struktur-repo)
- [Tech Stack](#-tech-stack)
- [Quick Start (Docker)](#-quick-start-docker)
- [Menjalankan Secara Lokal](#-menjalankan-secara-lokal)
- [Menjalankan Test](#-menjalankan-test)
- [Konfigurasi Environment](#-konfigurasi-environment)
- [Dokumentasi Lanjutan](#-dokumentasi-lanjutan)
- [Status & Batasan](#-status--batasan)

---

## ✨ Fitur

- **Career track → competency → skill**: katalog jalur belajar dengan graf prasyarat antar skill.
- **Diagnostic**: soal penempatan dengan kunci jawaban yang disimpan di server.
- **Roadmap & learning path**: urutan skill menuju target yang dipilih, lengkap dengan status *mastered / available / locked* dan estimasi jam belajar.
- **Study**: per skill, pengguna membaca bagian materi tertentu lalu menjawab checkpoint yang dinilai server-side.
- **Assessment**: pengumpulan jawaban dengan penilaian server-side (klien tidak bisa mengubah skor).
- **Credential & verifikasi publik**: credential diterbitkan hanya jika skor kompetensi ≥ 70 *dan* assessment lulus; status `issued` hanya setelah hash proof berhasil di-anchor. Verifikasi publik tersedia tanpa login.
- **Integrasi AI** (opsional): provider `mock`, `groq`, atau HTTP-compatible.

---

## 📁 Struktur Repo

```text
Progressio/
├── curriculum/        # Standar penilaian — SUMBER KEBENARAN
│   ├── validator.py   #   validator tanpa dependency (dipakai CI dan backend)
│   ├── schemas/       #   JSON Schema untuk tiap entitas
│   ├── tests/         #   suite validasi + fixture valid & invalid
│   └── tracks/        #   satu folder per career track (mis. backend-engineering)
├── back-end/          # Django 5.1 + DRF — mesin penilai dan API
├── front-end/         # Web client Next.js (App Router) + browser-flow tests
├── Mobile/            # Client Flutter (masih dalam pengembangan)
├── docs/              # Runbook demo, QA, dan catatan penyelesaian
├── e2e/               # Skenario end-to-end
├── docker-compose.yml         # Stack lokal: PostgreSQL, Redis, backend, Celery
├── docker-compose.demo.yml    # Stack untuk demo
└── docker-compose.hosted.yml  # Stack untuk deployment
```

### Backend apps (`back-end/apps/`)

| App | Tanggung jawab |
|---|---|
| `accounts` | Custom user (role `student`, `recruiter`, `admin`) dan JWT auth |
| `curriculum` | Importer paket kurikulum → model Django |
| `careers` | Career track |
| `competencies` | Competency dan prasyaratnya |
| `skills` | Skill dan skill graph |
| `learning` | Lesson, study step, progres, roadmap |
| `assessments` | Assessment, submission, diagnostic, dan grading server-side |
| `credentials` | Credential, evidence, dan aturan kelayakan |
| `blockchain` | Hash SHA-256 kanonik dan anchoring proof |
| `verification` | Verifikasi publik tanpa auth |
| `ai` | Adapter AI (`mock`, `groq`, `http`) |
| `common` | Utilitas bersama, health check, command `seed_demo` |

> Jangan mengubah track, competency, skill, lesson, atau assessment lewat Django admin. Isi lewat `python manage.py import_curriculum` karena perubahan manual akan tertimpa saat impor berikutnya. Detail ada di [curriculum/README.md](curriculum/README.md).

---

## 🛠️ Tech Stack

| Bagian | Teknologi |
|---|---|
| Backend | Python 3.12, Django 5.2, Django REST Framework, drf-spectacular (OpenAPI 3.0), SimpleJWT |
| Database | PostgreSQL 15 (SQLite untuk demo/test lokal) |
| Async | Celery 5 + Redis 7 |
| Web | Next.js 16 (App Router), React 19, Node.js ≥ 20.19 |
| Mobile | Flutter |
| Container | Docker & Docker Compose |

---

## 🚀 Quick Start (Docker)

Dari root repo:

```bash
docker compose up --build -d

# Jalankan migrasi database
docker compose exec backend python manage.py migrate

# Impor kurikulum ke database
docker compose exec backend python manage.py import_curriculum --help

# Lihat log backend
docker compose logs -f backend
```

Setelah stack aktif:

| Layanan | URL |
|---|---|
| Swagger UI | http://localhost:8000/api/docs/ |
| Redoc | http://localhost:8000/api/redoc/ |
| OpenAPI schema | http://localhost:8000/api/schema/ |
| Health check | http://localhost:8000/api/v1/health/ |

---

## 💻 Menjalankan Secara Lokal

Prasyarat: Python 3.12, Node.js ≥ 20.19. Perintah di bawah untuk PowerShell dari root repo.

### 1. Backend

```powershell
cd back-end
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt

$env:APP_ENV = "local"          # wajib: local atau production
$env:DB_ENGINE = "sqlite"       # atau atur DB_* untuk PostgreSQL
$env:AI_PROVIDER = "mock"
$env:BLOCKCHAIN_PROVIDER = "mock"

python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

### 2. Frontend

```powershell
cd front-end
npm ci
npm run dev
```

Buka http://127.0.0.1:3000. Next.js meneruskan request `/api` ke Django; target-nya diatur lewat `API_PROXY_TARGET` (default `http://127.0.0.1:8000`, lihat [front-end/.env.example](front-end/.env.example)).

### 3. Mobile (opsional)

```bash
cd Mobile
flutter pub get
flutter run
```

### Demo terisolasi

Untuk rehearsal demo dengan database SQLite in-memory yang dibuat ulang setiap kali dijalankan (tidak menyentuh database proyek), ikuti [docs/demo-runbook.md](docs/demo-runbook.md).

---

## 🧪 Menjalankan Test

Test dijalankan di CI (`.github/workflows/`) untuk backend, kurikulum, dan web. Untuk menjalankan secara lokal dengan provider eksternal dimatikan:

```powershell
# Backend (dari back-end/, dengan venv aktif dan env seperti di atas)
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py spectacular --fail-on-warn --file openapi.tmp.yaml

# Kurikulum (dari root repo)
python -m unittest discover -s curriculum -t .

# Web (dari front-end/)
npm test
npm run build
```

| Workflow CI | Cakupan |
|---|---|
| `backend-tests.yml` | Migrasi, test Django (termasuk PostgreSQL 15), validasi OpenAPI, impor kurikulum |
| `curriculum-tests.yml` | Validasi semua paket kurikulum dan fixture |
| `web-tests.yml` | Test dan build web, probe kontrak API |

---

## ⚙️ Konfigurasi Environment

- `APP_ENV` **wajib** diisi eksplisit (`local` atau `production`). Startup gagal jika tidak ada, sehingga konfigurasi development tidak aktif diam-diam.
- Di profil `production`, startup gagal kecuali `SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` (HTTPS), dan `CSRF_TRUSTED_ORIGINS` (HTTPS) sudah diisi.
- Template variabel ada di [`back-end/.env.example`](back-end/.env.example), [`back-end/.env.production.example`](back-end/.env.production.example), dan [`back-end/.env.demo.example`](back-end/.env.demo.example).

> 🔐 Jangan commit file `.env` yang berisi secret. Isi secret production lewat secret manager. Nilai di `docker-compose.yml` hanya untuk development lokal.

---

## 📚 Dokumentasi Lanjutan

- [Backend README](back-end/README.md) — arsitektur backend, konfigurasi hosted, dan throttling ([THROTTLING.md](back-end/THROTTLING.md))
- [Curriculum README](curriculum/README.md) — format paket kurikulum dan aturan validasi
- [Frontend README](front-end/README.md) — status fase pengembangan web dan API contract ([API_CONTRACT.md](front-end/API_CONTRACT.md))
- [Demo runbook](docs/demo-runbook.md) — langkah demo lokal yang terisolasi
- [Progressio backend spec](progressio-backend-spec.md) — spesifikasi backend

---

## 🚧 Status & Batasan

- Web client masih berkembang: katalog, diagnostic, roadmap, study, dan proof sudah ada, tetapi beberapa alur belum lengkap. Lihat [front-end/README.md](front-end/README.md).
- Mobile masih dalam tahap awal (halaman login, register, lupa password, dan OTP).
- Provider `mock` untuk AI dan blockchain hanya untuk pengembangan. Jangan diklaim sebagai transaksi OpenAI atau blockchain sungguhan. Untuk integrasi jaringan nyata, gunakan `BLOCKCHAIN_PROVIDER=http` dengan layanan signer eksternal.
- Email default menggunakan console backend (dicetak ke terminal). Email production dinonaktifkan sampai SMTP dikonfigurasi.
- Celery sudah terpasang di Docker stack, tetapi alur background (evaluasi AI, transaksi blockchain) masih dikembangkan.

---

## 📄 Lisensi

Repo ini belum memiliki file lisensi. Tambahkan `LICENSE` sebelum repo dibagikan secara publik agar penggunaan ulang jelas.
