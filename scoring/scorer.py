def compute_score(sections, ats_result):
    skill_score = ats_result["score"]

    # Experience boost
    exp_text = sections.get("experience", "")
    experience_score = 1 if len(exp_text) > 50 else 0.5

    # Education boost
    edu_text = sections.get("education", "")
    education_score = 1 if "btech" in edu_text or "bachelor" in edu_text else 0.5

    # Final weighted score
    final_score = (
        0.5 * skill_score +
        0.3 * experience_score +
        0.2 * education_score
    )

    return round(final_score, 2)