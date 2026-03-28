def compute_score(sections, semantic_result):
    skill_score = semantic_result["score"]

    exp_score = 1 if len(sections.get("experience", "")) > 50 else 0.6
    edu_score = 1 if "btech" in sections.get("education", "") else 0.6

    final = (0.6 * skill_score) + (0.25 * exp_score) + (0.15 * edu_score)

    return round(final, 2)