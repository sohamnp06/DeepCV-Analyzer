import psycopg2


def get_connection():
    return psycopg2.connect(
        dbname="resume_tracker_db",   # ✅ FIXED
        user="postgres",              # change if needed
        password="your_password",
        host="localhost",
        port="5432"
    )


# -----------------------------
# USER AUTH
# -----------------------------
def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id",
        (username, password)
    )

    user_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return user_id


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user[0] if user else None


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