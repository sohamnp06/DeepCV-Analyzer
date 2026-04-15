import hashlib
import os
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor

from config import load_env_file

load_env_file()

logger = logging.getLogger(__name__)

def _env(name, default=None):
    value = os.getenv(name, default)
    if value is None:
        return default
    return value

def get_db_connection():
    database_url = os.getenv("DATABASE_URL")

    try:
        if database_url:
            return psycopg2.connect(database_url)

        return psycopg2.connect(
            dbname=_env("POSTGRES_DB", "resume_tracker_db"),
            user=_env("POSTGRES_USER", "postgres"),
            password=_env("POSTGRES_PASSWORD", ""),
            host=_env("POSTGRES_HOST", "localhost"),
            port=_env("POSTGRES_PORT", "5432"),
            sslmode='require'
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def _hash_password(password):
    secret = _env("AUTH_SECRET", "change-this-secret")
    return hashlib.sha256(f"{secret}:{password}".encode("utf-8")).hexdigest()

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

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