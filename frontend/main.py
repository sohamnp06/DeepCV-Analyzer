from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import PyPDF2
import uuid
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ================== SUPABASE ==================
SUPABASE_URL = "https://orfsobcgsocjpwaebfta.supabase.co"
SUPABASE_KEY = "YOUR_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================== APP ==================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== JOB DATA ==================
job_descriptions = {
    "frontend": "HTML CSS JavaScript React UI UX responsive design",
    "backend": "Python Django Node.js API database SQL authentication",
    "data": "Python pandas numpy data analysis visualization statistics",
    "ml": "machine learning deep learning tensorflow scikit-learn AI models"
}

# ================== PDF ==================
def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ================== SCORE ==================
def calculate_score(resume, job):
    cv = CountVectorizer()
    vectors = cv.fit_transform([resume, job]).toarray()
    score = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    return round(score * 100, 2)

# ================== API ==================
@app.post("/analyze")
async def analyze(file: UploadFile = File(...), role: str = Form(...)):

    try:
        if role not in job_descriptions:
            return {"error": "Invalid role selected"}

        contents = await file.read()

        # ================== UPLOAD ==================
        file_name = str(uuid.uuid4()) + ".pdf"

        try:
            supabase.storage.from_("resumes").upload(
                file_name,
                contents,
                {"content-type": "application/pdf"}
            )
        except Exception as e:
            return {"error": f"Upload failed: {str(e)}"}

        file_url = f"{SUPABASE_URL}/storage/v1/object/public/resumes/{file_name}"

        # ================== EXTRACT ==================
        try:
            with open("temp.pdf", "wb") as f:
                f.write(contents)

            with open("temp.pdf", "rb") as f:
                resume_text = extract_text(f)
        except:
            return {"error": "PDF read failed"}

        # ================== SCORE ==================
        score = calculate_score(resume_text, job_descriptions[role])

        # ================== SAVE ==================
        try:
            supabase.table("candidates").insert({
                "role": role,
                "score": score,
                "file_url": file_url
            }).execute()
        except Exception as e:
            return {"error": f"DB failed: {str(e)}"}

        return {
            "score": score,
            "file_url": file_url
        }

    except Exception as e:
        return {"error": str(e)}