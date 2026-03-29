from models.embedding_model import get_embedding
from sklearn.metrics.pairwise import cosine_similarity


def match_resume_to_jd(resume_text, jd_text):
    resume_emb = get_embedding([resume_text])
    jd_emb = get_embedding([jd_text])

    score = cosine_similarity(resume_emb, jd_emb)[0][0]

    return round(float(score), 2)