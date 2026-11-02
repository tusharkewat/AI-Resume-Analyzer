from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    overall_score = Column(Float, nullable=False)
    score_breakdown = Column(JSON, nullable=False, default=dict)
    matching_skills = Column(JSON, nullable=False, default=list)
    missing_or_unverified_skills = Column(JSON, nullable=False, default=list)
    recommendations = Column(JSON, nullable=False, default=dict)
    analysis_method = Column(String(100), nullable=False, default="rule_based_nlp")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="analyses")
    resume = relationship("Resume", back_populates="analyses")
