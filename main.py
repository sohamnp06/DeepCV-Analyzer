from parser.extract_text import extract_text
from parser.utils import clean_text
from nlp.section_classifier import get_structured_sections

from scoring.semantic_matcher import semantic_match
from scoring.scorer import compute_score
from scoring.skill_gap import generate_skill_gap


pdf_path = "uploads/resume2.pdf"
role = "web_developer"

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

# STEP 6 (NEW)
skill_gap = generate_skill_gap(semantic_result)


print("\n===== SEMANTIC MATCH RESULT =====")
print(semantic_result)

print("\n===== FINAL SCORE =====")
print(final_score)

print("\n===== SECTIONS =====")
for k, v in sections.items():
    print(f"\n--- {k.upper()} ---")
    print(v[:200])


# 🔥 NEW OUTPUT
print("\n===== SKILL GAP ANALYSIS =====")

print("\nStrong Skills:")
for s in skill_gap["strong"]:
    print(f"- {s}")

print("\nMissing Skills:")
for s in skill_gap["missing"]:
    print(f"- {s}")

print("\nRecommendations:")
for r in skill_gap["recommendations"]:
    print(f"- {r}")