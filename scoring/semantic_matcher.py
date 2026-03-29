import json
from sklearn.metrics.pairwise import cosine_similarity
from models.embedding_model import get_embedding


def load_keywords():
    with open("data/ats_keywords.json", "r") as f:
        return json.load(f)


NORMALIZATION_MAP = {
    "html5": "html",
    "css3": "css",
    "js": "javascript",
    "node.js": "node",
    "react.js": "react",
    "express.js": "express",
    "dsa": "data structures algorithms",
    "data structures and algorithms": "data structures algorithms",
    "os": "operating system"
}


def normalize(text):
    text = text.lower()
    for k, v in NORMALIZATION_MAP.items():
        text = text.replace(k, v)
    return text


def semantic_match(resume_text, role):
    data = load_keywords()

    role_data = data[role]

    must_have = role_data["must_have"]
    optional = role_data["optional"]

    # Normalize resume
    resume_text = normalize(resume_text)

    lines = list(set([
        normalize(l.strip())
        for l in resume_text.split("\n")
        if len(l.strip()) > 10
    ]))

    line_embeddings = get_embedding(lines)
    keyword_embeddings = get_embedding(must_have)

    matched = []
    missing = []
    scores = []

    for i, keyword_emb in enumerate(keyword_embeddings):
        sims = cosine_similarity([keyword_emb], line_embeddings)[0]

        best_score = max(sims)
        scores.append(best_score)

        keyword = must_have[i]

        if best_score > 0.4:
            matched.append((keyword, round(float(best_score), 2)))
        else:
            missing.append(keyword)

    final_score = sum(scores) / len(scores)

    return {
        "role": role,
        "score": round(float(final_score), 2),
        "matched": matched,
        "missing": missing,
        "optional_skills": optional
    }