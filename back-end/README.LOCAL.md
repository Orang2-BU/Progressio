# Local Development Setup - Progressio Backend

## Quick Start (SQLite - No PostgreSQL Required)

### 1. Setup Environment
```powershell
cd back-end

# Copy local env (uses SQLite instead of PostgreSQL)
copy .env.example .env
$env:APP_ENV = "local"

# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies (if not done yet)
pip install -r requirements.txt
```

### 2. Initialize Database
```powershell
# Run migrations
python manage.py migrate

# Import curriculum data
python manage.py import_curriculum

# Create demo accounts (optional)
python manage.py seed_demo
```

### 3. Run Development Server
```powershell
python manage.py runserver
```

Server: http://localhost:8000
API Docs: http://localhost:8000/api/docs/

### 4. Run Tests
```powershell
# Backend tests (SQLite)
python manage.py test

# Or with explicit SQLite
$env:DB_ENGINE = "sqlite"
python manage.py test
```

## Demo Accounts (after seed_demo)
- Student: `demo-student` / `DemoPass-2026!`
- Recruiter: `demo-recruiter` / `DemoPass-2026!`

## Environment Variables (.env)
- `APP_ENV=local` â†’ Required explicit local profile; Django startup fails if `APP_ENV` is missing or invalid.
- `DB_ENGINE=sqlite` → Uses db.sqlite3 (no PostgreSQL needed)
- `AI_PROVIDER=mock` → No OpenAI API key required
- `BLOCKCHAIN_NETWORK=mock` → No blockchain connection

## Production Mode (Docker + PostgreSQL)
See the root README for `docker-compose.hosted.yml` and `.env.production.example`.
