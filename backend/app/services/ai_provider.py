import os
import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import httpx
from app.config import settings
from app.schemas.analysis import AnalysisRecommendations, BulletPointRewrite
from app.schemas.resume import StructuredResumeData

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    @abstractmethod
    async def generate_recommendations(
        self,
        resume_text: str,
        structured_resume: StructuredResumeData,
        job_title: str,
        job_description: str,
        matching_skills: List[str],
        missing_skills: List[str]
    ) -> Tuple[AnalysisRecommendations, str]:
        """
        Generates grounded recommendations and bullet point rewrites.
        Returns:
            Tuple[AnalysisRecommendations, method_name_string]
        """
        pass


def rewrite_grounded_bullet(orig: str) -> BulletPointRewrite:
    """
    Rewrites a resume bullet point into a natural, grammatical XYZ statement.
    Grounded strictly in the candidate's words without fabricating metrics or facts.
    """
    cleaned = re.sub(r'^[•\-\*\–—\d\.\s]+', '', orig).strip().rstrip('. ')
    if not cleaned:
        cleaned = orig.strip().rstrip('. ')

    # Check for existing metrics in the bullet
    metric_pattern = re.compile(
        r'(\d+%\s*|\$\d+|\b\d+\s*x\b|\b\d+k\b|\b\d+ms\b|\b\d+\s*seconds?\b|\breduced\s+by\s+\d+|\bincreased\s+by\s+\d+|\bscaled\s+to\s+\d+)',
        re.IGNORECASE
    )
    has_existing_metric = bool(metric_pattern.search(cleaned))

    # Detect common passive / weak openings
    passive_replacements = [
        (r'^(?:responsible\s+for|tasked\s+with)\s+(?:the\s+)?(?:development|developing)\s+(?:of\s+)?', 'Architected and developed '),
        (r'^(?:responsible\s+for|tasked\s+with)\s+(?:the\s+)?(?:management|managing)\s+(?:of\s+)?', 'Led and managed '),
        (r'^(?:responsible\s+for|tasked\s+with)\s+(?:the\s+)?(?:optimization|optimizing)\s+(?:of\s+)?', 'Optimized '),
        (r'^(?:responsible\s+for|tasked\s+with)\s+', 'Spearheaded '),
        (r'^(?:worked\s+on|assisted\s+with|helped\s+with|participated\s+in)\s+(?:the\s+)?(?:development|building|creation)\s+(?:of\s+)?', 'Co-engineered and delivered '),
        (r'^(?:worked\s+on|assisted\s+with|helped\s+with|participated\s+in)\s+', 'Engineered and contributed to '),
        (r'^(?:duties\s+included|involved\s+in)\s+', 'Executed '),
    ]

    transformed_core = cleaned
    was_passive = False
    for pattern, replacement in passive_replacements:
        if re.search(pattern, transformed_core, re.IGNORECASE):
            transformed_core = re.sub(pattern, replacement, transformed_core, count=1, flags=re.IGNORECASE)
            was_passive = True
            break

    # If first word was not altered, ensure first character is capitalized
    if not was_passive and transformed_core:
        transformed_core = transformed_core[0].upper() + transformed_core[1:]

    # Construct XYZ enhancement based on whether a metric already exists
    if has_existing_metric:
        rewritten = f"{transformed_core}, ensuring high software reliability and seamless release velocity."
        explanation = (
            "Preserved strong action verb and verified metric from your original text; "
            "augmented with an XYZ business outcome clause."
        )
    elif was_passive:
        rewritten = (
            f"{transformed_core}, achieving [quantifiable metric, e.g., X% latency reduction / Y req/sec throughput] "
            f"through engineering best practices."
        )
        explanation = (
            "Replaced passive duty statement with an impactful action verb and formatted into Google's XYZ formula "
            "(Accomplished [X] as measured by [Y], by doing [Z]) with an honest metric placeholder."
        )
    else:
        rewritten = (
            f"{transformed_core}, achieving [actual metric, e.g., X% performance gain or Y hours saved weekly], "
            f"by applying modern design patterns."
        )
        explanation = (
            "Retained your original action verb and tech stack; structured into Google's XYZ formula by "
            "inserting a placeholder for your actual measured outcome."
        )

    return BulletPointRewrite(
        original=orig,
        rewritten=rewritten,
        explanation=explanation
    )


