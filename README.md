# 🚀 DeepCV-Analyzer

**DeepCV-Analyzer** is an advanced, AI-powered resume intelligence system designed to bridge the gap between candidates and job roles using state-of-the-art NLP and Semantic Matching. 

By leveraging the **Hugging Face Inference API**, this version is highly optimized, lightweight (~0MB local model footprint), and ready for seamless deployment on platforms like the **Render Free Tier**.

---

## ✨ What Makes Us Unique?

Unlike traditional ATS (Applicant Tracking Systems) that rely on primitive keyword matching, **DeepCV-Analyzer** introduces a higher level of intelligence:

- **🧠 Cloud-Powered Semantic Understanding**: Uses the `all-MiniLM-L6-v2` transformer model via the **Hugging Face Inference Router** to understand the *intent* and *context* of your experience. It recognizes that "Building Web APIs" and "Backend Development" are semantically related, even if the exact keywords don't match.
- **🔍 Domain-Specific Skill Gap Analysis**: Our engine doesn't just list missing words; it categorizes your skills into **Programming, Frontend, Backend, Databases, Core CS, Cloud, and Data Science**. It identifies which *ecosystems* you need to strengthen.
- **⚡ Deployment Optimized**: By moving from heavy local `sentence-transformers` dependencies (~2.8GB installation) to a lightweight `requests`-based API client, the backend now starts instantly and fits easily within free-tier resource limits.
- **📝 Narrative Intelligence**: Features a structured **Textual Narrative Report**. It tells a professional story about your profile—strengths, weaknesses, and concrete steps for improvement—with clear "Impact" context for every recommendation.
- **🔒 Integrated Security**: Implements SHA-256 password hashing and PostgreSQL persistence, with all sensitive keys managed securely via environment variables.

---

## 🌟 Core Features

- **AI-Powered Resume Scoring**: Calculates a multi-dimensional score based on JD matching, experience depth, and educational background.
- **Automated Section Classification**: Uses heuristic-based NLP to split resumes into Education, Experience, Skills, and Projects for isolated evaluation.
- **Persistent Analysis History**: Tracks and stores every scan, allowing users to monitor their profile's evolution over time.
- **Unified Command Center**: A single `start.py` script orchestrates the entire multi-port environment (Backend on 8080, Frontend on 4100).
- **Interactive UI**: A modern, dark-themed "Blue-Grid" aesthetic designed for a premium user experience.

---

## 🛠️ Technology Stack

- **Backend**: FastAPI (Async Python)
- **Frontend**: Vanilla JavaScript + HTML5/CSS3 (Decoupled Client-Server Architecture)
- **AI/ML**: Hugging Face Inference API (`all-MiniLM-L6-v2` / `bge-small-en-v1.5`), `scikit-learn`
- **Database**: PostgreSQL (Relational Persistence)
- **PDF Core**: PyMuPDF (`fitz`) for high-fidelity text extraction

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
python start.py
```
Visit the **Frontend** at: [http://127.0.0.1:4100/landing.html](http://127.0.0.1:4100/landing.html)

---

## 📂 Project Architecture

- **`api_server.py`**: The heart of the system—handles uploads, triggers AI analysis, and manages data persistence.
- **`scoring/`**: Contains matching algorithms, the `skill_gap` engine, and the structured narrative report builder.
- **`models/embedding_model.py`**: Handles API communication with Hugging Face with robust failure-handling and multi-model fallbacks.
- **`frontend/`**: A fully decoupled web client with a custom high-performance dev server.
- **`database/db.py`**: Secure logic for user authentication (SHA-256) and results persistence.

---

## ⚠️ Important Notes
- **API Access**: You must provide a valid `HUGGINGFACE_API_KEY` in your `.env` for the semantic matcher to function.
- **Lightweight Footprint**: This project no longer requires local PyTorch or large transformer models, saving ~3GB of disk space.
- **Postgres**: Ensure your PostgreSQL service is active before launching `start.py`.