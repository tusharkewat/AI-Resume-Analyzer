from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.schemas.dashboard import DashboardStatsResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    total_analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).count()

    avg_score_res = db.query(func.avg(Analysis.overall_score)).filter(Analysis.user_id == current_user.id).scalar()
    avg_score = round(float(avg_score_res), 1) if avg_score_res is not None else 0.0

    # Aggregate top skills across candidate resumes
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    skill_counter = Counter()
    for r in resumes:
        s_data = r.structured_data or {}
        tech = s_data.get("technical_skills", [])
        for sk in tech:
            skill_counter[sk] += 1

    top_skills = [{"name": name, "count": count} for name, count in skill_counter.most_common(8)]

    # Fetch recent analyses
    recent = (
        db.query(Analysis, Resume.original_filename)
        .join(Resume, Analysis.resume_id == Resume.id)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(5)
        .all()
    )

    recent_analyses = []
    for a, filename in recent:
        recent_analyses.append({
            "id": a.id,
            "job_title": a.job_title,
            "overall_score": a.overall_score,
            "resume_filename": filename,
            "created_at": a.created_at.isoformat()
        })

    return DashboardStatsResponse(
        total_resumes=total_resumes,
        total_analyses=total_analyses,
        average_match_score=avg_score,
        top_skills=top_skills,
        recent_analyses=recent_analyses
    )
