# LifeLink AI — Changelog

```
Version      : 1.0
Last Updated : 2026-08-03
Authors      : [Developer 1 Name], [Developer 2 Name]
Derived From : ARCHITECTURE.md v1.0
```

> **Rules for this file**
> - Every change that affects the codebase, database, or API must be logged here **in the same PR that introduces the change**.
> - Format: Date → Developer → What changed.
> - Be specific. Write what actually changed, not vague summaries.
> - Group entries by date. Multiple entries per day are fine.
> - Never delete old entries.

---

## Format

```
## [YYYY-MM-DD]

### Developer Name

**Type:** feat | fix | docs | refactor | chore | test

- Short description of what changed
- Module / file affected
- If database changed: table and column
- If API changed: endpoint and method
```

---

## [2026-08-03]

### [Developer 1 Name]

**Type:** docs

- Created `ARCHITECTURE.md` v1.0 — Master Blueprint for LifeLink AI
- Contains all 50 sections across 4 phases: Product, Technical, Engineering, Implementation
- Established module ownership, tech stack decisions, folder structure, and all 7 ADRs

**Type:** docs

- Created `DATABASE.md` v1.0
- Defined all 14 tables, columns, constraints, indexes, and foreign keys
- Documented blood type compatibility matrix and all 14 PostgreSQL enum types
- Established migration strategy and soft-delete policy

**Type:** docs

- Created `API.md` v1.0
- Documented all 46 API endpoints across 9 modules
- Defined standard request/response envelopes, error code reference, and rate limiting rules

**Type:** docs

- Created `README.md` v1.0
- Project overview, problem statement, feature matrix, tech stack, installation guide, local development setup

**Type:** docs

- Created `CHANGELOG.md` v1.0 (this file)
- Established changelog format and contribution rules

---

## [2026-08-13]

### Technical Lead

**Type:** chore

- Initialized full production-grade project structure for LifeLink AI (Phase 1.1)
- Created Next.js 14 frontend scaffolding including components (ui, layout, features), hooks, store, types, styles, services, utils, and lib directories
- Created FastAPI backend scaffolding with app/, core/, configuration, and all 10 core modules (auth, donor, hospital, blood_bank, inventory, emergency, notification, ai_gateway, analytics, admin)
- Created FastAPI AI microservice scaffolding with modules (matching, prediction, ocr, nlp)
- Added Docker files: Dockerfiles for frontend, backend, and ai-service, nginx.conf proxy, init.sql database setups, and root docker-compose.yml
- Configured project tools: .gitignore, .editorconfig, .pre-commit-config.yaml, ruff/mypy/pytest settings via pyproject.toml
- Set up placeholders and empty routers/services/repositories/models/schemas for all modules

---

## [2026-08-15]

### Technical Lead

**Type:** chore

- Created Windows developer experience batch scripts: `build.bat`, `run.bat`, and `stop.bat`
- Added prerequisites and Docker daemon checks, auto-generation of development environment keys, and compose build validations in `build.bat`
- Added container startup sequence, healthcheck check looping, and automatic browser launch in `run.bat`
- Added clean container shutdown logic in `stop.bat`
- Updated `README.md` with Windows Quick Start documentation section

---

## [2026-09-02]

### Engineering Team

**Type:** feat

- Implemented Phase 1.2 Feature 1: Public Emergency Request Intake & Tracking
- Added Alembic migration `create_emergency_requests_table`
- Built backend models, repository, service, and router for emergency requests
- Created Zero-PII public tracking schema `EmergencyPublicTrackingSchema` protecting patient privacy
- Added sequence retry loop for collision-free `request_number` generation
- Built Next.js public emergency intake form (`/emergency`) and live tracking view (`/emergency/track/[id]`)

**Type:** feat

