import json
from sklearn.metrics.pairwise import cosine_similarity
from models.embedding_model import get_embedding


def load_keywords():
    with open("data/ats_keywords.json", "r") as f:
        return json.load(f)


def semantic_match(resume_text, role):
    data = load_keywords()
    keywords = data[role]

    lines = list(set([l.strip() for l in resume_text.split("\n") if len(l.strip()) > 10]))

    # 🔥 BATCH EMBEDDING (VERY IMPORTANT)
    line_embeddings = get_embedding(lines)
    keyword_embeddings = get_embedding(keywords)

    matched = []
    missing = []
    scores = []

    for i, keyword_emb in enumerate(keyword_embeddings):
        sims = cosine_similarity([keyword_emb], line_embeddings)[0]

        best_score = max(sims)
        scores.append(best_score)

        if best_score > 0.4:
            matched.append((keywords[i], round(float(best_score), 2)))
        else:
            missing.append(keywords[i])

    final_score = sum(scores) / len(scores)

    return {
        "role": role,
        "score": round(float(final_score), 2),
        "matched": matched,
        "missing": missing
    }