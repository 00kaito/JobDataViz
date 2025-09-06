-- Initial database setup for Job Market Dashboard
-- This file is executed when PostgreSQL container starts for the first time

-- Create database if it doesn't exist (this is handled by POSTGRES_DB env var)
-- CREATE DATABASE IF NOT EXISTS jobmarket;

-- Use the database
\c jobmarket;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create initial admin user (optional - can be done via application)
-- Note: This will be created by the application's first registration
-- but can be pre-created here for automation

-- Set timezone
SET timezone = 'Europe/Warsaw';

-- Initial configuration complete
SELECT 'Database initialized successfully' AS status;