- Implemented Phase 1.2 Feature 2: Authentication & Identity Foundation
- Added Alembic migration `create_auth_tables` for `users` and `user_roles`
- Implemented bcrypt work factor 12 password hashing and JWT HS256 access/refresh tokens in `app.core.security`
- Built RBAC dependencies (`get_current_user`, `get_current_active_user`, `require_role`)
- Created backend auth router (`/register`, `/login`, `/me`, `/logout`)
- Built frontend auth state store (`authStore`), Axios interceptor, and pages (`/login`, `/register`, `/dashboard`)
- Added comprehensive pytest test suite in `tests/test_auth.py`

**Type:** feat

- Implemented Phase 1.3: Donor Registration & Donor Profile
- Added Alembic migration `create_donors_table`
- Built backend `Donor` model, schemas, repository, service, and router (`POST /api/v1/donors`, `GET /api/v1/donors/me`, `PUT /api/v1/donors/me`, `PATCH /api/v1/donors/me/availability`)
- Enforced 1-to-1 authenticated user ownership and eligibility standards (weight ≥ 45kg)
- Built Next.js Donor Dashboard & Profile page (`/donor`) with real-time availability toggle
- Added donor test suite in `tests/test_donor.py` (7 tests passing)


**Type:** feat | refactor | fix

- Complete Frontend Design System & UI/UX Redesign (Objective A)
  - Established dual Light & Dark semantic color system in `globals.css` and `tailwind.config.js` with HSL variables.
  - Eliminated oppressive pitch-black and decorative red overload; restored semantic colors (Critical Red, Warning Orange, Success Green, Information Blue, LifeLink Crimson Primary).
  - Built `ThemeProvider` and accessible `ThemeToggle` component with localStorage persistence and anti-FOUC script.
  - Redesigned global `Navbar`: LifeLink AI branding, primary navigation, visible `Sign In` and `Register` CTAs, `Request Blood` primary emergency action, and full responsive mobile drawer sheet.
  - Redesigned landing page (`/`): 2-column hero with calm value proposition, high-fidelity Live Dispatch Radar product preview, semantic shortage bulletin, interactive 8-group blood selector, 3-step workflow (`Request → Match → Notify`), dedicated `#hospitals` section, calm donor section, and professional footer with collapsible Developer Diagnostics.
  - Polished `/emergency`, `/emergency/track/[id]`, `/login`, `/register`, `/dashboard`, and `/donor` with full WCAG 2.1 AA accessibility (accessible `useId`, label associations, keyboard traps, touch targets).
  - Sanitized internal developer jargon (`US-P01`, `ADR-002`, `PostgreSQL`, `UUID`, hardcoded `localhost:8000` URLs).
- Development Run / Stop Workflow Fix (Objective B)
  - Updated `run.bat` to set `title LifeLink Launcher` and record its PID in `.lifelink_launcher.pid`.
  - Created `scripts/close_lifelink_windows.ps1` for targeted process termination using `Win32_Process` CommandLine filtering and PID tracking.
  - Updated `stop.bat` to terminate all LifeLink-spawned windows (`LifeLink Launcher`, `LifeLink Logs - Frontend`, `LifeLink Logs - Backend`, `LifeLink Logs - AI Service`) while strictly preserving unrelated CMD, PowerShell, and Terminal windows.
  - Verified container health, route status (all 7 routes HTTP 200 OK), and 19/19 backend tests passing.

## [2026-09-02]

### Senior Engineering & Architecture Team

**Type:** feat | test | refactor

