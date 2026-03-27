from parser.extract_text import extract_text
from parser.utils import clean_text
from nlp.section_classifier import get_structured_sections
from scoring.ats_matcher import match_keywords
from scoring.scorer import compute_score


pdf_path = "uploads/resume2.pdf"
role = "web_developer"   # change dynamically later

# Step 1
text = extract_text(pdf_path)

# Step 2
cleaned = clean_text(text)
sections = get_structured_sections(cleaned)

# Step 3
ats_result = match_keywords(cleaned, role)
final_score = compute_score(sections, ats_result)


print("\n===== ATS RESULT =====")
print(ats_result)

print("\n===== FINAL SCORE =====")
print(final_score)