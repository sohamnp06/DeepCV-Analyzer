"""
Structured narrative descriptions for the analysis report.
Uses outputs from semantic_matcher, jd_matcher, scorer, section_scorer, skill_gap.
"""

import html


def _strength_paragraph(label: str, strength: str, excerpt: str, max_words: int = 60) -> str:
    strength = (strength or "Weak").strip()
    text = html.escape((excerpt or "").strip())
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words]) + "…"

    tone = {
        "Strong": "is well-written and provides good details about your background.",
        "Moderate": "shows potential but could be improved with more specific results and achievements.",
        "Weak": "needs more detail. Try adding more information about your specific contributions and responsibilities.",
    }.get(strength, "could be clearer. Try focusing on your main tasks and how they relate back to the role.")

    if not text:
        return (
            f"The **{label}** section is **{strength}** compared to typical profiles: content "
            f"{tone} Consider expanding with concrete examples."
        )

    return (
        f"The **{label}** section is rated **{strength}**. Sample content suggests the candidate "
        f"{tone} Excerpt: {text}"
    )


def build_analysis_narrative(
    role_display: str,
    jd_text: str,
    ats_score_pct: float,
    jd_match_pct: float,
    final_score_raw: float,
    semantic_result: dict,
    section_quality: dict,
    gap_result: dict,
    sections: dict,
) -> dict:
    """
    Returns human-readable paragraphs keyed by analysis area.
    """
    matched = semantic_result.get("matched") or []
    missing = semantic_result.get("missing") or []
    optional = semantic_result.get("optional_skills") or []

    matched_list = [m[0] if isinstance(m, (list, tuple)) else m for m in matched]
    matched_with_sim = [
        f"{m[0]} (~{m[1]})" if isinstance(m, (list, tuple)) and len(m) > 1 else str(m)
        for m in matched
    ]

    # --- ATS / semantic matcher ---
    ats_lines = [
        f"**Role Profile:** {role_display}",
        "We checked your resume for the most important skills required for this role. Here is what we found:",
    ]
    if matched_list:
        ats_lines.append("**Your Matching Skills:** " + ", ".join(matched_list[:12]))
    else:
        ats_lines.append("**Your Matching Skills:** No direct matches found for the core requirements yet.")

    if missing:
        ats_lines.append("**Skills to Add:** " + ", ".join(missing[:10]))
    if optional:
        ats_lines.append("**Other Relevant Skills:** " + ", ".join(optional[:10]))

    ats_matcher = "\n\n".join(ats_lines)

    # --- JD matcher ---
    jd_short = jd_text.strip()
    if len(jd_short) > 300:
        jd_short = jd_short[:300] + "..."
    
    jd_matcher = (
        "We compared your entire resume against the job description to see how well your overall profile aligns with the role.\n\n"
        f"**Matching Score:** **{jd_match_pct:.0f}%**\n\n"
        f"**Target Requirements:** {jd_short}"
    )

    # --- Skill gap ---
    non_empty_missing = {k: v for k, v in gap_result.get("missing_by_category", {}).items() if v}
    gap_parts = ["**Key Gaps Identified:**"]
    if non_empty_missing:
        gap_parts.append("; ".join(f"{k.capitalize()}: {', '.join(v[:3])}" for k, v in list(non_empty_missing.items())[:5]))
    else:
        gap_parts.append("Your skills are well-aligned with the core requirements of this role.")

    skill_gap = "\n\n".join(gap_parts)

    # --- Section-wise ---
    education = _strength_paragraph("Education", section_quality.get("education"), sections.get("education", ""))
    experience = _strength_paragraph("Experience", section_quality.get("experience"), sections.get("experience", ""))
    projects = _strength_paragraph("Projects", section_quality.get("projects"), sections.get("projects", ""))

    # --- Enhanced Recommendations Logic ---
    recs = gap_result.get("recommendations") or []
    detailed_recs = []
    
    # 1. Skill-based deep dives
    for r in recs:
        if "frontend" in r.lower():
            detailed_recs.append("📊 **Frontend Specialist:** Beyond just HTML/CSS, focus on mastering architectural patterns in React or Vue. Implement advanced state management (Redux/Zustand) to stand out from junior developers.")
        elif "backend" in r.lower():
            detailed_recs.append("⚙️ **Backend Engineering:** Strengthen your understanding of Database indexing and API performance. Consider building a microservice-oriented project to demonstrate scalability knowledge.")
        elif "core cs" in r.lower():
            detailed_recs.append("🧠 **CS Fundamentals:** High-scoring profiles often demonstrate strong DSA skills. We recommend solving 'hard' categorized problems on LeetCode focusing on Dynamic Programming and Graphs.")
        elif "tools" in r.lower():
            detailed_recs.append("🛠️ **DevOps & Tooling:** Modern roles require more than just code. Dockerize your current projects and explore CI/CD pipelines (GitHub Actions) to show you can handle production-level deployments.")
        else:
            detailed_recs.append(f"✅ {r}")

    # 2. Section-based advice
    if section_quality.get("projects") == "Weak":
        detailed_recs.append("📁 **Project Portfolio:** Your projects section is currently thin. Add 2-3 deep-dive projects that solve a real-world problem, ideally with a live link and a clear README.")
    if section_quality.get("experience") == "Weak":
        detailed_recs.append("💼 **Experience Metrics:** To pass senior ATS filters, transform your experience bullet points from 'tasks' into 'achievements.' Use the STAR method (Situation, Task, Action, Result) with real numbers.")

    recommendations_list = (
        "\n\n".join(detailed_recs[:6])
        if detailed_recs
        else "• Your profile is well-rounded. Focus on fine-tuning your summary to highlight your unique USP for this specific role."
    )
    recommendations_paragraph = "**Strategic Recommendations:**\n\n" + recommendations_list

    full_report_text = "\n\n---\n\n".join([
        ats_matcher,
        jd_matcher,
        skill_gap,
        education,
        experience,
        projects,
        recommendations_paragraph,
    ])

    return {
        "overview": f"Our analysis shows that your profile is currently a **{ats_score_pct:.0f}%** match for the **{role_display}** role. You have a solid foundation, especially in your matching skills, but there are clear areas where expanding your technical depth would significantly boost your ranking.",
        "ats_matcher": ats_matcher,
        "jd_matcher": jd_matcher,
        "skill_gap": skill_gap,
        "education": education,
        "experience": experience,
        "projects": projects,
        "recommendations_paragraph": recommendations_paragraph,
        "full_report_text": full_report_text,
    }
