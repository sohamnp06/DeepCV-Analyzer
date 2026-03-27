import re


def clean_text(text):
    # Normalize spaces
    text = re.sub(r'\n+', '\n', text)

    # Remove weird symbols but keep useful ones
    text = re.sub(r'[^\w\s\.\,\-\+\#]', '', text)

    # Lowercase for NLP consistency
    text = text.lower()

    return text.strip()