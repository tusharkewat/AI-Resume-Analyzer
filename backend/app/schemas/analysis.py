from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AnalysisCreateRequest(BaseModel):
    resume_id: int
    job_title: str = Field(..., min_length=2, max_length=150)
    job_description: str = Field(..., min_length=20, max_length=15000)


class ScoreBreakdown(BaseModel):
    skills_score: float = Field(..., ge=0, le=100)
    skills_weight: float = Field(0.50)
    text_similarity_score: float = Field(..., ge=0, le=100)
    text_similarity_weight: float = Field(0.25)
    experience_score: float = Field(..., ge=0, le=100)
    experience_weight: float = Field(0.15)
    education_score: float = Field(..., ge=0, le=100)
    education_weight: float = Field(0.10)
    readability_score: float = Field(..., ge=0, le=100)
    explanation: str


class MatchingSkillItem(BaseModel):
    skill: str
    category: str
    match_type: str = "exact"  # "exact", "alias", "inferred"
    evidence: Optional[str] = None


class MissingSkillItem(BaseModel):
    skill: str
    category: str
    importance: str = "required"  # "required", "preferred"
    suggestion: str


class BulletPointRewrite(BaseModel):
    original: str
    rewritten: str
    explanation: str


class AnalysisRecommendations(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    summary_improvements: List[str] = Field(default_factory=list)
    project_improvements: List[str] = Field(default_factory=list)
    bullet_point_rewrites: List[BulletPointRewrite] = Field(default_factory=list)
    actionable_steps: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    resume_filename: Optional[str] = None
    job_title: str
    job_description: str
    overall_score: float
    score_breakdown: ScoreBreakdown
    matching_skills: List[MatchingSkillItem]
    missing_or_unverified_skills: List[MissingSkillItem]
    recommendations: AnalysisRecommendations
    analysis_method: str
    created_at: datetime
    disclaimer: str = (
        "This evaluation is an algorithmic estimation based on keyword matching, "
        "TF-IDF content similarity, and heuristic extraction. It does not predict or guarantee "
        "interview selection or employment decisions."
    )

    model_config = ConfigDict(from_attributes=True)


class AnalysisListItem(BaseModel):
    id: int
    resume_id: int
    resume_filename: Optional[str] = None
    job_title: str
    overall_score: float
    analysis_method: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
