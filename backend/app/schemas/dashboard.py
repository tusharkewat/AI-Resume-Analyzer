from typing import List, Dict, Any
from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    total_resumes: int
    total_analyses: int
    average_match_score: float
    top_skills: List[Dict[str, Any]]
    recent_analyses: List[Dict[str, Any]]