- Phase 1.4: Hospital & Blood Bank Operational Foundation Completed
  - Feature 1: Hospital Operational Portal
    - Implemented `Hospital`, `HospitalStaff`, and `HospitalTypeEnum` in `backend/app/modules/hospital/models.py`.
    - Created repository layer `HospitalRepository` and service layer `HospitalService` with ReBAC authorization and tenancy isolation.
    - Implemented API endpoints (`POST /api/v1/hospitals`, `GET /api/v1/hospitals/me`, `PUT /api/v1/hospitals/me`, `GET /api/v1/hospitals/me/dashboard`, `GET /api/v1/hospitals/me/requests`, `POST /api/v1/hospitals/me/requests`, `GET /api/v1/hospitals`, `GET /api/v1/hospitals/{id}`).
    - Built frontend Hospital Dashboard (`/hospital`), Hospital Facility Profile (`/hospital/profile`), and Hospital Emergency Requisitions Log (`/hospital/requests`) with modal creation, status filtering, and real-time live metric cards.
  - Feature 2: Blood Bank Operational Portal
    - Implemented `BloodBank` model in `backend/app/modules/blood_bank/models.py`.
    - Created repository layer `BloodBankRepository` and service layer `BloodBankService`.
    - Implemented API endpoints (`POST /api/v1/blood-banks`, `GET /api/v1/blood-banks/me`, `PUT /api/v1/blood-banks/me`, `GET /api/v1/blood-banks/me/dashboard`, `GET /api/v1/blood-banks/me/demand`, `GET /api/v1/blood-banks`, `GET /api/v1/blood-banks/{id}`).
    - Built frontend Blood Bank Operations Console (`/blood-bank`) and Blood Bank Facility Settings (`/blood-bank/profile`) with regional emergency demand feed and honest empty state for Phase 1.5 cold-chain storage.
  - Database Schema & Migrations:
    - Alembic migration `d6934071e5c3` created `hospitals`, `hospital_staff`, `blood_banks`, and added foreign keys (`hospital_id` and `requested_by`) to `emergency_requests`.
  - Frontend Global Navigation & UI:
    - Added role resolution helpers in `lib/auth.ts` (`getPrimaryRole`, `getDefaultDashboardPath`, `isHospitalStaff`, `isBloodBankStaff`, `isDonor`).
    - Updated `Navbar.tsx` to dynamically adapt navigation between Hospital, Blood Bank, Donor, and Unauthenticated states in desktop and mobile drawer.
  - Verification & Testing:
    - Backend Pytest suite expanded from 19 to 31 tests (100% passing in 17.30s).
    - Live HTTP E2E suite executed (13/13 passing): verified multi-role registration, login, profile management, live emergency requisition dispatch, live demand feed, public DPDP-compliant tracking, and cross-role authorization isolation.
    - Terminal isolation test verified 100% preservation of unrelated user consoles.

## [2026-09-02]

### Senior Engineering & Architecture Team

**Type:** feat | test | refactor

- Phase 1.5: Blood Inventory + Blood Availability Operational Foundation Completed
  - Feature 1: Real Blood Bank Inventory
    - Created deterministic blood compatibility and parsing in `backend/app/core/medical.py` (Whole Blood, RBC, and Plasma rules).
    - Database migration `e7045182f6d4` created `blood_inventory` and `inventory_history` tables with `facility_type_enum` and `inventory_change_enum`.
    - Implemented `BloodInventory` and `InventoryHistory` models, repositories, and services with ADR-001 pessimistic locking (`with_for_update`) and immutable audit logging.
    - Added API endpoints: `GET /api/v1/blood-banks/me/inventory`, `PUT /api/v1/blood-banks/me/inventory/{blood_type}`, `PUT /api/v1/blood-banks/me/inventory`, and public directory `GET /api/v1/blood-banks/{id}/inventory`.
    - Upgraded Blood Bank Console (`/blood-bank`) with 4 cold storage summary cards, live 8-group ABO/Rh inventory management table, and interactive stock adjustment modal.
  - Feature 2: Hospital Requisition Foundation & Deterministic Compatibility
    - Verified hospital emergency requisition lifecycle and preserved public emergency intake.
    - Unified ABO/Rh compatibility checking into zero-dependency standard-library medical logic.
  - Feature 3: Blood Availability Integration
    - Implemented `GET /api/v1/blood-banks/me/demand/{request_id}/availability` calculating truthful compatible stock availability against regional emergency demand.
    - Excluded expired stock from available counts.
    - Added live availability indicators (🟢 Compatible Stock Available, 🟡 Partial Compatible Stock, 🔴 Zero Compatible Stock) on the Blood Bank Console.
    - Preserved patient privacy: zero patient PII exposed to blood bank or public tracking endpoints.
  - Verification & Regression:
    - Expanded backend test suite from 31 to 41 tests (100% passing in 25.13s).
    - Executed live HTTP E2E integration test suite (10/10 tests passing).
    - Verified Next.js 14 production standalone build (14/14 routes generated cleanly).
    - Verified all 13 core routes return HTTP 200 OK.
    - Verified run.bat and stop.bat process isolation.