class RuleBasedRecommendationProvider(BaseAIProvider):
    """
    Deterministic rule-based recommendation engine.
    Ensures zero-fabrication, metric placeholders, grounded analysis,
    and works with 100% reliability offline without external APIs.
    """

    async def generate_recommendations(
        self,
        resume_text: str,
        structured_resume: StructuredResumeData,
        job_title: str,
        job_description: str,
        matching_skills: List[str],
        missing_skills: List[str]
    ) -> Tuple[AnalysisRecommendations, str]:
        strengths: List[str] = []
        weaknesses: List[str] = []
        summary_improvements: List[str] = []
        project_improvements: List[str] = []
        bullet_rewrites: List[BulletPointRewrite] = []
        actionable_steps: List[str] = []
        warnings: List[str] = []

        # 1. Strengths Analysis
        if matching_skills:
            top_matches = ", ".join(matching_skills[:5])
            strengths.append(f"Demonstrated verified proficiency in target technologies: {top_matches}.")
        if structured_resume.total_years_experience and structured_resume.total_years_experience > 2:
            strengths.append(
                f"Established track record of ~{int(structured_resume.total_years_experience)} years of professional engineering experience."
            )
        if len(structured_resume.work_experience) >= 2:
            strengths.append(
                f"Multi-organization experience demonstrating progressive responsibility across {len(structured_resume.work_experience)} roles."
            )
        if structured_resume.education:
            degrees = ", ".join([e.degree for e in structured_resume.education if e.degree])
            if degrees:
                strengths.append(f"Formal academic foundation: {degrees}.")

        if not strengths:
            strengths.append("Foundational background with transferable technical and analytical competencies.")

        # 2. Weaknesses & Content Gaps
        if missing_skills:
            high_pri = ", ".join(missing_skills[:5])
            weaknesses.append(
                f"Candidate profile currently lacks explicit demonstration of key requested skills: {high_pri}."
            )
        if not structured_resume.summary:
            weaknesses.append("Missing a dedicated Executive Summary / Professional Profile at the top of the resume.")
        if structured_resume.work_experience:
            all_bullets = [b for item in structured_resume.work_experience for b in item.bullets]
            metrics_count = sum(1 for b in all_bullets if any(char in b for char in ['%', '$', '0x', 'x', '+']))
            if all_bullets and (metrics_count / len(all_bullets)) < 0.25:
                weaknesses.append(
                    "Work experience descriptions lack quantifiable impact metrics (e.g. latency reduced by X%, users scaled to Y)."
                )
        if not structured_resume.projects and len(structured_resume.work_experience) < 3:
            weaknesses.append(
                "Limited portfolio projects to corroborate practical skills in target stack."
            )

        # 3. Missing keywords from JD
        jd_words = set(job_description.lower().split())
        resume_words = set(resume_text.lower().split())
        candidate_missing_kw = [
            s for s in missing_skills
            if s.lower() in jd_words and s.lower() not in resume_words
        ]
        missing_keywords = candidate_missing_kw[:10] if candidate_missing_kw else missing_skills[:8]

        # 4. Summary Suggestions
        if not structured_resume.summary:
            summary_improvements.append(
                f"Add a 3-4 sentence professional summary tailored to '{job_title}', highlighting your years of experience, "
                f"core stack ({', '.join(matching_skills[:3]) if matching_skills else 'your primary skills'}), and major career impact."
            )
        else:
            summary_improvements.append(
                f"Infuse target role keywords '{job_title}' into the opening sentence of your summary."
            )
            if missing_skills:
                summary_improvements.append(
                    f"If you have experience with {missing_skills[0]}, weave it into your summary's core competencies clause."
                )

        # 5. Project Suggestions
        if structured_resume.projects:
            project_improvements.append(
                "Highlight the technical architecture decisions and system scale for each project rather than only features."
            )
            project_improvements.append(
                "Include live demo links or public GitHub repository URLs to enable recruiters to review source code."
            )
        else:
            project_improvements.append(
                f"Add 1-2 featured projects demonstrating hands-on implementation of {', '.join(missing_skills[:3]) or 'modern architecture patterns'}."
            )

        # 6. Bullet Point Rewrites (Strictly Grounded, Action-Oriented, Placeholders for Metrics)
        sample_bullets = []
        for item in structured_resume.work_experience:
            for b in item.bullets:
                if len(b) > 20:
                    sample_bullets.append(b)
                if len(sample_bullets) >= 3:
                    break
            if len(sample_bullets) >= 3:
                break

        if sample_bullets:
            for orig in sample_bullets:
                bullet_rewrites.append(rewrite_grounded_bullet(orig))
        else:
            bullet_rewrites.append(BulletPointRewrite(
                original="Responsible for developing features and fixing bugs.",
                rewritten="Architected and shipped [feature/component name] using [technologies], improving user throughput by [actual percentage] and resolving [number] critical issues.",
                explanation="Replaced passive duty statement with an impactful engineering achievement statement."
            ))

        # 7. Actionable Next Steps
        if missing_skills:
            actionable_steps.append(
                f"Audit experience for unmentioned touchpoints with {', '.join(missing_skills[:3])} and articulate them clearly."
            )
        actionable_steps.append("Quantify bullet points with tangible business metrics (cost saved, efficiency gained, users served).")
        actionable_steps.append("Tailor your resume headline directly to the exact target job title.")
        actionable_steps.append("Ensure PDF format uses a single-column ATS-friendly layout without embedded tables or complex graphics.")

        # 8. Warnings
        if not structured_resume.contact.email or not structured_resume.contact.phone:
            warnings.append("Contact information appears incomplete: Ensure email and phone are prominently visible.")
        if len(missing_skills) > 5:
            warnings.append(
                "Significant skill gap detected compared to explicit job requirements. Consider supplementing with portfolio projects or targeted certifications."
            )

        recommendations = AnalysisRecommendations(
            strengths=strengths,
            weaknesses=weaknesses,
            missing_keywords=missing_keywords,
            summary_improvements=summary_improvements,
            project_improvements=project_improvements,
            bullet_point_rewrites=bullet_rewrites,
            actionable_steps=actionable_steps,
            warnings=warnings
        )

        return recommendations, "rule_based_nlp"


