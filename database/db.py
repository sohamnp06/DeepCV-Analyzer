import hashlib
import os

import psycopg2
from psycopg2.extras import RealDictCursor

from config import load_env_file

load_env_file()


def _env(name, default=None):
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        dbname=_env("POSTGRES_DB", "resume_tracker_db"),
        user=_env("POSTGRES_USER", "postgres"),
        password=_env("POSTGRES_PASSWORD"),
        host=_env("POSTGRES_HOST", "localhost"),
        port=_env("POSTGRES_PORT", "5432"),
    )


def _hash_password(password):
    secret = _env("AUTH_SECRET", "change-this-secret")
    return hashlib.sha256(f"{secret}:{password}".encode("utf-8")).hexdigest()


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
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
    conn.commit()
    cursor.close()
    conn.close()


# -----------------------------
# USER AUTH
# -----------------------------
def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
        (username, _hash_password(password)),
    )

    user_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return user_id


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT id, username FROM users WHERE username=%s AND password_hash=%s",
        (username, _hash_password(password)),
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user if user else None


def check_user_exists(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user is not None


# -----------------------------
# INSERT RESULT
# -----------------------------
def insert_result(user_id, data):
    conn = get_connection()
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
    cursor.close()
    conn.close()