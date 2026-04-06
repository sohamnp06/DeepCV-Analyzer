# 🚀 DeepCV-Analyzer

**DeepCV-Analyzer** is an advanced, AI-powered resume intelligence system designed to bridge the gap between candidates and job roles using state-of-the-art NLP and Semantic Matching.

---

## ✨ What Makes Us Unique?

Unlike traditional ATS (Applicant Tracking Systems) that rely on primitive keyword matching, **DeepCV-Analyzer** introduces a higher level of intelligence:

- **🧠 Semantic Understanding**: Uses the `all-MiniLM-L6-v2` transformer model to understand the *intent* and *context* of your experience. It recognizes that "Building Web APIs" and "Backend Development" are semantically related, even if the exact keywords don't match.
- **🔍 Domain-Specific Skill Gap Analysis**: Our engine doesn't just list missing words; it categorizes your skills into **Programming, Frontend, Backend, Databases, and Core CS Fundamentals**. It identifies which *ecosystems* you need to strengthen.
- **⚡ Zero-Cache Development Alpha**: Features a custom-built Python-based frontend server that injects `No-Cache` headers, ensuring developers see real-time UI updates without the frustration of browser caching.
- **📝 Narrative Intelligence**: Replaces generic bar charts with a structured **Textual Narrative Report**. It tells a story about your profile—strengths, weaknesses, and concrete steps for improvement.
- **🔒 Integrated Security**: Implements SHA-256 password hashing and PostgreSQL persistence, providing a production-ready foundation for user data.

---

## 🌟 Core Features

- **AI-Powered Resume Scoring**: Calculates a multi-dimensional score based on JD matching, experience length, and educational background.
- **Automated Section Classification**: Uses heuristic-based NLP to split resumes into Education, Experience, Skills, and Projects for isolated evaluation.
- **Persistent Analysis History**: Tracks and stores every scan, allowing users to monitor their profile's evolution over time.
- **Unified Command Center**: A single `start.py` script orchestrates the entire multi-port environment (Backend on 8080, Frontend on 4100).
- **Interactive UI**: A modern, dark-themed "Blue-Grid" aesthetic designed for a premium user experience.

---

## 🛠️ Technology Stack

- **Backend**: FastAPI (Async Python)
- **Frontend**: Vanilla JavaScript + HTML5/CSS3 (Decoupled Client-Server Architecture)
- **AI/ML**: `sentence-transformers` (Cross-Encoders/Bi-Encoders), `scikit-learn`
- **Database**: PostgreSQL (Relational Persistence)
- **PDF Core**: PyMuPDF (`fitz`) for high-fidelity text extraction

---

## 🚀 Getting Started

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and provide your PostgreSQL credentials and an `AUTH_SECRET`.

### 3. Launch the System
```bash
python start.py
```
Visit the **Frontend** at: [http://127.0.0.1:4100/landing.html](http://127.0.0.1:4100/landing.html)

---

## 📂 Project Architecture

- **`api_server.py`**: The heart of the system—handles uploads, triggers AI models, and talks to the DB.
- **`scoring/`**: Contains the proprietary matching algorithms and the `skill_gap` engine.
- **`models/`**: Manages the loading and execution of LLM-based embedding models.
- **`frontend/`**: A fully decoupled web client with its own high-performance dev server.
- **`database/`**: Robust logic for user authentication and results persistence.

---

## ⚠️ Important Notes
- **Models**: On first run, the system will download the `all-MiniLM-L6-v2` model (~80MB).
- **Postgres**: Ensure your PostgreSQL service is active before launching `start.py`.