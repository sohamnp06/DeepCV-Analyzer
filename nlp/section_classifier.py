import re


SECTION_HEADERS = {
    "education": ["education", "academic", "qualification"],
    "experience": ["experience", "work experience", "employment"],
    "skills": ["skills", "technical skills"],
    "projects": ["projects"],
    "summary": ["summary", "profile", "about", "objective"]
}


def is_header(line):
    line = line.lower().strip()

    for section, keywords in SECTION_HEADERS.items():
        for kw in keywords:
            # strong header match (short + keyword)
            if kw in line and len(line.split()) <= 4:
                return section

    return None


def get_structured_sections(text):
    sections = {
        "education": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "summary": [],
        "other": []
    }

    current_section = "other"

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for line in lines:
        detected = is_header(line)

        if detected:
            current_section = detected
            continue

        # assign content to current section
        sections[current_section].append(line)

    # join text
    for key in sections:
        sections[key] = " ".join(sections[key])

    return sections