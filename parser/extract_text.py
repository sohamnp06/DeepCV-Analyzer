import pdfplumber
import fitz  


def extract_with_pdfplumber(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[pdfplumber ERROR]: {e}")
    return text


def extract_with_pymupdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + "\n"
    except Exception as e:
        print(f"[PyMuPDF ERROR]: {e}")
    return text


def extract_text(pdf_path):
    """
    Hybrid extraction:
    1. Try pdfplumber
    2. If empty → fallback to PyMuPDF
    """
    text = extract_with_pdfplumber(pdf_path)

    if not text.strip():
        print("[INFO] Falling back to PyMuPDF...")
        text = extract_with_pymupdf(pdf_path)

    return text.strip()