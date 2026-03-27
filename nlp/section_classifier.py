import re


SECTION_KEYWORDS = {
    "education": ["education", "btech", "mtech", "bachelor", "master", "university"],
    "experience": ["experience", "intern", "developer", "engineer", "company"],
    "skills": ["skills", "python", "java", "sql", "react"],
    "projects": ["project", "built", "developed"],
    "summary": ["summary", "profile", "about", "objective"]
}


def clean_line(line):
    line = line.strip().lower()

    # remove very noisy lines
    if len(line) < 3:
        return None

    if re.match(r'^\d+$', line):
        return None

    return line


def score_line(line):
    scores = {k: 0 for k in SECTION_KEYWORDS}

    for section, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if kw in line:
                scores[section] += 1

    return scores


def classify_line(line):
    scores = score_line(line)

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return "other"

    return best


def classify_sections(text):
    sections = {
        "education": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "summary": [],
        "other": []
    }

    for line in text.split("\n"):
        line = clean_line(line)
        if not line:
            continue

        section = classify_line(line)
        sections[section].append(line)

    # join results
    for key in sections:
        sections[key] = " ".join(sections[key])

    return sections


def get_structured_sections(text):
    return classify_sections(text)