import os
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from config import load_env_file
from database.db import init_db, insert_result, login_user, register_user, check_user_exists
from fastapi.responses import RedirectResponse

load_env_file()

app = FastAPI(title="DeepCV Analyzer API")
DB_READY = False
DB_ERROR = ""

from fastapi.staticfiles import StaticFiles

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGIN", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



DEFAULT_JD = {
    "web_developer": "Looking for a web developer with HTML, CSS, JavaScript, React, Node, API and Git skills. Experience in building scalable frontend and backend systems.",
    "software_developer": "Looking for a software developer with Python OR Java, Data Structures and Algorithms (DSA), DBMS, system design, and strong problem-solving fundamentals.",
    "data_scientist": "Looking for a data scientist with Python, Machine Learning (ML), pandas, numpy, SQL, deep learning, and strong applied statistics knowledge.",
    "machine_learning_engineer": "Looking for a Machine Learning engineer with Python, PyTorch or TensorFlow, NLP, Computer Vision, and deployment experience.",
    "data_analyst": "Looking for a data analyst with Excel, SQL, Tableau or PowerBI, Python, and the ability to derive actionable business insights from large datasets.",
    "devops_engineer": "Looking for a DevOps engineer with AWS/Azure/GCP, Docker, Kubernetes, CI/CD pipelines, Terraform, and Linux administration.",
    "product_manager": "Looking for a Product Manager with Agile methodologies, JIRA, strategic roadmap planning, A/B testing, and cross-functional leadership skills."
}

def infer_role(resume_text):
    text = resume_text.lower()
    scores = {
        "web_developer": sum(text.count(k) for k in ["html", "css", "react", "node", "javascript", "frontend", "backend", "web", "angular", "vue"]),
        "software_developer": sum(text.count(k) for k in ["java", "c++", "dsa", "system", "object oriented", "c#", ".net", "golang"]),
        "data_scientist": sum(text.count(k) for k in ["machine learning", "python", "pandas", "numpy", "statistics", "model", "scikit-learn", "data science"]),
        "machine_learning_engineer": sum(text.count(k) for k in ["pytorch", "tensorflow", "deep learning", "nlp", "computer vision", "llm", "keras"]),
        "data_analyst": sum(text.count(k) for k in ["excel", "sql", "tableau", "powerbi", "power bi", "dashboard", "analytics", "reporting"]),
        "devops_engineer": sum(text.count(k) for k in ["aws", "docker", "kubernetes", "ci/cd", "terraform", "jenkins", "linux", "ansible"]),
        "product_manager": sum(text.count(k) for k in ["agile", "jira", "roadmap", "scrum", "product", "stakeholders", "strategy", "metrics"])
    }
    return max(scores, key=scores.get)


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

@app.get("/")
def read_root():
    return RedirectResponse(url="/landing.html")


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
    if not check_user_exists(username.strip()):
        raise HTTPException(status_code=404, detail="User not registered, please sign up.")
        
    user = login_user(username.strip(), password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect password.")
    return {"user_id": user["id"], "username": user["username"]}


@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    user_id: int = Form(...),
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

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume")

    file_bytes = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        raw_text = extract_text(temp_path)
        cleaned = clean_text(raw_text)
        
        # Analyze role and JD locally
        role = infer_role(cleaned)
        jd_text = DEFAULT_JD[role]

        sections = get_structured_sections(cleaned)
        semantic_result = semantic_match(cleaned, role)
        final_score = compute_score(sections, semantic_result)

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
            "inferred_role": role.replace("_", " ").title()
        }
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass

# Mount frontend so the entire app can be deployed to a single free tier service
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
