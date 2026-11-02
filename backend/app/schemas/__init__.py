from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    PasswordChangeRequest,
    UserUpdateRequest
)
from app.schemas.resume import (
    StructuredResumeData,
    ResumeResponse,
    ResumeListItem,
    ContactInfo,
    WorkExperienceItem,
    EducationItem,
    ProjectItem
)
from app.schemas.analysis import (
    AnalysisCreateRequest,
    AnalysisResponse,
    AnalysisListItem,
    ScoreBreakdown,
    MatchingSkillItem,
    MissingSkillItem,
    AnalysisRecommendations
)
from app.schemas.dashboard import DashboardStatsResponse

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "UserResponse",
    "TokenResponse",
    "PasswordChangeRequest",
    "UserUpdateRequest",
    "StructuredResumeData",
    "ResumeResponse",
    "ResumeListItem",
    "ContactInfo",
    "WorkExperienceItem",
    "EducationItem",
    "ProjectItem",
    "AnalysisCreateRequest",
    "AnalysisResponse",
    "AnalysisListItem",
    "ScoreBreakdown",
    "MatchingSkillItem",
    "MissingSkillItem",
    "AnalysisRecommendations",
    "DashboardStatsResponse"
]
