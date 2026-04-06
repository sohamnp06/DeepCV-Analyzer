import hashlib
import os
import logging
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
            # For Supabase/Render, ensure sslmode is required
            if "sslmode=" not in database_url:
                separator = "&" if "?" in database_url else "?"
                database_url += f"{separator}sslmode=require"
            return psycopg2.connect(database_url)

        # Fallback to individual parameters
        return psycopg2.connect(
            dbname=_env("POSTGRES_DB", "resume_tracker_db"),
            user=_env("POSTGRES_USER", "postgres"),
            password=_env("POSTGRES_PASSWORD", ""),
            host=_env("POSTGRES_HOST", "localhost"),
            port=_env("POSTGRES_PORT", "5432"),
            sslmode='require' if os.getenv("DATABASE_URL") else 'prefer'
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def _hash_password(password):
    secret = _env("AUTH_SECRET", "change-this-secret")
    return hashlib.sha256(f"{secret}:{password}".encode("utf-8")).hexdigest()

def init_db():
    """Initializes the database schema."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # User Authentication Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        
        # Resume Analysis Results Table (Production)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS resume_analysis (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role VARCHAR(100) NOT NULL,
                final_score NUMERIC(5,2) NOT NULL,
                jd_score NUMERIC(5,2) NOT NULL,
                matched_skills TEXT,
                missing_skills TEXT,
                education_quality VARCHAR(20),
                experience_quality VARCHAR(20),
                projects_quality VARCHAR(20),
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Example Table (specifically requested as analysis_results)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_results (
                id SERIAL PRIMARY KEY,
                text TEXT,
                score NUMERIC(5,2),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
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
        cursor.execute(
            "SELECT id, username FROM users WHERE username=%s AND password_hash=%s",
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
    """Saves detailed analysis to the resume_analysis table."""
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
        cursor.execute(query, (
            user_id,
            data["role"],
            data["final_score"],
            data["jd_score"],
            data["matched_skills"],
            data["missing_skills"],
            data["education_quality"],
            data["experience_quality"],
            data["projects_quality"],
            data["recommendations"]
        ))
        conn.commit()
    finally:
        conn.close()