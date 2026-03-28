from parser.extract_text import extract_text
from parser.utils import clean_text
from nlp.section_classifier import get_structured_sections
from scoring.semantic_matcher import semantic_match
from scoring.scorer import compute_score


pdf_path = "uploads/resume1.pdf"
role = "software_developer"

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


print("\n===== SEMANTIC MATCH RESULT =====")
print(semantic_result)

print("\n===== FINAL SCORE =====")
print(final_score)

print("\n===== SECTIONS =====")
for k, v in sections.items():
    print(f"\n--- {k.upper()} ---")
    print(v[:200])