## [2026-09-07]

### Senior Engineering & Architecture Team

**Type:** feat | test | refactor | ml

- Phase 1.6: Matching & Coordination Engine Completed
  - Feature 1: Matching Domain & Database Foundation
    - Database migration `f8152936a7e5` created `match_runs` and `match_candidates` tables with `match_run_status_enum`, `match_candidate_type_enum`, and `match_candidate_status_enum`.
    - Implemented `MatchRun` and `MatchCandidate` SQLAlchemy models, Pydantic schemas, and repositories with spatial indexing and composite queries.
    - Added ReBAC security verification: strictly authenticated hospital admins/staff can match only requisitions belonging to their hospital.
  - Feature 2: Deterministic Candidate Discovery Gate
    - Strict medical safety invariant: zero ML in eligibility or medical compatibility.
    - Verified candidates filtered deterministically against ABO/Rh rules (`backend/app/core/medical.py`), exclusion of 56-day cooling period donors, unavailable donors, and expired blood bank inventory.
    - Privacy protection: zero patient PII passed into candidate objects; donor IDs pseudo-anonymized as `Donor #<HEX>`.
  - Feature 3: AI Donor Response Propensity & Ranking Layer
    - Evaluated and trained donor response propensity model on the UCI Blood Transfusion Service Center dataset (`ai/training/train_donor_response.py`) using StandardScaler and class-balanced Logistic Regression with 5-fold cross validation (ROC-AUC 0.7521, Recall 0.7528).
    - Serialized model artifact `donor_response_v1.joblib` and `metadata.json` under `ai/models/donor-response-v1/`.
    - Integrated multi-factor composite ranking: $0.40 \times \text{Compatibility} + 0.30 \times \text{Proximity} + 0.20 \times \text{Availability} + 0.10 \times \text{Propensity}$.
    - Implemented transparent AI explainability checklist with bulleted medical and operational factors.
    - Built deterministic fallback scoring in case AI service is unreachable or uninitialized.
  - Feature 4: Clinician Matching & Coordination Workspace UI
    - Created Hospital Matching Console at `/hospital/requests/[id]/matches` with Requisition Summary Banner, Radius Selector (15km, 25km, 50km, 100km), Re-run Matching action, and AI Disclosure Banner.
    - Built Verified Blood Bank Candidate cards with units available, distance, and contact details.
    - Built Privacy-Safe Donor Candidate cards with masked donor identifier, distance, response propensity badge, and explainability factors.
## [2026-09-08]

### Senior Engineering & Architecture Team

**Type:** feat | test | refactor | docs

