<p align="center">
  <h1 align="center">🩸 LifeLink AI</h1>
  <p align="center"><strong>AI-Powered Emergency Blood Intelligence & Coordination Platform</strong></p>
  <p align="center">
    <img src="https://img.shields.io/badge/Status-Phase%201.7%20Complete-brightgreen?style=flat-square" />
    <img src="https://img.shields.io/badge/Version-1.7.0-blue?style=flat-square" />
    <img src="https://img.shields.io/badge/Tests-51%20Passing%20(100%25)-success?style=flat-square" />
    <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square" />
    <img src="https://img.shields.io/badge/Frontend-Next.js%2014-black?style=flat-square" />
    <img src="https://img.shields.io/badge/Database-PostgreSQL%2016-336791?style=flat-square" />
    <img src="https://img.shields.io/badge/AI-donor--response--v1%20(ROC--AUC%200.7521)-F7931E?style=flat-square" />
  </p>
</p>

---

## Problem Statement

Every year in India, thousands of patients experience critical delays during medical emergencies — not because blood is entirely unavailable, but because **the existing healthcare ecosystem lacks a real-time, deterministic, intelligent coordination network**.

Hospitals, blood banks, voluntary donors, and emergency patients frequently operate in fragmented silos. LifeLink AI delivers an operational core that bridges demand and dual-supply (blood bank stock + voluntary donors) with deterministic biological safety and advisory AI ranking.

---

## What is LifeLink AI?

LifeLink AI is a full-stack emergency blood coordination platform connecting **patients, eligible voluntary donors, hospitals, blood banks, and platform administrators** into a unified, secure, real-time workflow.

When an emergency blood requisition is initiated:
1. **Biological Safety Gate**: Pure Python standard library (`backend/app/core/medical.py`) applies deterministic ABO/Rh compatibility rules across Whole Blood, RBC, and Plasma.
2. **Dual-Supply Discovery**: Simultaneously discovers available units from verified Blood Banks and eligible Voluntary Donors across 15, 25, 50, and 100 km radii.
3. **Advisory AI Propensity**: An internal AI microservice (`donor-response-v1`) predicts donor response propensity, integrated into a 40/30/20/10 composite score with instant deterministic fallback.
4. **Truthful 4-Stage Tracking**: Public tracking stepper (`/emergency/track/EMG-...`) offers real-time status visibility with zero personal data leakage.

---

## Implemented Features (Phases 1.1–1.7 Ground Truth)

| Capability / Module | Implemented Status | Architectural Details |
|---|:---:|---|
| **Role-Based Auth & ReBAC** | ✅ **COMPLETE** | 9 system roles, JWT access/refresh tokens, bcrypt hashing, rate limiting |
| **Donor Profile & Gating** | ✅ **COMPLETE** | Strict mandatory onboarding gating (6 fields), 56-day clinical donation cooldown |
| **Hospital Operations Portal** | ✅ **COMPLETE** | Facility registration, admin verification badges, requisition modal, matching workspace |
| **Blood Bank Operations** | ✅ **COMPLETE** | Dedicated inventory console, PostgreSQL stock with `component` column, demand feed |
| **Real-Time Blood Inventory** | ✅ **COMPLETE** | Pessimistic locking (`with_for_update`), check constraints, unexpired stock filtering |
| **Emergency Requisitions** | ✅ **COMPLETE** | Public intake (`/emergency`), tracking codes (`EMG-YYYYMMDD-XXXX`), status workflow |
| **Medical Compatibility Engine** | ✅ **COMPLETE** | Pure deterministic Python standard library (`medical.py`) for ABO/Rh safety |
| **Matching & Coordination** | ✅ **COMPLETE** | Dual-supply discovery, multi-tier search radii (15/25/50/100 km), composite scoring |
| **Advisory AI Microservice** | ✅ **COMPLETE** | Port 8001 microservice, `donor-response-v1` (ROC-AUC 0.7521), deterministic fallback |
| **Admin Verification Console** | ✅ **COMPLETE** | `/admin` queue for reviewing and approving hospitals and blood banks |
| **DPDP Privacy Protections** | ✅ **COMPLETE** | Masked candidate tokens (`Donor #DONOR-XXXX`), zero PII in public tracking |
| **Automated Test Suite** | ✅ **COMPLETE** | 51 unit & integration pytest cases (100% green) covering all core modules |
| **Push / SMS Gateway** | 🔮 *Phase 1.8* | External Twilio SMS / Firebase FCM integration |
| **Live GPS Map Telemetry** | 🔮 *Phase 1.8* | Real-time vehicle turn-by-turn tracking |
| **Medical Document OCR** | 🔮 *v2.0* | Prescription / lab test image scanning |
| **Organ Allocation Module** | 🔮 *v2.0* | Solid organ immunological HLA matching |

