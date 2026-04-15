import re


def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[^\w\s\.\,\-\+\#]', '', text)
    text = text.lower()
    return text.strip()