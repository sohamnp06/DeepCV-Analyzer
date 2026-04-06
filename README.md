# 🚀 DeepCV-Analyzer

**DeepCV-Analyzer** is an advanced, AI-powered resume intelligence system designed to bridge the gap between candidates and job roles using state-of-the-art NLP and Semantic Matching. 

By leveraging the **Hugging Face Inference API**, this version is highly optimized, lightweight (~0MB local model footprint), and ready for seamless deployment on platforms like the **Render Free Tier**.

---

## ✨ What Makes Us Unique?

Unlike traditional ATS (Applicant Tracking Systems) that rely on primitive keyword matching, **DeepCV-Analyzer** introduces a higher level of intelligence:

- **🧠 Cloud-Powered Semantic Understanding**: Uses the `all-MiniLM-L6-v2` transformer model via the **Hugging Face Inference Router** to understand context. It recognizes that "Building Web APIs" and "Backend Development" are semantically related.
- **🔍 Domain-Specific Skill Gap Analysis**: Categorizes your skills into **Programming, Frontend, Backend, Databases, Core CS, Cloud, and Data Science**.
- **⚡ Deployment Optimized**: By moving from heavy local `sentence-transformers` dependencies (~2.8GB installation) to a lightweight API client, the project fits easily within Render's free-tier limits.
- **📝 Narrative Intelligence**: Features a structured **Textual Narrative Report** that tells a professional story about your profile—strengths, weaknesses, and concrete steps for improvement.
- **🔒 Integrated Security**: SHA-256 hashing and PostgreSQL persistence with environment variable management.

---

## 🌟 Core Features

- **AI-Powered Resume Scoring**: Multi-dimensional scoring based on JD matching, experience depth, and educational background.
- **Unified Full-Stack Port**: The backend now serves the entire frontend UI, allowing you to run the complete stack on a single port.
- **Persistent Analysis History**: Tracks every scan for profile evolution monitoring.
- **Interactive UI**: A modern, dark-themed "Blue-Grid" aesthetic.

---

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JavaScript (Served via FastAPI StaticFiles)
- **AI/ML**: Hugging Face Inference API (`all-MiniLM-L6-v2` / `bge-small-en-v1.5`)
- **Database**: PostgreSQL
- **PDF Core**: PyMuPDF (`fitz`) 

---

## 🚀 Getting Started

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and provide your credentials.
```env
POSTGRES_DB=resume_tracker_db
POSTGRES_PASSWORD=your_password
AUTH_SECRET=long_random_secret
HUGGINGFACE_API_KEY=your_huggingface_token_here
```

### 3. Launch the System
```bash
python api_server.py
```
Visit the **Full Stack App** at: [http://127.0.0.1:8080/landing.html](http://127.0.0.1:8080/landing.html)

---

## 📂 Render Deployment (Web Service)

When deploying to **Render**, use the following settings:

- **Runtime**: `Python`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

---

## ⚠️ Important Notes
- **API Access**: You must provide a valid `HUGGINGFACE_API_KEY`.
- **Postgres**: Ensure your PostgreSQL service is active (or set `DATABASE_URL` in Render).
- **Frontend**: The `frontend/` folder is automatically served as static files at root `/`.