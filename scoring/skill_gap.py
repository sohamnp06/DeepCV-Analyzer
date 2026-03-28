def categorize_skills(skills):
    categories = {
        "programming": ["python", "java", "c++", "c#", "javascript"],
        "core_cs": ["data structures", "algorithms", "dbms", "operating systems", "system design"],
        "tools": ["git", "github", "aws", "azure"],
        "other": []
    }

    categorized = {
        "programming": [],
        "core_cs": [],
        "tools": [],
        "other": []
    }

    for skill in skills:
        found = False

        for category, keywords in categories.items():
            for kw in keywords:
                if kw in skill:
                    categorized[category].append(skill)
                    found = True
                    break
            if found:
                break

        if not found:
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
    result["missing_by_category"] = missing_cat

    # Simple recommendation logic
    recommendations = []

    if missing_cat["core_cs"]:
        recommendations.append("Improve core CS fundamentals (DSA, OS, DBMS).")

    if missing_cat["tools"]:
        recommendations.append("Learn industry tools like Git, AWS, Azure.")

    if missing_cat["programming"]:
        recommendations.append("Strengthen programming language proficiency.")

    if not recommendations:
        recommendations.append("Profile looks strong. Focus on advanced projects.")

    result["recommendations"] = recommendations

    return result