---

## Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | Next.js 14, React 18, Tailwind CSS, TypeScript | 15 App Router pages, Light/Dark theme, zero mock statistics |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2.x, Alembic | 32 REST endpoints, asyncpg driver, Pydantic v2 schemas |
| **AI Microservice** | FastAPI, Scikit-learn, joblib, NumPy | `donor-response-v1` LogisticRegression classifier (UCI dataset) |
| **Database & Cache** | PostgreSQL 16, Redis 7 | 6 Alembic migrations (Head: `f8152936a7e5`), row-level locking |
| **Proxy & Gateway** | Nginx Alpine | Reverse proxy, static asset routing, CORS handling |
| **Infrastructure** | Docker, Docker Compose, Windows Batch Scripts | 6-container topology, isolated network, `run.bat` / `stop.bat` |


---

## Team

| Developer | Role | Modules |
|---|---|---|
| [Developer 1 Name] | Platform Lead | Auth, Donor, Emergency, Notification, Admin, Frontend Auth/Emergency UI |
| [Developer 2 Name] | Infrastructure & AI Lead | Hospital, Blood Bank, Inventory, AI Service, Analytics, Docker, Frontend Maps/Inventory UI |

---

## Folder Structure

```
LifeLink-AI/
│
├── README.md
├── ARCHITECTURE.md       ← Master Blueprint (read this first)
├── DATABASE.md           ← Database schema and relationships
├── API.md                ← All API endpoint contracts
├── CHANGELOG.md          ← Change history
│
├── docker-compose.yml
├── .env.example
│
├── backend/              ← FastAPI Application (Python)
│   ├── Dockerfile
│   └── app/
│       ├── main.py
│       ├── core/
│       └── modules/
│           ├── auth/
│           ├── donor/
│           ├── hospital/
│           ├── blood_bank/
│           ├── inventory/
│           ├── emergency/
│           ├── notification/
│           ├── ai_gateway/
│           ├── analytics/
│           └── admin/
│
├── frontend/             ← Next.js Application (TypeScript)
│   ├── Dockerfile
│   └── app/
│
├── ai/                   ← AI Inference Service (Python/ML)
│   ├── Dockerfile
│   └── app/
│       └── modules/
│           ├── matching/
│           └── prediction/
│
├── docker/               ← Nginx and DB configs
└── tests/                ← End-to-end tests
```

---

## Installation

### Prerequisites

Ensure the following are installed on your machine:

