import pdfplumber
import fitz  # PyMuPDF


# -------------------------------
# 1. BASIC EXTRACTION (FAST PATH)
# -------------------------------
def extract_basic(page):
    return page.extract_text() or ""


# -------------------------------
# 2. TWO-COLUMN EXTRACTION
# -------------------------------
def extract_two_column(page):
    width = page.width

    left_bbox = (0, 0, width / 2, page.height)
    right_bbox = (width / 2, 0, width, page.height)

    left_text = page.within_bbox(left_bbox).extract_text() or ""
    right_text = page.within_bbox(right_bbox).extract_text() or ""

    return left_text + "\n" + right_text


# -------------------------------
# 3. COLUMN DETECTION HEURISTIC
# -------------------------------
def is_two_column(page):
    words = page.extract_words()
    if not words:
        return False

    x_positions = [w['x0'] for w in words]

    spread = max(x_positions) - min(x_positions)

    # If text spans wide area → likely 2 columns
    return spread > page.width * 0.6


# -------------------------------
# 4. PDFPLUMBER MAIN EXTRACTION
# -------------------------------
def extract_with_pdfplumber(pdf_path):
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:

                if is_two_column(page):
                    page_text = extract_two_column(page)
                else:
                    page_text = extract_basic(page)

                text += page_text + "\n"

    except Exception as e:
        print(f"[pdfplumber ERROR]: {e}")

    return text.strip()


# -------------------------------
# 5. PYMUPDF BLOCK EXTRACTION (FALLBACK)
# -------------------------------
def extract_with_pymupdf_blocks(pdf_path):
    text = ""

    try:
        doc = fitz.open(pdf_path)

        for page in doc:
            blocks = page.get_text("blocks")

            # Sort blocks top-to-bottom, then left-to-right
            blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

            for block in blocks:
                block_text = block[4].strip()
                if block_text:
                    text += block_text + "\n"

    except Exception as e:
        print(f"[PyMuPDF ERROR]: {e}")

    return text.strip()


# -------------------------------
# 6. FINAL HYBRID FUNCTION
# -------------------------------
def extract_text(pdf_path):
    """
    Unified extraction pipeline:
    1. Try pdfplumber (with column detection)
    2. If output is poor → fallback to PyMuPDF blocks
    """

    text = extract_with_pdfplumber(pdf_path)

    # Fallback condition
    if not text or len(text.split()) < 50:
        print("[INFO] Falling back to PyMuPDF block extraction...")
        text = extract_with_pymupdf_blocks(pdf_path)

    return text.strip()