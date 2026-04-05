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
        "Strong": "reads with depth and sufficient detail for ATS parsers.",
        "Moderate": "is present but could use more quantified outcomes and keywords.",
        "Weak": "is thin or missing; recruiters and ATS tools may under-score this area.",
    }.get(strength, "needs clearer structure and stronger keywords.")

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
        f"**Role profile:** {role_display}.",
        (
            "**ATS semantic matcher:** Your resume was compared against role must-have skills using "
            "embedding similarity. Each keyword is scored against your strongest matching lines."
        ),
        f"**Aggregate skill alignment (internal):** {semantic_result.get('score', 0):.2f} on a 0–1 scale "
        f"(mapped to **{ats_score_pct:.1f}%** overall ATS-style score after combining experience and education).",
    ]
    if matched_with_sim:
        ats_lines.append(
            "**Signals found:** " + ", ".join(matched_with_sim[:12])
            + ("…" if len(matched_with_sim) > 12 else "")
        )
    else:
        ats_lines.append("**Signals found:** No strong must-have matches above the similarity threshold.")

    if missing:
        ats_lines.append(
            "**Must-have gaps:** " + ", ".join(missing[:15]) + ("…" if len(missing) > 15 else "")
        )
    if optional:
        ats_lines.append(
            "**Optional / nice-to-have skills for this role:** " + ", ".join(optional[:10])
            + ("…" if len(optional) > 10 else "")
        )

    ats_matcher = "\n\n".join(ats_lines)

    # --- JD matcher ---
    jd_short = jd_text.strip()
    if len(jd_short) > 400:
        jd_short = jd_short[:400] + "…"
    jd_matcher = (
        "**Job description match:** The full resume text and the inferred target JD were embedded and "
        "compared with cosine similarity.\n\n"
        f"**Match score:** **{jd_match_pct:.1f}%** — higher means your wording and themes overlap more "
        "with the role summary below.\n\n"
        f"**Reference JD used:** {jd_short}"
    )

    # --- Composite scorer (scorer.py) ---
    composite_scorer = (
        "**Composite score (scorer):** Combines semantic skill alignment (~60%), experience "
        "section presence (~25%), and education signals (~15%).\n\n"
        f"**Raw composite (0–1):** {final_score_raw:.2f} → displayed as **{ats_score_pct:.1f}%** after scaling."
    )

    # --- Skill gap ---
    strong_by_cat = gap_result.get("strong_by_category") or {}
    missing_by_cat = gap_result.get("missing_by_category") or {}
    recs = gap_result.get("recommendations") or []

    gap_parts = [
        "**Skill gap analysis:** Groups matched and missing skills into categories (programming, frontend, "
        "backend, database, core CS, tools, other)."
    ]
    non_empty_missing = {k: v for k, v in missing_by_cat.items() if v}
    if non_empty_missing:
        gap_parts.append(
            "**Gaps by category:** "
            + "; ".join(f"{k}: {', '.join(v[:5])}" for k, v in list(non_empty_missing.items())[:8])
        )
    else:
        gap_parts.append("**Gaps by category:** No categorized gaps — must-have list may already be covered.")

    if non_empty_missing:
        gap_parts.append(
            "**Strengths by category (matched):** "
            + "; ".join(
                f"{k}: {', '.join(v[:5])}"
                for k, v in strong_by_cat.items()
                if v
            )[:800]
        )

    if recs:
        gap_parts.append("**Tailored recommendations:** " + " ".join(recs))

    skill_gap = "\n\n".join(gap_parts)

    # --- Section-wise (section_scorer + excerpts) ---
    education = _strength_paragraph(
        "Education",
        section_quality.get("education"),
        sections.get("education", ""),
    )
    experience = _strength_paragraph(
        "Experience",
        section_quality.get("experience"),
        sections.get("experience", ""),
    )
    projects = _strength_paragraph(
        "Projects",
        section_quality.get("projects"),
        sections.get("projects", ""),
    )

    recommendations_paragraph = (
        "**Recommendations:**\n\n"
        + "\n".join(f"• {r}" for r in recs)
        if recs
        else "• No specific gaps triggered automated recommendations; keep projects and metrics visible."
    )

    full_report_text = "\n\n---\n\n".join(
        [
            ats_matcher,
            jd_matcher,
            composite_scorer,
            skill_gap,
            education,
            experience,
            projects,
            recommendations_paragraph,
        ]
    )

    return {
        "overview": (
            f"This report summarizes your resume for **{role_display}**. "
            f"Overall ATS-style score: **{ats_score_pct:.1f}%**. JD alignment: **{jd_match_pct:.1f}%**."
        ),
        "ats_matcher": ats_matcher,
        "jd_matcher": jd_matcher,
        "composite_scorer": composite_scorer,
        "skill_gap": skill_gap,
        "education": education,
        "experience": experience,
        "projects": projects,
        "recommendations_paragraph": recommendations_paragraph,
        "full_report_text": full_report_text,
    }
