from parser.extract_text import extract_text
from parser.utils import clean_text

pdf_path = "uploads/resume2.pdf"

raw_text = extract_text(pdf_path)
cleaned_text = clean_text(raw_text)

print("----- RAW TEXT -----")
print(raw_text[:1000])

print("\n----- CLEANED TEXT -----")
print(cleaned_text[:1000])