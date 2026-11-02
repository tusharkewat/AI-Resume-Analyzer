import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.schemas.analysis import (
    AnalysisCreateRequest,
    AnalysisResponse,
    AnalysisListItem,
    ScoreBreakdown,
    AnalysisRecommendations
)
from app.schemas.resume import StructuredResumeData
from app.dependencies import get_current_user
from app.services.skill_matcher import SkillMatcherService
from app.services.scoring_engine import ScoringEngineService
from app.services.ai_provider import get_ai_service
from app.services.report_generator import PDFReportGenerator
from app.utils.rate_limiter import rate_limit
from app.config import settings

router = APIRouter(prefix="/analyses", tags=["Analyses"])


@router.post(
    "",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(settings.RATE_LIMIT_ANALYSIS_PER_MINUTE, 60, "create_analysis"))]
)
async def create_analysis(
    request: AnalysisCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify resume ownership
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this resume")

    structured = StructuredResumeData(**resume.structured_data)

    # 1. Match skills
    matching_skills, missing_skills, skills_score = await asyncio.to_thread(
        SkillMatcherService.match_skills,
        resume.extracted_text,
        structured.technical_skills + structured.soft_skills,
        request.job_description
    )

    # 2. Calculate explainable match score & breakdown
    overall_score, breakdown = await asyncio.to_thread(
        ScoringEngineService.calculate_score,
        resume.extracted_text,
        structured,
        request.job_description,
        skills_score
    )

    # 3. Recommendations & Rewrites (AI Provider with rule-based fallback)
    ai_service = get_ai_service()
    recommendations, method_name = await ai_service.generate_recommendations(
        resume_text=resume.extracted_text,
        structured_resume=structured,
        job_title=request.job_title,
        job_description=request.job_description,
        matching_skills=[m.skill for m in matching_skills],
        missing_skills=[m.skill for m in missing_skills]
    )

    # 4. Persist analysis
    analysis = Analysis(
        user_id=current_user.id,
        resume_id=resume.id,
        job_title=request.job_title.strip(),
        job_description=request.job_description.strip(),
        overall_score=overall_score,
        score_breakdown=breakdown.model_dump(),
        matching_skills=[m.model_dump() for m in matching_skills],
        missing_or_unverified_skills=[m.model_dump() for m in missing_skills],
        recommendations=recommendations.model_dump(),
        analysis_method=method_name
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    resp = AnalysisResponse.model_validate(analysis)
    resp.resume_filename = resume.original_filename
    return resp


@router.get("", response_model=List[AnalysisListItem])
def list_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analyses = (
        db.query(Analysis, Resume.original_filename)
        .join(Resume, Analysis.resume_id == Resume.id)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    results = []
    for a, filename in analyses:
        item = AnalysisListItem.model_validate(a)
        item.resume_filename = filename
        results.append(item)
    return results


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis report not found")
    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
    resp = AnalysisResponse.model_validate(analysis)
    if resume:
        resp.resume_filename = resume.original_filename
    return resp


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis report not found")
    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db.delete(analysis)
    db.commit()
    return {"message": "Analysis report deleted successfully."}


@router.get("/{analysis_id}/report")
def download_pdf_report(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis report not found")
    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated resume not found")

    pdf_bytes = PDFReportGenerator.generate_pdf(analysis, resume)
    safe_filename = f"Resume_Analysis_{analysis.job_title.replace(' ', '_')}_{analysis.id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"'
        }
    )
