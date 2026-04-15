import re

EXPERIENCE_ACTION_VERBS = [
    "led", "managed", "built", "developed", "designed", "implemented",
    "improved", "reduced", "optimized", "architected", "deployed", "launched",
    "created", "delivered", "collaborated", "automated", "integrated", "scaled",
    "mentored", "analyzed", "engineered", "migrated", "refactored", "maintained",
    "increased", "decreased", "established", "spearheaded", "pioneered", "directed",
    "coordinated", "streamlined", "enhanced", "resolved", "authored", "contributed",
    "executed", "demonstrated", "transformed", "leveraged", "owned", "shipped",
]

PROJECT_TECH_SIGNALS = [
    "github", "deployed", "hosted", "api", "machine learning", "neural",
    "database", "frontend", "backend", "model", "trained", "integrated",
    "react", "node", "django", "flask", "tensorflow", "pytorch", "docker",
    "aws", "python", "javascript", "typescript", "sql", "mongodb", "rest",
    "graphql", "kubernetes", "fastapi", "spring", "vue", "angular", "redis",
    "postgresql", "firebase", "next.js", "express", "nlp", "deep learning",
    "classification", "regression", "opencv", "microservice", "ci/cd",
]

METRIC_PATTERN = re.compile(
    r"(\d+\s*%"
    r"|\d+\s*x\b"
    r"|\d+\+?\s*(users|ms|seconds|hours|days|months|years|requests|calls|queries"
    r"|records|lines|modules|services|bugs|errors|features|endpoints|apis|points|times|commits|repos|stars|forks))",
    re.IGNORECASE,
)


def _count_metrics(text: str) -> int:
    return len(METRIC_PATTERN.findall(text))


def _count_action_verbs(text: str, verb_list: list) -> list:
    text_lower = text.lower()
    return [v for v in verb_list if re.search(r"\b" + re.escape(v) + r"\b", text_lower)]


def get_section_diagnostics(text: str, section_type: str) -> dict:
    if not text:
        return {"word_count": 0}

    diag = {"word_count": len(text.split())}

    if section_type == "experience":
        verbs = _count_action_verbs(text, EXPERIENCE_ACTION_VERBS)
        diag["action_verbs_found"] = verbs
        diag["action_verb_count"] = len(verbs)
        diag["metric_count"] = _count_metrics(text)

    elif section_type == "projects":
        found = [sig for sig in PROJECT_TECH_SIGNALS if sig in text.lower()]
        diag["tech_signals_found"] = found
        diag["tech_signal_count"] = len(found)
        diag["metric_count"] = _count_metrics(text)
        diag["has_github"] = "github" in text.lower()
        diag["has_deployment"] = any(k in text.lower() for k in ["deployed", "hosted", "live", "vercel", "netlify", "heroku", "render", "aws"])

    return diag


def score_experience_section(text: str) -> str:
    if not text or len(text.strip()) < 10:
        return "Weak"

    wc        = len(text.split())
    verb_hits = _count_action_verbs(text, EXPERIENCE_ACTION_VERBS)
    metrics   = _count_metrics(text)

    word_pts   = 30 if wc >= 150 else (25 if wc >= 80 else (15 if wc >= 30 else 5))
    verb_pts   = min(len(verb_hits) * 8, 40)
    metric_pts = min(metrics * 10, 30)

    total = word_pts + verb_pts + metric_pts

    if total >= 60:
        return "Strong"
    elif total >= 30:
        return "Moderate"
    return "Weak"


def score_projects_section(text: str) -> str:
    if not text or len(text.strip()) < 10:
        return "Weak"

    text_lower   = text.lower()
    wc           = len(text.split())
    tech_hits    = sum(1 for sig in PROJECT_TECH_SIGNALS if sig in text_lower)
    metrics      = _count_metrics(text)
    has_deploy   = any(k in text_lower for k in ["deployed", "hosted", "live", "vercel", "netlify", "heroku", "render", "aws", "github"])

    word_pts   = 30 if wc >= 150 else (25 if wc >= 80 else (15 if wc >= 30 else 5))
    tech_pts   = min(tech_hits * 5, 40)
    metric_pts = min((metrics * 10) + (10 if has_deploy else 0), 30)

    total = word_pts + tech_pts + metric_pts

    if total >= 60:
        return "Strong"
    elif total >= 30:
        return "Moderate"
    return "Weak"


def _basic_strength(text: str) -> str:
    wc = len(text.split()) if text else 0
    if wc > 100:
        return "Strong"
    elif wc > 40:
        return "Moderate"
    return "Weak"


def evaluate_sections(sections: dict) -> dict:
    exp_text  = sections.get("experience", "")
    proj_text = sections.get("projects", "")
    edu_text  = sections.get("education", "")

    result = {
        "experience": score_experience_section(exp_text),
        "projects":   score_projects_section(proj_text),
        "education":  _basic_strength(edu_text),
        "_exp_diag":  get_section_diagnostics(exp_text, "experience"),
        "_proj_diag": get_section_diagnostics(proj_text, "projects"),
    }

    return result