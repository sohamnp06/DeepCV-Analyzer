import os
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from config import load_env_file
from database.db import init_db, insert_result, login_user, register_user

load_env_file()

app = FastAPI(title="DeepCV Analyzer API")
DB_READY = False
DB_ERROR = ""

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGIN", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_JD = {
    "web_developer": "Looking for a web developer with HTML, CSS, JavaScript, React, Node, API and Git skills.",
    "software_developer": "Looking for a software developer with Python/Java, DSA, DBMS and system fundamentals.",
    "data_scientist": "Looking for a data scientist with Python, ML, pandas, numpy, SQL and statistics.",
}


@app.on_event("startup")
def startup_event():
    global DB_READY, DB_ERROR
    try:
        init_db()
        DB_READY = True
        DB_ERROR = ""
    except Exception as exc:
        DB_READY = False
        DB_ERROR = str(exc)


@app.get("/api/health")
def health():
    return {"status": "ok", "db_ready": DB_READY, "db_error": DB_ERROR}


def _ensure_db_ready():
    if not DB_READY:
        raise HTTPException(
            status_code=503,
            detail=f"Database not ready. Check PostgreSQL/.env. {DB_ERROR}",
        )


@app.post("/api/auth/register")
def register(username: str = Form(...), password: str = Form(...)):
    _ensure_db_ready()
    try:
        user_id = register_user(username.strip(), password)
        return {"user_id": user_id, "username": username.strip()}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Registration failed: {exc}")


@app.post("/api/auth/login")
def login(username: str = Form(...), password: str = Form(...)):
    _ensure_db_ready()
    user = login_user(username.strip(), password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"user_id": user["id"], "username": user["username"]}


@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    role: str = Form(...),
    user_id: int = Form(...),
    job_description: str = Form(""),
):
    _ensure_db_ready()
    # Lazy-load heavy NLP/ML modules so auth endpoints stay fast and backend boots quickly.
    from nlp.section_classifier import get_structured_sections
    from parser.extract_text import extract_text
    from parser.utils import clean_text
    from scoring.jd_matcher import match_resume_to_jd
    from scoring.scorer import compute_score
    from scoring.section_scorer import evaluate_sections
    from scoring.semantic_matcher import semantic_match
    from scoring.skill_gap import generate_skill_gap

    if role not in DEFAULT_JD:
        raise HTTPException(status_code=400, detail="Invalid role selected")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume")

    file_bytes = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        raw_text = extract_text(temp_path)
        cleaned = clean_text(raw_text)
        sections = get_structured_sections(cleaned)
        semantic_result = semantic_match(cleaned, role)
        final_score = compute_score(sections, semantic_result)

        jd_text = job_description.strip() or DEFAULT_JD[role]
        jd_score = match_resume_to_jd(cleaned, jd_text)
        section_quality = evaluate_sections(sections)
        gap_result = generate_skill_gap(semantic_result)

        db_data = {
            "role": role,
            "final_score": float(final_score) * 100,
            "jd_score": float(jd_score) * 100,
            "matched_skills": ", ".join([m[0] for m in semantic_result["matched"]]),
            "missing_skills": ", ".join(semantic_result["missing"]),
            "education_quality": section_quality["education"],
            "experience_quality": section_quality["experience"],
            "projects_quality": section_quality["projects"],
            "recommendations": ", ".join(gap_result["recommendations"]),
        }
        insert_result(user_id, db_data)

        return {
            "ats_score": round(db_data["final_score"], 2),
            "jd_match": round(db_data["jd_score"], 2),
            "section_quality": section_quality,
            "matched_skills": [m[0] for m in semantic_result["matched"]],
            "missing_skills": semantic_result["missing"],
            "recommendations": gap_result["recommendations"],
        }
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass
