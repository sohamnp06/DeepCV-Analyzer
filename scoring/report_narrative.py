"""
Structured narrative descriptions for the analysis report.
Uses outputs from semantic_matcher, jd_matcher, scorer, section_scorer, skill_gap.
"""

import html


def _strength_paragraph(label: str, strength: str, excerpt: str, max_words: int = 80) -> str:
    strength = (strength or "Weak").strip()
    text = html.escape((excerpt or "").strip())
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words]) + "…"

    # Richer tone mapping
    mapping = {
        "Strong": (
            f"Your **{label}** section is exemplary. It uses strong action verbs and quantifiable metrics "
            f"that set you apart as a results-driven professional. Maintain this level of detail to "
            f"consistently pass rigorous technical reviews."
        ),
        "Moderate": (
            f"The **{label}** section shows a solid foundation but lacks the 'impact punch' needed for top-tier roles. "
            f"We recommend shifting focus from what you *did* to what you *achieved*. Use numbers (e.g., 'Reduced latency by 20%') "
            f"to make your contributions undeniable."
        ),
        "Weak": (
            f"Currently, the **{label}** section is underselling your potential. It reads more like a job description "
            f"than a highlight of your personal expertise. You need to add specific technical details, "
            f"problem-solving instances, and clear outcomes to meet modern ATS standards."
        ),
    }
    
    tone = mapping.get(strength, "The section content could be more focused on role-specific outcomes.")

    if not text:
        return (
            f"Our analysis indicates that the **{label}** section needs significant expansion. "
            f"{tone} Profiles without this data often struggle with high-volume recruiter screenings."
        )

    return (
        f"{tone}\n\n"
        f"> **Current Excerpt Analysis:** {text}"
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

    # --- ATS Matcher ---
    ats_lines = [
        f"## 🎯 Role Compatibility Analysis: {role_display}",
        f"Your profile shows a **{ats_score_pct:.0f}%** match with the core skills required for a {role_display} role."
    ]
    if matched_list:
        ats_lines.append(f"✅ **Core Strengths:** Expert level proficiency in: {', '.join(matched_list[:10])}.")
    
    if missing:
        ats_lines.append(f"🚩 **Critical Gaps:** To reach high-priority screening thresholds, add depth in: {', '.join(missing[:8])}.")

    ats_matcher = "\n\n".join(ats_lines)

    # --- JD Matcher ---
    jd_short = jd_text.strip()
    if len(jd_short) > 250:
        jd_short = jd_short[:250] + "..."
    
    jd_matcher = (
        "## 🔍 Strategic Context Fit\n\n"
        f"Your profile alignment sits at **{jd_match_pct:.0f}%** when compared directly to the job description requirements.\n\n"
        f"> **Target Requirements Baseline:** {jd_short}"
    )

    # --- Areas of Improvement (Detailed Skill Gap) ---
    non_empty_missing = {k: v for k, v in gap_result.get("missing_by_category", {}).items() if v}
    gap_parts = ["## 🚧 Areas for Improvement"]
    
    if non_empty_missing:
        gap_parts.append("To bridge your current gap to industry-standard expert levels, we recommend focusing on these categorical improvements:")
        for cat, skills in list(non_empty_missing.items())[:4]:
            cat_label = cat.replace("_", " ").title()
            
            # Context-aware impacts
            impact_map = {
                "Core Cs": "Essential for passing deep-drill technical interviews and solving complex engineering problems.",
                "Frontend": "Critical for building responsive, high-retention user interfaces and mastering modern UI logic.",
                "Backend": "Ensures your infrastructure is secure, idempotent, and performs well under high concurrent load.",
                "Database": "The difference between applications that just function and those that scale efficiently.",
                "Cloud": "Deployment expertise is a must-have for modern DevOps-oriented engineering roles.",
                "Tools": "Mastering professional dev-tooling indicates you're ready for high-velocity agile sprints.",
                "Programming": "Showing depth in multiple paradigms demonstrates high adaptability to new tech stacks.",
            }
            impact = impact_map.get(cat_label, "Adding depth here will immediately increase your value to potential employers.")
            
            gap_parts.append(f"🚩 **{cat_label}:** Missing {', '.join(skills[:3])}. **Impact:** {impact}")
    else:
        gap_parts.append("Your technical skill set is exceptionally well-balanced. Your next strategic step is toward leadership and architecture.")

    skill_gap = "\n\n".join(gap_parts)

    # --- Section Quality ---
    education = _strength_paragraph("Educational Foundation", section_quality.get("education"), sections.get("education", ""))
    experience = _strength_paragraph("Professional Experience", section_quality.get("experience"), sections.get("experience", ""))
    projects = _strength_paragraph("Technical Portfolio", section_quality.get("projects"), sections.get("projects", ""))

    # --- Strategic Recommendations ---
    recs = gap_result.get("recommendations") or []
    detailed_recs = ["## 💡 Strategic Career Recommendations"]
    
    if ats_score_pct < 60:
        detailed_recs.append("- **Transition Strategy:** Your score indicates a possible role transition. Build 'Capstone Projects' that focus exclusively on the core technical gaps identified.")
    
    # Map raw recommendations to high-descriptiveness versions
    for r in recs:
        r_low = r.lower()
        if "frontend" in r_low:
            detailed_recs.append("- **Advanced Frontend Architecture:** Master architectural patterns like Redux or Context API. Focus on mastering 'React Hooks' and explore Server-Side Rendering (SSR) via Next.js for high-impact performance.")
        elif "backend" in r_low:
            detailed_recs.append("- **Scalable Backend Systems:** Move beyond basic CRUD. Implement caching strategies (Redis), asynchronous task processing (Celery), and secure OAuth/JWT authentication pipelines.")
        elif "cs core" in r_low or "fundamentals" in r_low:
            detailed_recs.append("- **Computer Science Foundations:** Deepen your understanding of Big-O complexity, Graph algorithms, and Database Internals. This depth is what separates senior engineers from juniors.")
        elif "devops" in r_low or "tools" in r_low:
            detailed_recs.append("- **Cloud & DevOps Proficiency:** Set up automated CI/CD pipelines using GitHub Actions. Dockerize your environments to ensure 'write once, run anywhere' production-readiness.")
        elif "data science" in r_low or "ml" in r_low:
            detailed_recs.append("- **Machine Learning Engineering:** Shift from running scripts to building models-as-a-service. Focus on MLOps pipelines—how to deploy, monitor, and scale models in a production ecosystem.")
        elif "cloud" in r_low:
            detailed_recs.append("- **Public Cloud Architecture:** Architect for the cloud first. Master VPCs, IAM security roles, and serverless architectures on platforms like AWS, GCP, or Azure.")
        else:
            detailed_recs.append(f"- {r}")

    # Add experience/project specific polish
    if section_quality.get("experience") == "Weak":
        detailed_recs.append("- **Impact-Driven Experience:** Transform your professional bullets. Replace work 'tasks' with 'results.' Use metrics like 'Improved efficiency by 30%' or 'Reduced code-base bugs by 15%'.")

    # This creates a single block that starts with - and our renderer will turn it into a <ul>
    recommendations_paragraph = "\n".join(detailed_recs)

    # Final Construction
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
        "overview": f"Your profile is a **{ats_score_pct:.0f}%** match for the **{role_display}** role. You have a solid foundation, especially in your matched core competencies. To emerge as a top 5% candidate, we recommend focusing on the specific architectural and metrics-driven improvements outlined in this report.",
        "ats_matcher": ats_matcher,
        "jd_matcher": jd_matcher,
        "skill_gap": skill_gap,
        "education": education,
        "experience": experience,
        "projects": projects,
        "recommendations_paragraph": recommendations_paragraph,
        "full_report_text": full_report_text,
    }
