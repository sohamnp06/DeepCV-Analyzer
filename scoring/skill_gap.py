def categorize_skills(skills):
    categories = {
        "programming": ["python", "java", "c++", "c#", "javascript"],
        "frontend": ["html", "css", "react", "angular", "vue", "bootstrap", "tailwind"],
        "backend": ["node", "django", "flask"],
        "database": ["sql", "mongodb"],
        "core_cs": ["data structures", "algorithms", "dbms", "operating systems", "system design"],
        "tools": ["git", "github", "aws", "azure"]
    }

    categorized = {k: [] for k in categories}
    categorized["other"] = []

    for skill in skills:
        skill_lower = skill.lower()
        placed = False

        for category, keywords in categories.items():
            for kw in keywords:
                if kw in skill_lower:
                    categorized[category].append(skill)
                    placed = True
                    break
            if placed:
                break

        if not placed:
            categorized["other"].append(skill)

    return categorized


def generate_skill_gap(semantic_result):
    matched = [m[0] for m in semantic_result["matched"]]
    missing = semantic_result["missing"]

    matched_cat = categorize_skills(matched)
    missing_cat = categorize_skills(missing)

    result = {}

    result["strong"] = matched
    result["missing"] = missing
    result["strong_by_category"] = matched_cat
    result["missing_by_category"] = missing_cat

    recommendations = []

    if missing_cat["core_cs"]:
        recommendations.append("Strengthen core CS fundamentals (DSA, OS, DBMS, System Design).")

    if missing_cat["frontend"]:
        recommendations.append("Improve frontend skills (HTML, CSS, React, UI frameworks).")

    if missing_cat["backend"]:
        recommendations.append("Work on backend frameworks like Node.js or Django.")

    if missing_cat["database"]:
        recommendations.append("Improve database knowledge (SQL, MongoDB).")

    if missing_cat["tools"]:
        recommendations.append("Learn industry tools like Git, AWS, Azure.")

    if missing_cat["programming"]:
        recommendations.append("Strengthen programming fundamentals and problem solving.")

    if not recommendations:
        recommendations.append("Profile looks strong. Focus on advanced projects and system design.")

    result["recommendations"] = recommendations

    return result