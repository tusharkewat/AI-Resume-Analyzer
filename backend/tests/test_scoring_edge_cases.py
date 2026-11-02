import pytest
from app.services.scoring_engine import ScoringEngineService
from app.services.skill_matcher import SkillMatcherService
from app.schemas.resume import (
    StructuredResumeData,
    ContactInfo,
    WorkExperienceItem,
    EducationItem
)


@pytest.fixture
def empty_candidate_resume() -> StructuredResumeData:
    return StructuredResumeData(
        contact=ContactInfo(full_name="Fresh Graduate", email="grad@example.com"),
        technical_skills=[],
        soft_skills=[],
        work_experience=[],
        education=[],
        certifications=[],
        projects=[],
        total_years_experience=0.0
    )


def test_experience_score_zero_for_entry_candidate_on_senior_role(empty_candidate_resume):
    jd = "We are seeking a Principal Architect with at least 8 years of production backend experience."
    
    # Calculate score
    score = ScoringEngineService._calculate_experience_score(empty_candidate_resume, jd)
    assert score == 0.0


def test_education_score_zero_when_degree_required_but_none_listed(empty_candidate_resume):
    jd = "Requirements: Bachelor's degree in Computer Science or Software Engineering required."
    
    score, edu_required = ScoringEngineService._calculate_education_score(empty_candidate_resume, jd)
    assert score == 0.0
    assert edu_required is True


def test_tfidf_similarity_short_or_gibberish():
    # 2-word gibberish JD should not crash or return a fake 50%
    score = ScoringEngineService._calculate_tfidf_similarity(
        resume_text="Senior Python developer with experience in microservices and distributed systems.",
        job_description="hi there"
    )
    assert score == 0.0

    # Empty string
    score_empty = ScoringEngineService._calculate_tfidf_similarity(
        resume_text="Python engineer",
        job_description=""
    )
    assert score_empty == 0.0


def test_skill_matcher_fallback_unrecognized_skills():
    # JD with non-standard keywords or standard skills
    matching_items, missing_items, score = SkillMatcherService.match_skills(
        resume_text="Python developer building FastAPI REST APIs and backend services.",
        resume_skills=["Python", "FastAPI"],
        job_description="We need someone to maintain REST APIs and backend services using Python."
    )
    assert score > 0.0
    assert len(matching_items) >= 1
    assert any(m.skill == "Python" for m in matching_items)
