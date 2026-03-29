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

    if any(k in line for k in ["btech", "mtech", "university", "college"]):
        return "education"

    if any(k in line for k in ["internship", "intern at", "worked at"]):
        return "experience"

    if any(k in line for k in ["project", "built", "developed"]):
        return "projects"

    return "other"

def extract_skills_real(sections):
    text = ""

    # Priority → Skills section
    if sections["skills"]:
        text = sections["skills"]
    else:
        # fallback
        text = sections["summary"] + " " + sections["experience"]

    text = text.lower()

    # Split text
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

    remove_words = [
        "phone", "email", "contact", "www"
    ]

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

        # Safety
        if not isinstance(sections[section], list):
            sections[section] = []

        sections[section].append(line)

    # Convert to string
    for key in sections:
        sections[key] = " ".join(sections[key])

    sections["skills"] = extract_skills_real(sections)

    sections["other"] = clean_other(sections["other"])

    return sections