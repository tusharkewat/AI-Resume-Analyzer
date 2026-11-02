from app.services.scoring_engine import ScoringEngineService
from app.services.skill_matcher import SkillMatcherService
from app.schemas.resume import StructuredResumeData, EducationItem, WorkExperienceItem


def test_scoring_engine_calculation():
    resume_text = (
        "Alice Developer\n"
        "Proficient in Python, FastAPI, Docker, and PostgreSQL with 5 years experience.\n"
        "Education: Bachelor of Science in Computer Science.\n"
    )
    structured = StructuredResumeData(
        technical_skills=["Python", "FastAPI", "Docker", "PostgreSQL"],
        soft_skills=["Communication"],
        education=[EducationItem(degree="Bachelor of Science in Computer Science")],
        work_experience=[
            WorkExperienceItem(
                title="Senior Backend Engineer",
                bullets=["Developed robust APIs in Python.", "Engineered PostgreSQL schemas."]
            )
        ],
        total_years_experience=5.0
    )

    jd = (
        "We are looking for a Senior Python Developer with 4+ years experience. "
        "Must have strong skills in Python, FastAPI, and PostgreSQL. Docker is preferred. "
        "Requires Bachelor degree in Computer Science or related field."
    )

    matching, missing, skills_score = SkillMatcherService.match_skills(
        resume_text,
        structured.technical_skills,
        jd
    )

    assert skills_score >= 80.0
    assert any(m.skill == "Python" for m in matching)

    overall_score, breakdown = ScoringEngineService.calculate_score(
        resume_text,
        structured,
        jd,
        skills_score
    )

    assert 0 <= overall_score <= 100
    assert breakdown.skills_score == skills_score
    assert breakdown.text_similarity_score > 0
    assert breakdown.education_score == 100.0  # Bachelor matches Bachelor requirement
    assert breakdown.experience_score >= 70.0


def test_scoring_without_education_in_jd():
    resume_text = "Junior developer with HTML, CSS, JavaScript."
    structured = StructuredResumeData(
        technical_skills=["JavaScript", "HTML", "CSS"],
        education=[]
    )
    jd_no_edu = "Front end developer needed for building interactive web pages with JavaScript and HTML."

    matching, missing, skills_score = SkillMatcherService.match_skills(
        resume_text,
        structured.technical_skills,
        jd_no_edu
    )

    overall_score, breakdown = ScoringEngineService.calculate_score(
        resume_text,
        structured,
        jd_no_edu,
        skills_score
    )

    # When education is not in JD, education weight should be 0.0
    assert breakdown.education_weight == 0.0
    assert round(breakdown.skills_weight + breakdown.text_similarity_weight + breakdown.experience_weight, 2) == 1.00