- Phase 1.7: UX Restructure, Role-Based Dashboards & Verification Completion
  - Objective 1: Role-Based Routing & Dashboard Redirection
    - Implemented unified `/dashboard` router component that auto-redirects users to `/hospital`, `/blood-bank`, `/donor`, or `/admin` based on primary user roles.
    - Updated `Navbar.tsx` and `Footer.tsx` navigation links and role-specific workspace navigation.
  - Objective 2: Truthful 4-Stage Emergency Tracking Stepper
    - Replaced theoretical request-level verification step with canonical 4-stage emergency request lifecycle (`1. Request Created` → `2. Matching & Coordination` → `3. Dispatch / In Progress` → `4. Fulfilled`).
    - Clarified that "Hospital Verification" is an institutional account/facility verification (`is_verified` boolean in Postgres), not a per-request stage.
    - Preserved strict DPDP-compliant zero-PII sanitization on `/emergency/track/[id]` public tracking views.
  - Objective 3: Donor Onboarding Gating & Mandatory Field Validation
    - Implemented strict frontend and backend gating requiring 6 mandatory profile fields (`Blood Type`, `Gender`, `Weight >= 45kg`, `City`, `State`, `Pincode` 4-10 digits).
    - Unfinished donor profiles are gated from appearing in emergency match candidate discovery until profile completion.
    - Added profile update endpoint `PATCH /api/v1/auth/me` (`full_name`, `phone`).
  - Objective 4: Hospital & Blood Bank Institutional Verification UI
    - Added truthful verification status badges (`Verified Facility` vs `Verification Pending (Admin Review)`) on `/hospital` and `/blood-bank`.
    - Integrated Admin facility verification workflow endpoints (`GET /api/v1/admin/verifications/pending`, `PATCH /api/v1/admin/hospitals/{id}/verify`, `PATCH /api/v1/admin/blood-banks/{id}/verify`).
  - Objective 5: Automated Test Suite Expansion & Documentation Synchronization
    - Expanded backend test suite from 45 to 51 test cases (100% passing across auth, donor gating, hospital, blood bank, inventory, matching, and validation).
    - Synchronized all architectural and technical documentation (`ARCHITECTURE.md`, `DATABASE.md`, `API.md`, `README.md`, `CHANGELOG.md`) with codebase reality.

## [2026-09-08]

### Senior Engineering & Architecture Team

**Type:** feat | fix | ux | test | docs

- Forensic UX/UI Cleanup, Navigation Hierarchy Correction & Donor Response Workflow
  - Layout Deduplication:
    - Removed redundant nested `<Navbar />` and `<Footer />` from `frontend/app/(public)/about/page.tsx` ensuring single top navigation and single footer across all routes.
  - Password Input Accessibility:
    - Enhanced `frontend/components/ui/Input.tsx` with an accessible Show/Hide toggle button for `type="password"`.
    - Added accessible SVG icons, `aria-label`, state preservation, keyboard operability, and touch-target padding (`pr-11`).
  - Navigation Hierarchy & Emergency Placement:
    - Relocated `[ Emergency ]` link directly adjacent to `[ LifeLink AI ]` brand identity in `frontend/components/layout/Navbar.tsx`.
    - Restructured donor navigation to prioritize `[ Donor Dashboard ]` first, followed by `[ About ]`. Synchronized mobile drawer.
  - Donor Opportunity Presentation & Response Workflow:
    - Refactored `/donor` opportunity cards to prominently display Hospital Name, Blood Type Needed, Units Required, Location, and Urgency.
    - Replaced the inappropriate `/emergency/track/[id]` requisition link with a dedicated Donor Emergency Opportunity Detail & Response route (`/donor/opportunities/[id]`).
    - Built rich donor response workspace with compatibility badges, urgency indicators, hospital facility details, accept/decline actions, and cooldown validation.
  - Backend Donor Response Capability & ReBAC:
    - Created `donor_emergency_responses` table via migration `g9263047a8f6`.
    - Added `GET /api/v1/donors/me/opportunities/{request_id}` and `POST /api/v1/donors/me/opportunities/{request_id}/respond` endpoints.
    - Enforced strict 56-day cooldown verification, blood compatibility check, and inactive request rejection.
    - Integrated real-time donor response status (`ACCEPTED`, `DECLINED`, `PENDING`) into hospital matching candidate cards (`/hospital/requests/[id]/matches`).
  - Verification:
    - Expanded automated pytest suite from 51 to 56 tests (100% passing in Docker backend container).
    - Frontend TypeScript type-checking and Next.js 14 production build verified with 0 errors.

---

*LifeLink AI — Changelog*  
*Update this file in every PR before merging to main.*


