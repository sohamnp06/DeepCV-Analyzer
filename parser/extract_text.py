import pdfplumber
import fitz


def extract_text_safe(page):
    try:
        return page.extract_text() or ""
    except:
        return ""


def extract_two_column_safe(page):
    width = page.width
    height = page.height

    try:
        left_bbox = (0, max(0, page.bbox[1]), width / 2, height)
        right_bbox = (width / 2, max(0, page.bbox[1]), width, height)

        left_text = page.within_bbox(left_bbox).extract_text() or ""
        right_text = page.within_bbox(right_bbox).extract_text() or ""

        return left_text + "\n" + right_text

    except:
        return extract_text_safe(page)


def is_two_column(page):
    try:
        words = page.extract_words()
        if not words:
            return False

        x_positions = [w['x0'] for w in words]
        spread = max(x_positions) - min(x_positions)

        return spread > page.width * 0.6

    except:
        return False


def extract_with_pdfplumber(pdf_path):
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:

                if is_two_column(page):
                    page_text = extract_two_column_safe(page)
                else:
                    page_text = extract_text_safe(page)

                text += page_text + "\n"

    except Exception as e:
        print(f"[pdfplumber ERROR]: {e}")

    return text.strip()


def extract_with_pymupdf(pdf_path):
    text = ""

    try:
        doc = fitz.open(pdf_path)

        for page in doc:
            blocks = page.get_text("blocks")

            blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

            for block in blocks:
                if block[4].strip():
                    text += block[4] + "\n"

    except Exception as e:
        print(f"[PyMuPDF ERROR]: {e}")

    return text.strip()


def extract_text(pdf_path):
    text = extract_with_pdfplumber(pdf_path)

    # fallback condition
    if not text or len(text.split()) < 50:
        print("[INFO] Falling back to PyMuPDF block extraction...")
        text = extract_with_pymupdf(pdf_path)

    return text