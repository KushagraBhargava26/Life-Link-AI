-- docker/postgres/init.sql
-- LifeLink AI — Database Initialization Script
-- Architecture Reference: ARCHITECTURE.md Section 24 (Database Overview)
--
-- Enables required PostgreSQL extensions and creates ENUM types on database startup.

-- Enable UUID extension for auto-generating primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable PostGIS extension for geospatial mapping and proximity queries (v2.0+)
CREATE EXTENSION IF NOT EXISTS "postgis";

-- =============================================================================
-- ENUM Types (must exist before tables are created by SQLAlchemy)
-- =============================================================================

CREATE TYPE IF NOT EXISTS facility_type_enum AS ENUM ('HOSPITAL', 'BLOOD_BANK');

CREATE TYPE IF NOT EXISTS inventory_change_enum AS ENUM (
    'RESTOCK', 'EMERGENCY_USE', 'EXPIRY_DISPOSAL',
    'TRANSFER_IN', 'TRANSFER_OUT', 'MANUAL_CORRECTION'
);

CREATE TYPE IF NOT EXISTS hospital_type_enum AS ENUM (
    'GOVERNMENT', 'PRIVATE', 'TRUST', 'CLINIC', 'SPECIALTY'
);

CREATE TYPE IF NOT EXISTS match_run_status_enum AS ENUM (
    'INITIATED', 'RUNNING', 'COMPLETED', 'FAILED', 'NO_CANDIDATES'
);

CREATE TYPE IF NOT EXISTS match_candidate_type_enum AS ENUM ('DONOR', 'BLOOD_BANK');

CREATE TYPE IF NOT EXISTS match_candidate_status_enum AS ENUM (
    'PROPOSED', 'SHORTLISTED', 'DISMISSED'
);

-- Log completion
SELECT 'Database initialized with UUID, PostGIS extensions and all ENUM types' as status;
