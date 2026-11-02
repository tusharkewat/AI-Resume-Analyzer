import re
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.analysis import ScoreBreakdown
from app.schemas.resume import StructuredResumeData


class ScoringEngineService:
    """Calculates explainable weighted match scores and readability metrics."""

    @staticmethod
    def calculate_score(
        resume_text: str,
        structured_resume: StructuredResumeData,
        job_description: str,
        skills_score: float
    ) -> Tuple[float, ScoreBreakdown]:
        """
        Calculates:
        - TF-IDF Cosine Similarity (0-100)
        - Experience Relevance (0-100)
        - Education Relevance (0-100)
        - Content Readability (0-100)
        - Overall weighted score (0-100)
        """
        # 1. TF-IDF Text Similarity
        text_sim_score = ScoringEngineService._calculate_tfidf_similarity(resume_text, job_description)

        # 2. Experience relevance
        exp_score = ScoringEngineService._calculate_experience_score(structured_resume, job_description)

        # 3. Education relevance
        edu_score, edu_required = ScoringEngineService._calculate_education_score(structured_resume, job_description)

        # 4. Readability score
        readability_score = ScoringEngineService._calculate_readability_score(resume_text, structured_resume)

        # Dynamic weights: if education is not specified in the JD, reallocate weight
        if edu_required:
            w_skills = 0.50
            w_text = 0.25
            w_exp = 0.15
            w_edu = 0.10
        else:
            w_skills = 0.55
            w_text = 0.28
            w_exp = 0.17
            w_edu = 0.0

        overall_score = round(
            (skills_score * w_skills) +
            (text_sim_score * w_text) +
            (exp_score * w_exp) +
            (edu_score * w_edu),
            1
        )
        overall_score = max(0.0, min(100.0, overall_score))

        explanation = (
            f"Overall score of {overall_score}/100 synthesized from: "
            f"Skills Match ({skills_score}%, weight {int(w_skills*100)}%), "
            f"Text/Context Similarity ({text_sim_score}%, weight {int(w_text*100)}%), "
            f"Experience Alignment ({exp_score}%, weight {int(w_exp*100)}%)"
        )
        if edu_required:
            explanation += f", and Education Match ({edu_score}%, weight {int(w_edu*100)}%)."
        else:
            explanation += ". Education criteria was not specified in the job description."

        breakdown = ScoreBreakdown(
            skills_score=skills_score,
            skills_weight=w_skills,
            text_similarity_score=text_sim_score,
            text_similarity_weight=w_text,
            experience_score=exp_score,
            experience_weight=w_exp,
            education_score=edu_score,
            education_weight=w_edu,
            readability_score=readability_score,
            explanation=explanation
        )

        return overall_score, breakdown

    @staticmethod
    def _calculate_tfidf_similarity(resume_text: str, job_description: str) -> float:
        clean_resume = resume_text.strip()
        clean_jd = job_description.strip()
        if not clean_resume or not clean_jd:
            return 0.0

        # Reject short gibberish or empty words
        words_jd = [w for w in re.findall(r'\b[a-zA-Z]{2,}\b', clean_jd)]
        if len(words_jd) < 5:
            return 0.0

        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=5000
            )
            tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            if float(sim) <= 0.0:
                return 0.0
            # Scale cosine similarity (0.45+ is an exceptional match) to 0-100 scale
            scaled_sim = min(100.0, round(float(sim) * 180.0, 1))
            return max(0.0, scaled_sim)
        except Exception:
            return 0.0

    @staticmethod
    def _calculate_experience_score(structured: StructuredResumeData, jd: str) -> float:
        jd_lower = jd.lower()
        has_work_exp = bool(structured.work_experience)
        candidate_years = structured.total_years_experience
        if candidate_years is None and has_work_exp:
            candidate_years = len(structured.work_experience) * 1.5
        elif candidate_years is None:
            candidate_years = 0.0

        years_match = re.search(r'(\d+)\+?\s*(?:to\s*\d+\s*)?years?(?:\s+of)?\s+experience', jd_lower)
        is_senior_role = any(t in jd_lower for t in ["senior", "sr.", "lead", "principal", "staff"])

        # Edge case: Candidate has zero documented work experience and zero estimated years
        if not has_work_exp and candidate_years == 0.0:
            if years_match or is_senior_role:
                return 0.0
            return 25.0

        score = 70.0  # Base standard score for candidates with documented work experience

        if years_match:
            required_years = float(years_match.group(1))
            if candidate_years >= required_years:
                score += 25.0
            elif candidate_years >= (required_years * 0.7):
                score += 10.0
            else:
                score -= 30.0
        else:
            # Seniority keyword matching
            seniority_levels = {
                "senior": ["senior", "sr.", "lead", "principal", "staff"],
                "lead": ["lead", "manager", "director", "head"],
                "junior": ["junior", "jr.", "entry level", "associate", "intern"]
            }
            for level, tokens in seniority_levels.items():
                if any(t in jd_lower for t in tokens):
                    resume_has_level = any(
                        any(t in (item.title or "").lower() for t in tokens)
                        for item in structured.work_experience
                    )
                    if resume_has_level:
                        score += 20.0
                    elif level in ["senior", "lead"]:
                        score -= 15.0
                    break

        # Bonus if strong work experience bullet points exist
        total_bullets = sum(len(w.bullets) for w in structured.work_experience)
        if total_bullets >= 6:
            score += 10.0

        return max(0.0, min(100.0, round(score, 1)))

    @staticmethod
    def _calculate_education_score(structured: StructuredResumeData, jd: str) -> Tuple[float, bool]:
        jd_lower = jd.lower()
        degrees_hierarchy = {
            "phd": ["ph.d", "phd", "doctorate"],
            "master": ["master", "m.s.", "msc", "m.tech", "mba"],
            "bachelor": ["bachelor", "b.s.", "bsc", "b.tech", "degree in computer science", "degree in engineering"]
        }

        # Check if JD requires degrees
        required_level = None
        for level, triggers in degrees_hierarchy.items():
            if any(t in jd_lower for t in triggers):
                required_level = level
                break

        if not required_level:
            return 80.0, False  # Education not explicitly demanded

        # Check candidate education
        if not structured.education:
            # Explicit requirement present in JD, but candidate has no education documented
            return 0.0, True

        candidate_degrees = " ".join([e.degree or e.details or "" for e in structured.education]).lower()

        if required_level == "phd":
            if any(t in candidate_degrees for t in degrees_hierarchy["phd"]):
                return 100.0, True
            elif any(t in candidate_degrees for t in degrees_hierarchy["master"]):
                return 75.0, True
            elif any(t in candidate_degrees for t in degrees_hierarchy["bachelor"]):
                return 60.0, True
            return 20.0, True

        if required_level == "master":
            if any(t in candidate_degrees for t in degrees_hierarchy["phd"] + degrees_hierarchy["master"]):
                return 100.0, True
            elif any(t in candidate_degrees for t in degrees_hierarchy["bachelor"]):
                return 80.0, True
            return 30.0, True

        if required_level == "bachelor":
            if any(t in candidate_degrees for t in degrees_hierarchy["phd"] + degrees_hierarchy["master"] + degrees_hierarchy["bachelor"]):
                return 100.0, True
            return 40.0, True

        return 80.0, False

    @staticmethod
    def _calculate_readability_score(resume_text: str, structured: StructuredResumeData) -> float:
        score = 80.0
        words = resume_text.split()
        word_count = len(words)

        # Ideal resume length is 300 to 1200 words
        if word_count < 100:
            score -= 40.0
        elif word_count < 250:
            score -= 15.0
        elif word_count > 1500:
            score -= 15.0

        # Action verbs check in bullets
        action_verbs = [
            "developed", "built", "engineered", "designed", "implemented", "optimized",
            "spearheaded", "orchestrated", "reduced", "increased", "deployed", "led", "managed",
            "architected", "delivered", "automated", "created", "refactored"
        ]
        total_bullets = sum(len(item.bullets) for item in structured.work_experience)
        if total_bullets > 0:
            matched_verbs = sum(
                1 for item in structured.work_experience
                for b in item.bullets
                if any(v in b.lower().split()[:3] for v in action_verbs)
            )
            ratio = matched_verbs / total_bullets
            if ratio >= 0.5:
                score += 15.0
            elif ratio >= 0.25:
                score += 5.0
            else:
                score -= 10.0

        # Contact info completeness check
        if not structured.contact.email or not structured.contact.phone:
            score -= 10.0

        return max(10.0, min(100.0, round(score, 1)))
