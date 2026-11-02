import json
from datetime import datetime, timezone
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.security.password import get_password_hash
from app.services.skill_matcher import SkillMatcherService
from app.services.scoring_engine import ScoringEngineService
from app.services.information_extractor import InformationExtractorService
from app.services.ai_provider import RuleBasedRecommendationProvider


def seed_demo_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if demo user already exists
        existing = db.query(User).filter(User.email == "alice@example.com").first()
        if existing:
            print("Demo user already exists.")
            return

        print("Seeding demo candidate Alice...")
        demo_user = User(
            full_name="Alice Developer",
            email="alice@example.com",
            hashed_password=get_password_hash("StrongPassword123!"),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

        sample_resume_text = (
            "Alice Developer\n"
            "alice@example.com | (555) 123-4567 | San Francisco, CA\n\n"
            "Professional Summary\n"
            "Results-driven Senior Software Engineer with 6+ years of experience engineering high-scale distributed systems, RESTful microservices, and reactive web applications.\n\n"
            "Technical Skills\n"
            "Python, FastAPI, Django, React, TypeScript, PostgreSQL, Redis, Docker, Kubernetes, AWS, Git, CI/CD, Microservices, Problem Solving, Leadership\n\n"
            "Work Experience\n"
            "Senior Software Engineer | CloudTech Solutions | 2021 - Present\n"
            "- Architected high-throughput microservices using FastAPI and Docker, processing 50k requests per second.\n"
            "- Optimized PostgreSQL database queries and indexing strategies, decreasing query latency by 35%.\n"
            "- Spearheaded automated CI/CD deployment pipelines using GitHub Actions.\n\n"
            "Full Stack Developer | Nexa Digital | 2018 - 2021\n"
            "- Engineered responsive web applications utilizing React and TypeScript.\n"
            "- Designed RESTful APIs in Python backed by PostgreSQL and Redis caches.\n\n"
            "Education\n"
            "Bachelor of Science in Computer Science | University of California, Berkeley | 2018\n"
        )

        structured_data = InformationExtractorService.extract_structured_data(sample_resume_text)

        resume = Resume(
            user_id=demo_user.id,
            original_filename="Alice_Developer_Resume.pdf",
            file_type="pdf",
            extracted_text=sample_resume_text,
            structured_data=structured_data.model_dump(),
            created_at=datetime.now(timezone.utc)
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        sample_job_title = "Senior Backend Engineer"
        sample_jd = (
            "We are seeking a Senior Backend Engineer to scale our distributed cloud platform.\n\n"
            "Responsibilities:\n"
            "- Build high-performance REST APIs and microservices using Python and FastAPI.\n"
            "- Optimize database schemas and queries in PostgreSQL and Redis.\n"
            "- Containerize services with Docker and manage deployments on Kubernetes and AWS.\n"
            "- Collaborate with cross-functional engineering teams.\n\n"
            "Requirements:\n"
            "- 4+ years of professional backend software development.\n"
            "- Strong proficiency in Python, FastAPI, Docker, and PostgreSQL.\n"
            "- Hands-on experience with Kubernetes, AWS, and CI/CD.\n"
            "- Bachelor's degree in Computer Science or equivalent."
        )

        matching_skills, missing_skills, skills_score = SkillMatcherService.match_skills(
            sample_resume_text,
            structured_data.technical_skills + structured_data.soft_skills,
            sample_jd
        )

        overall_score, breakdown = ScoringEngineService.calculate_score(
            sample_resume_text,
            structured_data,
            sample_jd,
            skills_score
        )

        # Generate rule-based recommendations
        import asyncio
        rule_ai = RuleBasedRecommendationProvider()
        recs, method = asyncio.run(
            rule_ai.generate_recommendations(
                sample_resume_text,
                structured_data,
                sample_job_title,
                sample_jd,
                [m.skill for m in matching_skills],
                [m.skill for m in missing_skills]
            )
        )

        analysis = Analysis(
            user_id=demo_user.id,
            resume_id=resume.id,
            job_title=sample_job_title,
            job_description=sample_jd,
            overall_score=overall_score,
            score_breakdown=breakdown.model_dump(),
            matching_skills=[m.model_dump() for m in matching_skills],
            missing_or_unverified_skills=[m.model_dump() for m in missing_skills],
            recommendations=recs.model_dump(),
            analysis_method=method,
            created_at=datetime.now(timezone.utc)
        )
        db.add(analysis)
        db.commit()
        print("Demo seed complete! Alice Developer created with resume and analysis.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
