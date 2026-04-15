SECTION_HEADERS = {
    "education": ["education", "academic", "qualification", "academics"],
    "experience": ["experience", "work experience", "employment", "history", "professional experience", "career", "work history"],
    "skills": ["skills", "technical skills", "core skills", "technologies", "competencies", "expertise"],
    "projects": ["projects", "personal projects", "portfolio", "academic projects", "open source"],
    "summary": ["summary", "profile", "about", "objective", "professional summary"]
}

def is_header(line):
    line = line.lower().strip()
    for section, keywords in SECTION_HEADERS.items():
        if any(kw in line for kw in keywords) and len(line.split()) <= 5:
            return section
    return None

def is_noise(line):
    return any(x in line.lower() for x in [
        "contact", "phone", "email", "www", ".com",
        "+91", "india", "mumbai"
    ])

def fallback_classify(line):
    line = line.lower()
    if any(k in line for k in ["btech", "mtech", "university", "college", "degree", "bachelor", "master"]):
        return "education"
    if any(k in line for k in ["internship", "intern at", "worked at", "software engineer at", "developer at", "freelance"]):
        return "experience"
    if any(k in line for k in ["project", "built", "developed", "hackathon", "repository"]):
        return "projects"
    return "other"

def extract_skills_real(sections):
    text = ""
    if sections["skills"]:
        text = sections["skills"]
    else:
        text = sections["summary"] + " " + sections["experience"]

    text = text.lower()

    tokens = []
    for part in text.replace(",", " ").replace("/", " ").split():
        part = part.strip()
        if len(part) > 2:
            tokens.append(part)

    stop_words = [
        "and", "with", "for", "the", "this", "that",
        "experience", "years", "worked", "using",
        "developer", "engineer"
    ]

    skills = [t for t in tokens if t not in stop_words]
    return " ".join(sorted(set(skills)))


def clean_other(text):
    text = text.lower()
    remove_words = ["phone", "email", "contact", "www"]
    for word in remove_words:
        text = text.replace(word, "")
    return text.strip()


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

        if not isinstance(sections[section], list):
            sections[section] = []

        sections[section].append(line)

    for key in sections:
        sections[key] = " ".join(sections[key])

    sections["skills"] = extract_skills_real(sections)
    sections["other"] = clean_other(sections["other"])

    return sections