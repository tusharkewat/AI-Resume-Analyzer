import pytest
from app.services.ai_provider import (
    rewrite_grounded_bullet,
    RuleBasedRecommendationProvider
)
from app.schemas.resume import (
    StructuredResumeData,
    ContactInfo,
    WorkExperienceItem
)


def test_rewrite_grounded_bullet_passive_voice():
    # Passive duty phrasing
    bullet = "Responsible for the development of backend microservices using FastAPI and Docker."
    result = rewrite_grounded_bullet(bullet)
    
    # Must not duplicate words like "Engineered and delivered architected"
    assert "architected and developed architected" not in result.rewritten.lower()
    # Must preserve proper noun casing (FastAPI, Docker)
    assert "FastAPI" in result.rewritten
    assert "Docker" in result.rewritten
    # Must use honest metric placeholder instead of fabricating fake percentages
    assert "[" in result.rewritten and "]" in result.rewritten
    assert "metric" in result.rewritten.lower() or "latency" in result.rewritten.lower()


def test_rewrite_grounded_bullet_already_active_and_has_metric():
    bullet = "Optimized database queries in PostgreSQL, reducing query latency by 45%."
    result = rewrite_grounded_bullet(bullet)
    
    # Must retain existing 45% metric
    assert "45%" in result.rewritten
    assert "PostgreSQL" in result.rewritten
    # Should not fabricate a contradictory placeholder when metric is already present
    assert "[" not in result.rewritten


def test_rewrite_grounded_bullet_no_duplicate_verbs():
    # Bullet already starting with strong verb
    bullet = "Architected a distributed event-driven message queue using Redis and Celery."
    result = rewrite_grounded_bullet(bullet)
    
    # Should not double prefix with "Engineered and delivered Architected"
    words = result.rewritten.split()
    assert words[0].lower() == "architected"
    assert "Redis" in result.rewritten
    assert "Celery" in result.rewritten


@pytest.mark.asyncio
async def test_rule_based_provider_recommendations_grounding():
    provider = RuleBasedRecommendationProvider()
    resume_data = StructuredResumeData(
        contact=ContactInfo(full_name="Jane Developer", email="jane@example.com"),
        technical_skills=["Python", "FastAPI"],
        soft_skills=["Team Leadership"],
        work_experience=[
            WorkExperienceItem(
                title="Backend Developer",
                company="Tech Corp",
                dates="2021 - Present",
                bullets=[
                    "Responsible for developing backend REST APIs.",
                    "Improved API response times by 30%."
                ]
            )
        ],
        education=[],
        certifications=[],
        projects=[],
        total_years_experience=3.0
    )

    recs, method = await provider.generate_recommendations(
        resume_text="Backend Developer at Tech Corp developing backend REST APIs.",
        structured_resume=resume_data,
        job_title="Senior Backend Engineer",
        job_description="Seeking a Senior Backend Engineer proficient in Python, FastAPI, Docker, and Kubernetes.",
        matching_skills=["Python", "FastAPI", "Docker"],
        missing_skills=["Kubernetes"]
    )

    assert method == "rule_based_nlp"
    assert len(recs.bullet_point_rewrites) >= 1
    # Check that bullet rewrites retain candidate context
    assert any("REST APIs" in b.rewritten for b in recs.bullet_point_rewrites)
    # Check missing skills advice is present in weaknesses/missing_keywords
    assert any("Kubernetes" in w for w in recs.weaknesses) or "Kubernetes" in recs.missing_keywords
