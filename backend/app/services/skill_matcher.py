import re
from typing import Dict, List, Tuple
from app.services.information_extractor import SKILL_TAXONOMY
from app.schemas.analysis import MatchingSkillItem, MissingSkillItem


class SkillMatcherService:
    """Matches candidate skills with job description requirements using canonical skill mappings."""

    @staticmethod
    def extract_job_skills(job_description: str) -> Tuple[List[str], List[str]]:
        """
        Extracts skills from job description, splitting into required vs preferred based on context.
        """
        jd_lower = f" {job_description.lower()} "
        required_skills: List[str] = []
        preferred_skills: List[str] = []

        # Find preferred section if any
        pref_split = re.split(r'\b(?:preferred|nice to have|bonus|plus)\b', jd_lower, maxsplit=1)
        required_part = pref_split[0]
        preferred_part = pref_split[1] if len(pref_split) > 1 else ""

        for category, skill_map in SKILL_TAXONOMY.items():
            for canonical, aliases in skill_map.items():
                in_req = False
                in_pref = False

                for alias in aliases:
                    escaped = re.escape(alias)
                    pattern = r'(?<![a-zA-Z0-9])' + escaped + r'(?![a-zA-Z0-9])'

                    if re.search(pattern, required_part):
                        in_req = True
                        break
                    elif preferred_part and re.search(pattern, preferred_part):
                        in_pref = True
                        break

                if in_req:
                    if canonical not in required_skills:
                        required_skills.append(canonical)
                elif in_pref:
                    if canonical not in preferred_skills:
                        preferred_skills.append(canonical)

        return required_skills, preferred_skills

    @staticmethod
    def match_skills(
        resume_text: str,
        resume_skills: List[str],
        job_description: str
    ) -> Tuple[List[MatchingSkillItem], List[MissingSkillItem], float]:
        """
        Evaluates skills match:
        - Matching skills with evidence from resume
        - Missing skills with priority and recommendation
        - Match score (0 to 100)
        """
        required_job_skills, preferred_job_skills = SkillMatcherService.extract_job_skills(job_description)
        all_job_skills = list(dict.fromkeys(required_job_skills + preferred_job_skills))

        # If job description mentions no standard skills, fall back to keyword overlap
        if not all_job_skills:
            # Fall back to skills present in resume that appear in JD
            for category, skill_map in SKILL_TAXONOMY.items():
                for canonical, aliases in skill_map.items():
                    escaped = re.escape(canonical.lower())
                    if re.search(r'(?<![a-zA-Z0-9])' + escaped + r'(?![a-zA-Z0-9])', job_description.lower()):
                        all_job_skills.append(canonical)
                        required_job_skills.append(canonical)

        matching_items: List[MatchingSkillItem] = []
        missing_items: List[MissingSkillItem] = []

        resume_lower = resume_text.lower()

        # Build category lookup
        canonical_to_cat: Dict[str, str] = {}
        canonical_to_aliases: Dict[str, List[str]] = {}
        for cat, skills in SKILL_TAXONOMY.items():
            for c_skill, aliases in skills.items():
                canonical_to_cat[c_skill] = cat
                canonical_to_aliases[c_skill] = aliases

        matched_count = 0
        total_eval_skills = len(all_job_skills)

        for skill in all_job_skills:
            category = canonical_to_cat.get(skill, "technical")
            aliases = canonical_to_aliases.get(skill, [skill.lower()])

            # Check if skill in resume
            found = False
            match_type = "exact"
            matched_alias = None

            if skill in resume_skills:
                found = True
                match_type = "exact"
            else:
                for alias in aliases:
                    escaped = re.escape(alias)
                    if re.search(r'(?<![a-zA-Z0-9])' + escaped + r'(?![a-zA-Z0-9])', resume_lower):
                        found = True
                        matched_alias = alias
                        match_type = "alias" if alias != skill.lower() else "exact"
                        break

            if found:
                # Find an evidence snippet in resume
                search_term = matched_alias or skill.lower()
                pattern = re.compile(rf'([^.\n]*?{re.escape(search_term)}[^.\n]*)', re.IGNORECASE)
                snip_match = pattern.search(resume_text)
                evidence = snip_match.group(0).strip()[:140] if snip_match else f"Mentioned in resume under {category}"

                matching_items.append(MatchingSkillItem(
                    skill=skill,
                    category=category,
                    match_type=match_type,
                    evidence=evidence
                ))
                matched_count += 1
            else:
                importance = "required" if skill in required_job_skills else "preferred"
                suggestion = (
                    f"Add concrete experience or project implementations highlighting {skill} "
                    f"if you possess this competency."
                )
                missing_items.append(MissingSkillItem(
                    skill=skill,
                    category=category,
                    importance=importance,
                    suggestion=suggestion
                ))

        if total_eval_skills == 0:
            # Fall back to meaningful token overlap between candidate resume and job description
            jd_tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower()))
            resume_tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_lower))
            overlap = len(jd_tokens.intersection(resume_tokens))
            if jd_tokens and overlap > 0:
                skills_score = min(100.0, round((overlap / max(len(jd_tokens), 10)) * 100.0, 1))
            else:
                skills_score = 0.0
        else:
            skills_score = round((matched_count / total_eval_skills) * 100.0, 1)

        return matching_items, missing_items, skills_score
