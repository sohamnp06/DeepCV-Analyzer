def get_section_strength(text):
    length = len(text)

    if length > 120:
        return "Strong"
    elif length > 60:
        return "Moderate"
    else:
        return "Weak"


def evaluate_sections(sections):
    result = {}

    result["education"] = get_section_strength(sections.get("education", ""))
    result["experience"] = get_section_strength(sections.get("experience", ""))
    result["projects"] = get_section_strength(sections.get("projects", ""))

    return result