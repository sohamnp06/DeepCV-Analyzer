from parser.extract_text import extract_text
from parser.utils import clean_text
from nlp.section_classifier import get_structured_sections

from scoring.semantic_matcher import semantic_match
from scoring.scorer import compute_score
from scoring.skill_gap import generate_skill_gap


pdf_path = "uploads/resume2.pdf"
role = "web_developer"


# -----------------------------------
# STEP 1: Extract
# -----------------------------------
text = extract_text(pdf_path)

# -----------------------------------
# STEP 2: Clean
# -----------------------------------
cleaned = clean_text(text)

# -----------------------------------
# STEP 3: Sections
# -----------------------------------
sections = get_structured_sections(cleaned)

# -----------------------------------
# STEP 4: Semantic Matching
# -----------------------------------
semantic_result = semantic_match(cleaned, role)

# -----------------------------------
# STEP 5: Final Score
# -----------------------------------
final_score = compute_score(sections, semantic_result)

# -----------------------------------
# STEP 6: Skill Gap
# -----------------------------------
skill_gap = generate_skill_gap(semantic_result)


# ===================================
# HELPER FUNCTION
# ===================================
def get_strength_label(score):
    if score >= 0.85:
        return "Strong"
    elif score >= 0.65:
        return "Medium"
    else:
        return "Weak"


# ===================================
# OUTPUT
# ===================================

print("\n" + "="*50)
print("FINAL SCORE:", final_score)
print("="*50)


# -----------------------------------
# 🔥 FORCE SHOW SCORE BREAKDOWN
# -----------------------------------
skill_score = semantic_result["score"]
skill_percent = int(skill_score * 100)

exp_len = len(sections.get("experience", ""))
exp_score = 1 if exp_len > 80 else 0.7 if exp_len > 40 else 0.4

edu_text = sections.get("education", "")
edu_score = 1 if ("btech" in edu_text or "bachelor" in edu_text) else 0.6

print("\n" + "="*50)
print("SCORE BREAKDOWN")
print("="*50)

print(f"Skills Match        : {skill_percent}%")
print(f"Experience Strength : {get_strength_label(exp_score)}")
print(f"Education Strength  : {get_strength_label(edu_score)}")


# -----------------------------------
# SECTIONS
# -----------------------------------
print("\n" + "="*50)
print("SECTIONS")
print("="*50)

for k, v in sections.items():
    print(f"\n--- {k.upper()} ---")
    print(v[:200])


# -----------------------------------
# SKILL GAP ANALYSIS
# -----------------------------------
print("\n" + "="*50)
print("SKILL GAP ANALYSIS")
print("="*50)

print("\nStrong Skills:")
for s in skill_gap["strong"]:
    print(f"- {s}")

print("\nMissing Skills:")
for s in skill_gap["missing"]:
    print(f"- {s}")

print("\nRecommendations:")
for r in skill_gap["recommendations"]:
    print(f"- {r}")


# -----------------------------------
# PROFILE SUMMARY
# -----------------------------------
print("\n" + "="*50)
print("PROFILE SUMMARY")
print("="*50)

strengths = []
weaknesses = []

if skill_score >= 0.6:
    strengths.append("Good alignment with required skills")

if exp_score >= 0.7:
    strengths.append("Decent practical experience")

if edu_score >= 0.85:
    strengths.append("Strong educational background")

if skill_score < 0.5:
    weaknesses.append("Low skill match for target role")

if exp_score < 0.6:
    weaknesses.append("Limited experience")

if len(skill_gap["missing"]) > 5:
    weaknesses.append("Multiple critical skill gaps")

print("\nStrengths:")
for s in strengths:
    print(f"- {s}")

print("\nWeaknesses:")
for w in weaknesses:
    print(f"- {w}")