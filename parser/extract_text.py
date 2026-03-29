import fitz  # PyMuPDF


def extract_text(pdf_path):
    text = ""

    try:
        doc = fitz.open(pdf_path)

        for page in doc:
            blocks = page.get_text("blocks")

            blocks = [b for b in blocks if b[4].strip()]

            # Better column-aware sort
            blocks = sorted(blocks, key=lambda b: (round(b[0] / 100) * 100, b[1]))

            for block in blocks:
                line = block[4].replace("\n", " ").strip()

                if len(line) > 2:
                    text += line + "\n"

    except Exception as e:
        print(f"[ERROR]: {e}")

    return text