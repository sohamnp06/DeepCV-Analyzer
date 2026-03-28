import json
from sklearn.metrics.pairwise import cosine_similarity
from models.embedding_model import get_embedding


def load_keywords(path="data/ats_keywords.json"):
    with open(path, "r") as f:
        return json.load(f)


def semantic_match(resume_text, role):
    keywords_data = load_keywords()
    role = role.lower().replace(" ", "_")

    keywords = keywords_data[role]

    lines = [l.strip() for l in resume_text.split("\n") if l.strip()]

    matched = []
    missing = []
    keyword_scores = []

    for keyword in keywords:
        keyword_emb = get_embedding(keyword)

        best_score = 0

        for line in lines:
            line_emb = get_embedding(line)

            sim = cosine_similarity(
                [keyword_emb],
                [line_emb]
            )[0][0]

            best_score = max(best_score, sim)

        keyword_scores.append(best_score)

        if best_score > 0.4:
            matched.append((keyword, round(best_score, 2)))
        else:
            missing.append(keyword)

    final_score = sum(keyword_scores) / len(keyword_scores)

    return {
        "role": role,
        "score": round(final_score, 2),
        "matched": matched,
        "missing": missing
    }