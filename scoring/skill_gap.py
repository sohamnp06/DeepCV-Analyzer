def categorize_skills(skills):
    categories = {
        "programming": ["python", "java", "c++", "c#", "javascript", "typescript", "go", "rust", "ruby", "php"],
        "frontend": ["html", "css", "react", "angular", "vue", "bootstrap", "tailwind", "next.js", "frontend", "ui", "ux", "sass", "less"],
        "backend": ["node", "django", "flask", "express", "spring boot", "backend", "api", "rest api", "graphql"],
        "database": ["sql", "mongodb", "postgresql", "mysql", "redis", "firebase", "database", "orm", "nosql"],
        "data_science": ["numpy", "pandas", "scipy", "scikit-learn", "tensorflow", "pytorch", "keras", "data science", "machine learning", "deep learning", "nlp"],
        "core_cs": ["data structures", "algorithms", "dbms", "operating systems", "system design", "oops", "computer networks"],
        "tools": ["git", "github", "docker", "kubernetes", "jenkins", "gitlab", "bitbucket"],
        "cloud": ["aws", "azure", "gcp", "heroku", "cloud", "s3", "ec2", "lambda"]
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
    matched = [m[0] if isinstance(m, (list, tuple)) else str(m) for m in (semantic_result.get("matched", []))]
    missing = semantic_result.get("missing", [])

    matched_cat = categorize_skills(matched)
    missing_cat = categorize_skills(missing)

    result = {}

    result["strong"] = matched
    result["missing"] = missing
    result["strong_by_category"] = matched_cat
    result["missing_by_category"] = missing_cat

    recommendations = []

    if missing_cat["core_cs"]:
        recommendations.append("Strengthen core CS fundamentals (DSA, OS, DBMS) to improve engineering depth and problem-solving skills.")

    if missing_cat["frontend"]:
        recommendations.append("Enhance frontend expertise by working with modern frameworks like React or Next.js and focusing on UI/UX best practices.")

    if missing_cat["backend"]:
        recommendations.append("Develop robust backend services using scalable frameworks (Node.js/Spring) and focus on API design and microservices.")

    if missing_cat["database"]:
        recommendations.append("Master both SQL and NoSQL database concepts, focusing on indexing, query optimization, and data modeling.")

    if missing_cat["data_science"]:
        recommendations.append("Deepen your ML/AI knowledge by exploring advanced neural networks, NLP, or computer vision architectures.")

    if missing_cat["tools"]:
        recommendations.append("Improve DevOps proficiency by mastering Git workflows and CI/CD tools to demonstrate production-readiness.")

    if missing_cat["cloud"]:
        recommendations.append("Gain experience with cloud platforms (AWS/Azure/GCP) to understand how to deploy and scale applications in the cloud.")

    if missing_cat["programming"]:
        recommendations.append("Broaden your programming polyglot skills by learning highly-scalable languages like Go or Rust.")

    if not recommendations:
        recommendations.append("🚀 **Strategic Focus:** Your core profile is exceptionally strong. To move into the top 1% of applicants, we recommend focusing on 'Strategic Leadership'—this involves mentoring team members, leading open-source initiatives, and mastering High-Level System Design (HLD) to demonstrate you can architect entire platforms, not just code features.")
    else:
        recommendations.append("💼 **Career Roadmap:** Your technical baseline is solid. Focus on bridging the categorical gaps identified above and quantifying your impact more heavily using the STAR method (metrics-based results).")

    result["recommendations"] = recommendations
    return result