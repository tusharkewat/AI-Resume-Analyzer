import re
from typing import Dict, List, Optional, Any, Tuple
from app.schemas.resume import (
    StructuredResumeData,
    ContactInfo,
    WorkExperienceItem,
    EducationItem,
    ProjectItem
)

# Curated skill taxonomies with canonical names and synonyms/aliases
SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "languages": {
        "Python": ["python", "python3", "py"],
        "JavaScript": ["javascript", "js", "ecmascript"],
        "TypeScript": ["typescript", "ts"],
        "Java": ["java", "jvm"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "csharp", ".net c#"],
        "Go": ["golang", "go"],
        "Rust": ["rust", "rustlang"],
        "Ruby": ["ruby"],
        "PHP": ["php"],
        "Swift": ["swift"],
        "Kotlin": ["kotlin"],
        "SQL": ["sql", "structured query language"],
        "HTML": ["html", "html5"],
        "CSS": ["css", "css3"],
        "Bash": ["bash", "shell scripting", "powershell", "zsh"],
        "R": ["r programming", "r language"],
        "Scala": ["scala"]
    },
    "frameworks": {
        "React": ["react", "react.js", "reactjs"],
        "Next.js": ["next.js", "nextjs", "next"],
        "Vue.js": ["vue", "vue.js", "vuejs"],
        "Angular": ["angular", "angularjs"],
        "Node.js": ["node", "node.js", "nodejs"],
        "Express": ["express", "express.js", "expressjs"],
        "FastAPI": ["fastapi"],
        "Django": ["django", "django rest framework", "drf"],
        "Flask": ["flask"],
        "Spring Boot": ["spring boot", "springboot", "spring"],
        "Tailwind CSS": ["tailwind", "tailwindcss"],
        "PyTorch": ["pytorch"],
        "TensorFlow": ["tensorflow", "tf"],
        "Scikit-Learn": ["scikit-learn", "sklearn"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"]
    },
    "cloud_devops": {
        "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
        "Google Cloud (GCP)": ["gcp", "google cloud", "google cloud platform"],
        "Microsoft Azure": ["azure", "microsoft azure"],
        "Docker": ["docker", "containerization", "containers"],
        "Kubernetes": ["kubernetes", "k8s"],
        "Terraform": ["terraform", "iac", "infrastructure as code"],
        "CI/CD": ["ci/cd", "continuous integration", "continuous delivery", "github actions", "gitlab ci", "jenkins"],
        "Linux": ["linux", "ubuntu", "debian", "redhat", "centos"]
    },
    "databases": {
        "PostgreSQL": ["postgresql", "postgres", "psql"],
        "MySQL": ["mysql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "SQLite": ["sqlite", "sqlite3"],
        "Elasticsearch": ["elasticsearch", "elastic"],
        "DynamoDB": ["dynamodb"],
        "Oracle": ["oracle db", "oracle"]
    },
    "developer_tools_practices": {
        "Git": ["git", "github", "gitlab"],
        "REST API": ["rest", "restful", "rest api", "apis"],
        "GraphQL": ["graphql"],
        "Microservices": ["microservices", "microservice architecture"],
        "Agile": ["agile", "scrum", "kanban", "sprints"],
        "TDD": ["tdd", "test driven development", "unit testing", "pytest", "jest"]
    },
    "soft_skills": {
        "Leadership": ["leadership", "leading teams", "team lead", "mentorship", "mentoring"],
        "Communication": ["communication", "written communication", "verbal communication", "presentation"],
        "Problem Solving": ["problem solving", "troubleshooting", "analytical thinking"],
        "Team Collaboration": ["collaboration", "cross-functional collaboration", "team player"],
        "Project Management": ["project management", "time management", "scrum master"]
    }
}

SECTION_HEADERS = {
    "summary": ["summary", "professional summary", "profile", "about me", "executive summary", "objective"],
    "experience": ["experience", "work experience", "professional experience", "employment history", "work history"],
    "education": ["education", "academic history", "academic background", "qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "tech stack", "expertise"],
    "projects": ["projects", "personal projects", "key projects", "notable projects"],
    "certifications": ["certifications", "licenses & certifications", "certificates", "credentials"]
}


class InformationExtractorService:
    """Parses raw resume text into structured fields using regex patterns and domain heuristics."""

    @staticmethod
    def extract_structured_data(text: str) -> StructuredResumeData:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        sections = InformationExtractorService._split_into_sections(lines)

        contact = InformationExtractorService._extract_contact(lines, text)
        summary = InformationExtractorService._extract_summary(sections.get("summary", []))
        tech_skills, soft_skills, skills_by_cat = InformationExtractorService._extract_skills(text)
        work_experience, total_years = InformationExtractorService._extract_experience(sections.get("experience", []))
        education = InformationExtractorService._extract_education(sections.get("education", []))
        projects = InformationExtractorService._extract_projects(sections.get("projects", []))
        certifications = InformationExtractorService._extract_certifications(sections.get("certifications", []))
        languages = InformationExtractorService._extract_languages(text)
        keywords = InformationExtractorService._extract_keywords(text)

        return StructuredResumeData(
            contact=contact,
            summary=summary,
            technical_skills=tech_skills,
            soft_skills=soft_skills,
            skills_by_category=skills_by_cat,
            work_experience=work_experience,
            education=education,
            projects=projects,
            certifications=certifications,
            languages=languages,
            total_years_experience=total_years,
            extracted_keywords=keywords
        )

    @staticmethod
    def _split_into_sections(lines: List[str]) -> Dict[str, List[str]]:
        sections: Dict[str, List[str]] = {}
        current_section = "header"
        sections[current_section] = []

        for line in lines:
            line_lower = line.strip().lower()
            # Clean possible markdown or symbols: "## Experience", "EXPERIENCE:"
            clean_header = re.sub(r'^[#*\-•\s]+|[::\s]+$', '', line_lower).strip()

            matched_sec = None
            for sec_name, triggers in SECTION_HEADERS.items():
                if clean_header in triggers or (len(clean_header) < 30 and any(clean_header == t for t in triggers)):
                    matched_sec = sec_name
                    break

            if matched_sec:
                current_section = matched_sec
                if current_section not in sections:
                    sections[current_section] = []
            else:
                sections[current_section].append(line)

        return sections

    @staticmethod
    def _extract_contact(lines: List[str], full_text: str) -> ContactInfo:
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', full_text)
        email = email_match.group(0) if email_match else None

        # Phone
        phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', full_text)
        phone = phone_match.group(0) if phone_match else None

        # Name detection: look at the first 3 non-empty lines that don't contain email/phone/links
        full_name = None
        for line in lines[:5]:
            clean = line.strip()
            if email and email in clean:
                continue
            if phone and phone in clean:
                continue
            if "@" in clean or "http" in clean or "linkedin.com" in clean or "github.com" in clean:
                continue
            words = clean.split()
            # Names typically 2 to 4 words, alphabetic, capitalized
            if 1 < len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
                full_name = clean
                break

        # Location heuristic: City, ST or City, Country
        location = None
        loc_match = re.search(r'\b([A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\b|[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z]+)\b', full_text[:1000])
        if loc_match:
            loc_candidate = loc_match.group(0).strip()
            if not any(k in loc_candidate.lower() for k in ["january", "february", "experience", "education"]):
                location = loc_candidate

        return ContactInfo(
            full_name=full_name,
            email=email,
            phone=phone,
            location=location
        )

    @staticmethod
    def _extract_summary(summary_lines: List[str]) -> Optional[str]:
        if not summary_lines:
            return None
        text = " ".join(summary_lines).strip()
        return text if len(text) > 15 else None

    @staticmethod
    def _extract_skills(full_text: str) -> Tuple[List[str], List[str], Dict[str, List[str]]]:
        text_lower = f" {full_text.lower()} "
        tech_skills: List[str] = []
        soft_skills: List[str] = []
        skills_by_cat: Dict[str, List[str]] = {}

        for category, skill_map in SKILL_TAXONOMY.items():
            cat_list = []
            for canonical, aliases in skill_map.items():
                matched = False
                for alias in aliases:
                    # Escape special characters in alias e.g. c++, c#
                    escaped = re.escape(alias)
                    # Use boundary conditions that work for c++ / c# as well
                    pattern = r'(?<![a-zA-Z0-9])' + escaped + r'(?![a-zA-Z0-9])'
                    if re.search(pattern, text_lower):
                        matched = True
                        break
                if matched:
                    cat_list.append(canonical)
                    if category == "soft_skills":
                        if canonical not in soft_skills:
                            soft_skills.append(canonical)
                    else:
                        if canonical not in tech_skills:
                            tech_skills.append(canonical)
            if cat_list:
                skills_by_cat[category] = cat_list

        return tech_skills, soft_skills, skills_by_cat

    @staticmethod
    def _extract_experience(exp_lines: List[str]) -> Tuple[List[WorkExperienceItem], Optional[float]]:
        if not exp_lines:
            return [], None

        items: List[WorkExperienceItem] = []
        current_title = None
        current_company = None
        current_dates = None
        current_bullets: List[str] = []

        date_pattern = re.compile(
            r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\b\d{4})\s*[-–—to]+\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\b\d{4}|\bPresent\b|\bCurrent\b)',
            re.IGNORECASE
        )

        years_found: List[int] = []

        for line in exp_lines:
            match = date_pattern.search(line)
            is_bullet = line.startswith(('-', '•', '*', '–', '—')) or line.strip().startswith(('1.', '2.', '3.'))

            if match:
                # Save previous experience item if accumulated
                if current_title or current_bullets:
                    items.append(WorkExperienceItem(
                        title=current_title or "Role",
                        company=current_company,
                        dates=current_dates,
                        bullets=current_bullets
                    ))
                    current_bullets = []

                current_dates = match.group(0).strip()
                # Parse years for overall tenure estimate
                num_matches = re.findall(r'\b(19\d{2}|20\d{2})\b', line)
                for ym in num_matches:
                    years_found.append(int(ym))

                # Remaining part of the line might be title or company
                remainder = date_pattern.sub('', line).strip(' |-–—,\t')
                if remainder:
                    parts = [p.strip() for p in re.split(r' at | \| | , ', remainder) if p.strip()]
                    current_title = parts[0] if len(parts) > 0 else "Software Engineer"
                    current_company = parts[1] if len(parts) > 1 else None
                else:
                    current_title = "Role"
            elif is_bullet:
                bullet_clean = re.sub(r'^[•\-\*\–—0-9\.]+\s*', '', line).strip()
                if bullet_clean:
                    current_bullets.append(bullet_clean)
            else:
                if len(line) < 60 and not current_bullets:
                    # Likely a company name or role title on a separate line
                    if not current_title or current_title == "Role":
                        current_title = line.strip()
                    elif not current_company:
                        current_company = line.strip()
                else:
                    # Non-bullet text under current position
                    if line.strip():
                        current_bullets.append(line.strip())

        if current_title or current_bullets:
            items.append(WorkExperienceItem(
                title=current_title or "Role",
                company=current_company,
                dates=current_dates,
                bullets=current_bullets
            ))

        total_years = None
        if len(years_found) >= 2:
            min_year = min(years_found)
            max_year = max(years_found)
            diff = max_year - min_year
            if 0 < diff <= 45:
                total_years = float(diff)

        return items, total_years

    @staticmethod
    def _extract_education(edu_lines: List[str]) -> List[EducationItem]:
        if not edu_lines:
            return []

        degree_keywords = [
            "Bachelor", "Master", "Ph.D.", "PhD", "B.S.", "B.Sc.", "B.Tech",
            "M.S.", "M.Sc.", "M.Tech", "MBA", "Associate", "Degree", "B.A.", "B.E."
        ]

        items: List[EducationItem] = []
        for line in edu_lines:
            has_degree = any(dk.lower() in line.lower() for dk in degree_keywords)
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', line)
            year = year_match.group(0) if year_match else None

            if has_degree or year:
                # Attempt to extract degree name
                degree = None
                for dk in degree_keywords:
                    deg_match = re.search(rf'({re.escape(dk)}[^\,\-\|\n]*)', line, re.IGNORECASE)
                    if deg_match:
                        degree = deg_match.group(0).strip()
                        break

                items.append(EducationItem(
                    degree=degree or line.strip()[:60],
                    institution=line.strip() if not degree else None,
                    year=year,
                    details=line.strip()
                ))

        return items

    @staticmethod
    def _extract_projects(proj_lines: List[str]) -> List[ProjectItem]:
        if not proj_lines:
            return []

        projects: List[ProjectItem] = []
        curr_name = None
        curr_desc = []

        for line in proj_lines:
            clean = line.strip()
            if not clean:
                continue
            if len(clean) < 50 and not clean.startswith(('-', '•', '*')):
                if curr_name:
                    projects.append(ProjectItem(name=curr_name, description=" ".join(curr_desc)))
                    curr_desc = []
                curr_name = clean
            else:
                curr_desc.append(re.sub(r'^[•\-\*]+\s*', '', clean))

        if curr_name:
            projects.append(ProjectItem(name=curr_name, description=" ".join(curr_desc)))

        return projects

    @staticmethod
    def _extract_certifications(cert_lines: List[str]) -> List[str]:
        certs = []
        for line in cert_lines:
            clean = re.sub(r'^[•\-\*0-9\.]+\s*', '', line).strip()
            if clean and len(clean) > 3:
                certs.append(clean)
        return certs

    @staticmethod
    def _extract_languages(full_text: str) -> List[str]:
        known_languages = ["English", "Spanish", "French", "German", "Mandarin", "Hindi", "Japanese", "Portuguese", "Italian", "Russian", "Arabic"]
        found = []
        for lang in known_languages:
            if re.search(rf'\b{lang}\b', full_text, re.IGNORECASE):
                found.append(lang)
        return found

    @staticmethod
    def _extract_keywords(full_text: str) -> List[str]:
        words = re.findall(r'\b[A-Za-z0-9\-+#.]{3,20}\b', full_text)
        stop_words = {
            "the", "and", "for", "with", "that", "this", "from", "have", "will", "your", "been", "were",
            "which", "their", "about", "would", "there", "work", "team", "year", "years", "using", "used"
        }
        freq: Dict[str, int] = {}
        for w in words:
            wl = w.lower()
            if wl not in stop_words and len(wl) > 3:
                freq[wl] = freq.get(wl, 0) + 1

        sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [k for k, _ in sorted_kw[:25]]