- [Docker](https://www.docker.com/) (v24+)
- [Docker Compose](https://docs.docker.com/compose/) (v2+)
- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) (v20+) — for local frontend development only
- [Python](https://www.python.org/) (3.11+) — for local backend development only
### Quick Start — Windows

For developers running on Windows with Docker Desktop installed, we provide three convenient shortcut batch scripts:

#### First-time setup:
1. Ensure **Docker Desktop** is launched and running.
2. Double-click `build.bat` in the repository root. This will:
   - Verify prerequisites (Docker, Docker Compose).
   - Create a local development `.env` file from `.env.example`.
   - Auto-generate secure local development secrets (`SECRET_KEY` and `AI_SERVICE_API_KEY`).
   - Run `docker compose build` to build all containers.
3. Double-click `run.bat` to launch the services. This will:
   - Startup Nginx, Frontend, Backend, AI service, PostgreSQL, and Redis.
   - Wait for health check statuses to pass.
   - Automatically launch the browser at `http://localhost`.

#### Subsequent runs:
Double-click `run.bat` to start the already-built containers.

#### Stop:
Double-click `stop.bat` to cleanly shut down all services without deleting persistent database volumes.

---

### Manual Installation (All Platforms)

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/LifeLink-AI.git
cd LifeLink-AI
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in all required values:

```bash
# Required — generate a secure 256-bit key
SECRET_KEY=your-256-bit-secret-key-here

# Required — Firebase credentials (download from Firebase Console)
FIREBASE_CREDENTIALS_JSON=base64-encoded-credentials

# Required — Gmail or SendGrid for email
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional — Google Maps (defaults to OpenStreetMap if not provided)
GOOGLE_MAPS_API_KEY=
```

### 3. Start All Services

```bash
docker compose up --build
```

This starts:
- **Nginx** (port 80) — reverse proxy
- **Next.js Frontend** (port 3000, via Nginx)
- **FastAPI Backend** (port 8000, via Nginx)
- **AI Service** (port 8001, internal only)
- **PostgreSQL** (port 5432, internal only)
- **Redis** (port 6379, internal only)

### 4. Run Database Migrations

In a separate terminal, after the backend container is running:

```bash
docker compose exec backend alembic upgrade head
```

### 5. Access the Application

| Service | URL |
|---|---|
| Web Application | http://localhost |
| Backend API | http://localhost/api/v1 |
| API Documentation (Swagger) | http://localhost:8000/docs |
| API Documentation (ReDoc) | http://localhost:8000/redoc |

---

## Running Locally (Without Docker)

For faster development iteration, you can run each service locally.

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/lifelink"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key"

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:3000

### AI Service

```bash
cd ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8001
```

### PostgreSQL and Redis (Local)

If running services locally without Docker, start PostgreSQL and Redis manually or use:

```bash
# Start only the database and cache containers
docker compose up postgres redis
```

---

## Running Tests

### Automated Pytest Suite (51 Tests — 100% Green)

The backend test suite verifies authentication, donor onboarding gating, cooldown calculations, hospital and blood bank operational endpoints, inventory pessimistic concurrency, medical ABO/Rh rules, and matching candidate scoring:

```bash
# Inside the backend container
docker compose exec backend pytest -v

# Or locally with poetry / virtualenv
cd backend
pytest -v
```

### Frontend Build Verification

```bash
cd frontend
npm run build
```

---

## API Documentation

The FastAPI backend automatically generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

For the complete API contract including request/response schemas, error codes, and auth requirements, see [API.md](./API.md).

---

## Documentation

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Master blueprint — system design, module ownership, tech decisions, development standards, AI architecture. |
| [DATABASE.md](./DATABASE.md) | Complete database schema, table definitions, indexes, foreign keys, and Alembic migrations (`f8152936a7e5`). |
| [API.md](./API.md) | All 32 implemented API endpoint contracts with request/response schemas, auth requirements, and error codes. |
| [CHANGELOG.md](./CHANGELOG.md) | Chronological record of phase-by-phase deliverables and releases through Phase 1.7. |


---

## Development Workflow

### Branch Strategy

```bash
# Create a feature branch
git checkout -b feature/auth-jwt-refresh

# Commit with Conventional Commit format
git commit -m "feat(auth): add JWT refresh token endpoint"

# Push and open Pull Request for review
git push origin feature/auth-jwt-refresh
```

### Commit Message Format

```
<type>(<scope>): <description>

Types: feat, fix, docs, refactor, test, chore
Scopes: auth, donor, hospital, blood-bank, inventory, emergency, ai, frontend
```

### Before Every PR

- [ ] All tests pass: `pytest`
- [ ] Code linted: `ruff check .` and `mypy .`
- [ ] CHANGELOG.md updated
- [ ] If API changed: API.md updated
- [ ] If DB changed: DATABASE.md updated and migration written

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `APP_ENV` | YES | `development` or `production` |
| `SECRET_KEY` | YES | 256-bit secret for JWT signing |
| `DATABASE_URL` | YES | PostgreSQL async connection string |
| `REDIS_URL` | YES | Redis connection string |
| `AI_SERVICE_URL` | YES | URL of the AI service |
| `AI_SERVICE_API_KEY` | YES | Internal API key for AI service |
| `FIREBASE_CREDENTIALS_JSON` | YES | Base64-encoded Firebase service account |
| `SMTP_HOST` | YES | SMTP server hostname |
| `SMTP_PORT` | YES | SMTP port (587 for TLS) |
| `SMTP_USERNAME` | YES | SMTP username / email address |
| `SMTP_PASSWORD` | YES | SMTP password or app password |
| `NOMINATIM_BASE_URL` | NO | Override default Nominatim URL |
| `ACCESS_TOKEN_TTL` | NO | Access token TTL in seconds (default: 900) |
| `REFRESH_TOKEN_TTL` | NO | Refresh token TTL in seconds (default: 604800) |

---

## Future Scope

- Medical Report OCR (EasyOCR) for automated patient data extraction
- AI demand forecasting for blood shortage prediction
- Natural language emergency request processing (spaCy NER)
- Organ donation and matching module
- Mobile application (React Native)
- Government analytics dashboard
- Blockchain-based donation audit trail
- IoT-connected blood storage monitoring
- Drone delivery coordination
- National blood registry public API

For the complete roadmap, see [ARCHITECTURE.md — Section 50](./ARCHITECTURE.md#50-future-scope-and-expansion).

---

## License

This project is developed as a Final Year B.Tech AI/ML Project.

---

*LifeLink AI — Version 1.0.0-alpha*
*Last Updated: 2026-08-03*
