import json


def load_keywords(path="data/ats_keywords.json"):
    with open(path, "r") as f:
        return json.load(f)


def match_keywords(resume_text, role):
    keywords_data = load_keywords()

    role = role.lower().replace(" ", "_")

    if role not in keywords_data:
        raise ValueError(f"Role '{role}' not found in ATS keywords")

    keywords = keywords_data[role]

    resume_text = resume_text.lower()

    matched = []
    missing = []

    for keyword in keywords:
        if keyword in resume_text:
            matched.append(keyword)
        else:
            missing.append(keyword)

    score = len(matched) / len(keywords)

    return {
        "role": role,
        "score": round(score, 2),
        "matched": matched,
        "missing": missing
    }