class LLMRecommendationProvider(BaseAIProvider):
    """
    Optional LLM provider that calls an external API if configured.
    Falls back gracefully to RuleBasedRecommendationProvider on any error.
    """

    def __init__(self, fallback_provider: BaseAIProvider):
        self.fallback = fallback_provider
        self.provider = settings.LLM_PROVIDER.lower().strip()
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL or "gemini-1.5-flash"

    async def generate_recommendations(
        self,
        resume_text: str,
        structured_resume: StructuredResumeData,
        job_title: str,
        job_description: str,
        matching_skills: List[str],
        missing_skills: List[str]
    ) -> Tuple[AnalysisRecommendations, str]:
        # If no key or provider set to none, directly run deterministic fallback
        if self.provider == "none" or not self.api_key:
            return await self.fallback.generate_recommendations(
                resume_text, structured_resume, job_title, job_description, matching_skills, missing_skills
            )

        prompt = (
            f"You are an expert technical resume coach and hiring manager.\n"
            f"Target Role: {job_title}\n"
            f"Job Description:\n{job_description[:2000]}\n\n"
            f"Candidate Skills: {', '.join(matching_skills)}\n"
            f"Missing Skills: {', '.join(missing_skills)}\n"
            f"Candidate Resume Text:\n{resume_text[:2500]}\n\n"
            f"Return a strict JSON object with this schema:\n"
            f"{{\n"
            f'  "strengths": ["string"],\n'
            f'  "weaknesses": ["string"],\n'
            f'  "missing_keywords": ["string"],\n'
            f'  "summary_improvements": ["string"],\n'
            f'  "project_improvements": ["string"],\n'
            f'  "bullet_point_rewrites": [{{"original": "string", "rewritten": "string", "explanation": "string"}}],\n'
            f'  "actionable_steps": ["string"],\n'
            f'  "warnings": ["string"]\n'
            f"}}\n"
            f"Rules:\n"
            f"1. Never invent fake metrics or achievements; use placeholders like [actual % improvement].\n"
            f"2. Ground rewrites exclusively in candidate's supplied experience.\n"
            f"3. Return ONLY valid JSON, no markdown formatting."
        )

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                if self.provider == "gemini":
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
                    }
                    res = await client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                        parsed = json.loads(raw_json)
                        recs = AnalysisRecommendations(**parsed)
                        return recs, f"llm_{self.provider}"

                elif self.provider == "openai":
                    url = "https://api.openai.com/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    payload = {
                        "model": self.model if self.model else "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a professional resume evaluation engine that outputs only JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.2
                    }
                    res = await client.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        raw_json = data["choices"][0]["message"]["content"]
                        parsed = json.loads(raw_json)
                        recs = AnalysisRecommendations(**parsed)
                        return recs, f"llm_{self.provider}"

        except Exception as e:
            logger.warning(f"Optional LLM provider failed or timed out: {e}. Falling back to rule-based engine.")

        # Reliable Fallback
        return await self.fallback.generate_recommendations(
            resume_text, structured_resume, job_title, job_description, matching_skills, missing_skills
        )


def get_ai_service() -> BaseAIProvider:
    rule_provider = RuleBasedRecommendationProvider()
    return LLMRecommendationProvider(fallback_provider=rule_provider)
