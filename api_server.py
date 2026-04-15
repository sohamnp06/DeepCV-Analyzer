import os
import tempfile
import asyncio
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from config import load_env_file
from database.db import init_db, insert_result, login_user, register_user, check_user_exists, get_db_connection
from scoring.report_narrative import build_analysis_narrative

get_structured_sections = None
extract_text = None
clean_text = None
match_resume_to_jd = None
compute_score = None
evaluate_sections = None
semantic_match = None
generate_skill_gap = None

load_env_file()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deepcv-api")

DB_READY = False
DB_ERROR = ""
ENGINES_READY = False

def load_ml_modules_sync():
    global get_structured_sections, extract_text, clean_text, match_resume_to_jd
    global compute_score, evaluate_sections, semantic_match, generate_skill_gap, ENGINES_READY
    
    from nlp.section_classifier import get_structured_sections as gss
    from parser.extract_text import extract_text as et
    from parser.utils import clean_text as ct
    from scoring.jd_matcher import match_resume_to_jd as mrj
    from scoring.scorer import compute_score as cs
    from scoring.section_scorer import evaluate_sections as es
    from scoring.semantic_matcher import semantic_match as sm
    from scoring.skill_gap import generate_skill_gap as gsg
    
    get_structured_sections = gss
    extract_text = et
    clean_text = ct
    match_resume_to_jd = mrj
    compute_score = cs
    evaluate_sections = es
    semantic_match = sm
    generate_skill_gap = gsg
    
    ENGINES_READY = True

