from parser.extract_text import extract_text
from parser.utils import clean_text
from nlp.section_classifier import get_structured_sections

from scoring.semantic_matcher import semantic_match
from scoring.scorer import compute_score
from scoring.skill_gap import generate_skill_gap

from scoring.jd_matcher import match_resume_to_jd
from scoring.section_scorer import evaluate_sections

# NEW DB
from database.db import insert_result


pdf_path = "uploads/resume1.pdf"
role = "web_developer"

job_description = """
Looking for a web developer with strong skills in HTML, CSS, JavaScript,
React, Node.js, and API integration. Experience with Git is required.
"""

# STEP 1
text = extract_text(pdf_path)

# STEP 2
cleaned = clean_text(text)

# STEP 3
sections = get_structured_sections(cleaned)

# STEP 4
semantic_result = semantic_match(cleaned, role)

# STEP 5
final_score = compute_score(sections, semantic_result)

# STEP 6
skill_gap = generate_skill_gap(semantic_result)

# STEP 7
jd_score = match_resume_to_jd(cleaned, job_description)

# STEP 8
section_quality = evaluate_sections(sections)


# ===================================
# PRINT OUTPUT
# ===================================

print("\n===== FINAL SCORE =====")
print(final_score)

print("\n===== ROLE MATCH (ATS) =====")

print("\nMatched Skills:")
for m in semantic_result["matched"]:
    print(f"- {m[0]} ({m[1]})")

print("\nMissing MUST-HAVE Skills:")
for s in semantic_result["missing"]:
    print(f"- {s}")

print("\n===== JD MATCH SCORE =====")
print(f"{int(jd_score * 100)}%")

print("\n===== SECTION QUALITY =====")
for k, v in section_quality.items():
    print(f"{k.capitalize()}: {v}")

print("\n===== SKILL GAP ANALYSIS =====")

print("\nRecommendations:")
for r in skill_gap["recommendations"]:
    print(f"- {r}")

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

insert_result(db_data)

print("\n✅ Data stored in PostgreSQL successfully!")