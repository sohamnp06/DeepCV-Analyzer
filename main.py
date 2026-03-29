from parser.extract_text import extract_text
from parser.utils import clean_text
from nlp.section_classifier import get_structured_sections

from scoring.semantic_matcher import semantic_match
from scoring.scorer import compute_score
from scoring.skill_gap import generate_skill_gap
from scoring.jd_matcher import match_resume_to_jd
from scoring.section_scorer import evaluate_sections

from database.db import register_user, login_user, insert_result


# -----------------------------
# 🔐 AUTH SYSTEM
# -----------------------------
print("\n1. Register\n2. Login")
choice = input("Select option: ")

if choice == "1":
    username = input("Enter username: ")
    password = input("Enter password: ")
    user_id = register_user(username, password)
    print("User registered!")

else:
    username = input("Enter username: ")
    password = input("Enter password: ")
    user_id = login_user(username, password)

    if not user_id:
        print("Invalid credentials")
        exit()

    print("Login successful!")


# -----------------------------
# MODEL PIPELINE
# -----------------------------
pdf_path = "uploads/resume1.pdf"
role = "web_developer"

job_description = """
Looking for a web developer with HTML, CSS, JS, React, Node, API, Git
"""

text = extract_text(pdf_path)
cleaned = clean_text(text)
sections = get_structured_sections(cleaned)

semantic_result = semantic_match(cleaned, role)
final_score = compute_score(sections, semantic_result)
skill_gap = generate_skill_gap(semantic_result)
jd_score = match_resume_to_jd(cleaned, job_description)
section_quality = evaluate_sections(sections)


# -----------------------------
# OUTPUT
# -----------------------------
print("\n===== FINAL SCORE =====", final_score)

print("\nMatched Skills:")
for m in semantic_result["matched"]:
    print("-", m[0])

print("\nMissing Skills:")
for s in semantic_result["missing"]:
    print("-", s)

print("\nJD Match:", int(jd_score * 100), "%")

print("\nSection Quality:")
for k, v in section_quality.items():
    print(k, ":", v)


# -----------------------------
# SAVE TO DB
# -----------------------------
db_data = {
    "role": role,
    "final_score": float(final_score),
    "jd_score": float(jd_score),

    "matched_skills": ", ".join([m[0] for m in semantic_result["matched"]]),
    "missing_skills": ", ".join(semantic_result["missing"]),

    "education_quality": section_quality["education"],
    "experience_quality": section_quality["experience"],
    "projects_quality": section_quality["projects"],

    "recommendations": ", ".join(skill_gap["recommendations"])
}

insert_result(user_id, db_data)

print("\n✅ Data stored successfully in DB!")