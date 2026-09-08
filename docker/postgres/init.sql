-- docker/postgres/init.sql
-- LifeLink AI — Database Initialization Script
-- Architecture Reference: ARCHITECTURE.md Section 24 (Database Overview)
--
-- Enables required PostgreSQL extensions on database startup.

-- Enable UUID extension for auto-generating primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable PostGIS extension for geospatial mapping and proximity queries (v2.0+)
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Log completion
SELECT 'Database initialized with UUID and PostGIS extensions' as status;
