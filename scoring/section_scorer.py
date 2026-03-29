def get_section_strength(text):
    word_count = len(text.split())

    if word_count > 100:
        return "Strong"
    elif word_count > 40:
        return "Moderate"
    else:
        return "Weak"


def evaluate_sections(sections):
    result = {}

    result["education"] = get_section_strength(sections.get("education", ""))
    result["experience"] = get_section_strength(sections.get("experience", ""))
    result["projects"] = get_section_strength(sections.get("projects", ""))

    return result