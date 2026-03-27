from parser.extract_text import extract_text
from parser.utils import clean_text
from nlp.section_classifier import get_structured_sections

pdf_path = "uploads/resume2.pdf"

text = extract_text(pdf_path)
cleaned = clean_text(text)

sections = get_structured_sections(cleaned)

sections = get_structured_sections(cleaned)

for key, value in sections.items():
    print(f"\n--- {key.upper()} ---")
    print(value[:300])