async def preload_engines():
    logger.info("Starting background preload of NLP and Scoring engines...")
    try:
        await asyncio.to_thread(load_ml_modules_sync)
        logger.info("AI Engines loaded successfully in background.")
    except Exception as e:
        logger.error(f"Failed to preload modules: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global DB_READY, DB_ERROR
    start_time = time.time()
    logger.info("Initializing application resources...")
    
    asyncio.create_task(preload_engines())
    
    try:
        init_db()
        DB_READY = True
        logger.info(f"Database initialized in {time.time() - start_time:.2f}s")
    except Exception as exc:
        DB_READY = False
        DB_ERROR = str(exc)
        logger.error(f"Database initialization failed: {exc}")
    yield
    logger.info("Shutting down application...")

app = FastAPI(title="DeepCV Analyzer Production API", lifespan=lifespan)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def simulate_latency():
    latency = float(os.getenv("API_LATENCY_MS", 0)) / 1000.0
    if latency > 0:
        await asyncio.sleep(latency)

DEFAULT_JD = {
    "web_developer": "Looking for a web developer with HTML, CSS, JavaScript, React, Node, API and Git skills.",
    "software_developer": "Looking for a software developer with Python OR Java, DSA, DBMS, and system design.",
    "data_scientist": "Looking for a data scientist with Python, ML, pandas, numpy, SQL, and statistics.",
    "ml_engineer": "Looking for a ML engineer with Python, PyTorch/TensorFlow, NLP, and CV.",
    "data_analyst": "Looking for a data analyst with Excel, SQL, Tableau/PowerBI, and Python.",
    "devops_engineer": "Looking for a DevOps engineer with AWS/Azure, Docker, Kubernetes, and CI/CD.",
    "product_manager": "Looking for a Product Manager with Agile, JIRA, and roadmap planning."
}

def infer_role(resume_text):
    text = resume_text.lower()
    
    try:
        import json
        with open("data/ats_keywords.json", "r") as f:
            ats_data = json.load(f)
            
        scores = {}
        for role, keywords_dict in ats_data.items():
            must_have = keywords_dict.get("must_have", [])
            optional = keywords_dict.get("optional", [])
            all_keywords = must_have + optional
            
            # Sum how many times each keyword appears across both must_have and optional arrays
            scores[role] = sum(text.count(k.lower()) for k in all_keywords)
            
        if scores:
            return max(scores, key=scores.get)
    except Exception as e:
        logger.error(f"Error loading ats_keywords in infer_role: {e}")

    scores = {
        "web_developer": sum(text.count(k) for k in ["html", "css", "react", "node", "web developer"]),
        "software_developer": sum(text.count(k) for k in ["java", "dsa", "c++", "system design", "software engineer", "backend"]),
        "data_scientist": sum(text.count(k) for k in ["data scientist", "machine learning", "python", "pandas", "numpy", "statistics"]),
        "ml_engineer": sum(text.count(k) for k in ["ml engineer", "machine learning", "pytorch", "nlp", "llm", "transformers", "scikit-learn", "deep learning"]),
        "data_analyst": sum(text.count(k) for k in ["data analyst", "sql", "excel", "dashboard", "tableau", "power bi"]),
        "devops_engineer": sum(text.count(k) for k in ["devops", "aws", "docker", "kubernetes", "ci/cd"]),
        "product_manager": sum(text.count(k) for k in ["product manager", "agile", "jira", "roadmap", "scrum"])
    }
    return max(scores, key=scores.get)

@app.get("/db-test")
async def db_test():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        logger.error(f"DB Test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    status = "ok" if (DB_READY and ENGINES_READY) else "initializing"
    return {
        "status": status,
        "db": DB_READY,
        "db_error": DB_ERROR if not DB_READY else None,
        "ai_engines": ENGINES_READY,
        "timestamp": time.time()
    }

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "DeepCV API",
        "version": "v1.0.2-fixed-auth"
    }

def _ensure_ready():
    if not DB_READY:
        raise HTTPException(status_code=503, detail="Database not ready.")
    if not ENGINES_READY:
        raise HTTPException(status_code=503, detail="AI Engines still preloading on Render. Please wait 30 seconds.")

async def get_credentials(request: Request, username: str, password: str):
    if username and password:
        return username.strip(), password
    try:
        data = await request.json()
        return data.get("username").strip(), data.get("password")
    except:
        return None, None

@app.post("/api/auth/register")
async def register(request: Request):
    _ensure_ready()
    u, p = await get_credentials(request, None, None)
    
    if not u or not p:
        raise HTTPException(status_code=400, detail="Username and password required")
        
    try:
        user_id = register_user(u, p)
        return {"user_id": user_id, "message": "User registered"}
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/auth/login")
async def login(request: Request):
    _ensure_ready()
    u, p = await get_credentials(request, None, None)

    if not u or not p:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    user = login_user(u, p)
    if not user: raise HTTPException(status_code=401, detail="Invalid login credentials")
    return {"user_id": user["id"], "username": user["username"], "status": "authenticated"}

@app.post("/api/analyze")
async def analyze_resume(file: UploadFile = File(...), user_id: int = Form(...)):
    _ensure_ready()
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    file_bytes = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        raw_text = extract_text(temp_path)
        cleaned = clean_text(raw_text)
        role = infer_role(cleaned)
        jd_text = DEFAULT_JD.get(role, f"Looking for a {role.replace('_', ' ').title()} with strong matching technical background.")

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
            "matched_skills": [m[0] for m in semantic_result["matched"]],
            "missing_skills": semantic_result["missing"],
            "education_quality": section_quality["education"],
            "experience_quality": section_quality["experience"],
            "projects_quality": section_quality["projects"],
            "recommendations": ", ".join(gap_result["recommendations"]),
        }
        insert_result(user_id, db_data)

        role_display = role.replace("_", " ").title()
        narratives = build_analysis_narrative(
            role_display=role_display, jd_text=jd_text,
            ats_score_pct=float(db_data["final_score"]),
            jd_match_pct=float(db_data["jd_score"]),
            final_score_raw=float(final_score),
            semantic_result=semantic_result,
            section_quality=section_quality,
            gap_result=gap_result, sections=sections,
        )

        return {
            "ats_score": round(db_data["final_score"], 2),
            "jd_match": round(db_data["jd_score"], 2),
            "section_quality": section_quality,
            "matched_skills": [m[0] for m in semantic_result["matched"]],
            "missing_skills": semantic_result["missing"],
            "recommendations": gap_result["recommendations"],
            "inferred_role": role_display,
            "narratives": narratives,
            "raw_sections": sections,
            "raw_semantic": semantic_result,
            "raw_score": float(final_score),
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal analysis error")
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
