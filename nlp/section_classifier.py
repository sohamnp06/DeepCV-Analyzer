SECTION_HEADERS = {
    "education": ["education", "academic", "qualification"],
    "experience": ["experience", "work experience", "employment"],
    "skills": ["skills", "technical skills", "core skills", "technologies"],
    "projects": ["projects"],
    "summary": ["summary", "profile", "about", "objective"]
}


def is_header(line):
    line = line.lower().strip()
    for section, keywords in SECTION_HEADERS.items():
        if any(kw in line for kw in keywords) and len(line.split()) <= 6:
            return section
    return None


def is_noise(line):
    return any(x in line.lower() for x in ["contact", "phone", "email", "www", ".com"])


def fallback_classify(line):
    line = line.lower()

    if any(k in line for k in ["btech", "university", "college"]):
        return "education"

    if any(k in line for k in ["intern", "developer", "engineer"]):
        return "experience"

    if any(k in line for k in ["project", "built", "developed"]):
        return "projects"

    return "other"


# 🔥 Dynamic skills extraction (no heavy NLP)
def extract_skills(skills_text, summary_text):
    combined = (skills_text + " " + summary_text).lower()

    # Remove noise
    noise_words = [
        "name", "contact", "phone", "email",
        "address", "mumbai", "india"
    ]

    for word in noise_words:
        combined = combined.replace(word, "")

    # -----------------------------------
    # SKILL KEYWORDS (EXPANDED)
    # -----------------------------------
    SKILLS_DB = [
        # programming
        "python", "java", "c++", "c#", "javascript",

        # web
        "html", "css", "react", "node", "django", "flask",

        # data
        "sql", "mongodb", "machine learning", "data analysis",

        # cs core
        "dsa", "data structures", "algorithms",
        "dbms", "operating system", "system design",

        # tools
        "git", "github", "aws", "azure",

        # soft skills
        "communication", "teamwork", "leadership",
        "problem solving", "collaboration"
    ]

    found = []

    for skill in SKILLS_DB:
        if skill in combined:
            found.append(skill)

    return " ".join(sorted(set(found)))

def get_structured_sections(text):
    sections = {
        "education": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "summary": [],
        "other": []
    }

    current_section = "other"
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for line in lines:

        if is_noise(line):
            continue

        header = is_header(line)

        if header:
            current_section = header
            continue

        if current_section == "other":
            section = fallback_classify(line)
        else:
            section = current_section

        sections[section].append(line)

    for key in sections:
        sections[key] = " ".join(sections[key])

    # 🔥 Use FULL TEXT for skills (IMPORTANT CHANGE)
    sections["skills"] = extract_skills(
    sections["skills"],
    sections["summary"]
    )

    return sections