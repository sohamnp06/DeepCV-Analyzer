import hashlib
import os
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor

from config import load_env_file

# Load environment variables
load_env_file()

logger = logging.getLogger(__name__)

def _env(name, default=None):
    value = os.getenv(name, default)
    if value is None:
        return default
    return value

def get_db_connection():
    """
    Creates and returns a connection to the PostgreSQL database.
    Supports both DATABASE_URL (Supabase/Render) and individual parameters.
    Ensures SSL is required for secure connections.
    """
    database_url = os.getenv("DATABASE_URL")
    
    try:
        if database_url:
            # If using Supabase Pooler, the connection string is already configured correctly
            return psycopg2.connect(database_url)

        # Fallback to individual parameters
        return psycopg2.connect(
            dbname=_env("POSTGRES_DB", "resume_tracker_db"),
            user=_env("POSTGRES_USER", "postgres"),
            password=_env("POSTGRES_PASSWORD", ""),
            host=_env("POSTGRES_HOST", "localhost"),
            port=_env("POSTGRES_PORT", "5432"),
            sslmode='require' # Always recommend SSL for cloud DBs
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def _hash_password(password):
    secret = _env("AUTH_SECRET", "change-this-secret")
    return hashlib.sha256(f"{secret}:{password}".encode("utf-8")).hexdigest()

def init_db():
    """Initializes the database schema matching the user's Supabase tables."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # User Authentication Table (matching your schema: password instead of password_hash)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        
        # Resume Analysis Results Table (matching your schema: JSONB for skills)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS resume_analysis (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role VARCHAR(100) NOT NULL,
                final_score FLOAT NOT NULL,
                jd_score FLOAT NOT NULL,
                matched_skills JSONB,
                missing_skills JSONB,
                education_quality VARCHAR(20),
                experience_quality VARCHAR(20),
                projects_quality VARCHAR(20),
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        conn.commit()
        cursor.close()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def register_user(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Using 'password' column name to match your Supabase schema
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id",
            (username, _hash_password(password)),
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    finally:
        conn.close()

def login_user(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Using 'password' column name to match your Supabase schema
        cursor.execute(
            "SELECT id, username FROM users WHERE username=%s AND password=%s",
            (username, _hash_password(password)),
        )
        user = cursor.fetchone()
        return user if user else None
    finally:
        conn.close()

def check_user_exists(username):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        return user is not None
    finally:
        conn.close()

def insert_result(user_id, data):
    """Saves detailed analysis to the resume_analysis table matching JSONB schema."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO resume_analysis (
            user_id, role, final_score, jd_score,
            matched_skills, missing_skills,
            education_quality, experience_quality, projects_quality,
            recommendations
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Convert lists to JSON strings so psycopg2 can insert them into JSONB columns
        matched_json = json.dumps(data["matched_skills"]) if isinstance(data["matched_skills"], list) else data["matched_skills"]
        missing_json = json.dumps(data["missing_skills"]) if isinstance(data["missing_skills"], list) else data["missing_skills"]

        cursor.execute(query, (
            user_id,
            data["role"],
            data["final_score"],
            data["jd_score"],
            matched_json,
            missing_json,
            data["education_quality"],
            data["experience_quality"],
            data["projects_quality"],
            data["recommendations"]
        ))
        conn.commit()
    finally:
        conn.close()