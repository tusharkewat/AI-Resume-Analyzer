export interface User {
  id: number;
  full_name: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ContactInfo {
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
}

export interface WorkExperienceItem {
  title?: string;
  company?: string;
  dates?: string;
  bullets: string[];
}

export interface EducationItem {
  degree?: string;
  institution?: string;
  year?: string;
  details?: string;
}

export interface StructuredResumeData {
  contact: ContactInfo;
  summary?: string;
  technical_skills: string[];
  soft_skills: string[];
  skills_by_category: Record<string, string[]>;
  work_experience: WorkExperienceItem[];
  education: EducationItem[];
  projects: any[];
  certifications: string[];
  languages: string[];
  total_years_experience?: number;
  extracted_keywords: string[];
}

export interface Resume {
  id: number;
  user_id: number;
  original_filename: string;
  file_type: string;
  structured_data: StructuredResumeData;
  created_at: string;
}

export interface ResumeListItem {
  id: number;
  original_filename: string;
  file_type: string;
  created_at: string;
}

export interface ScoreBreakdown {
  skills_score: number;
  skills_weight: number;
  text_similarity_score: number;
  text_similarity_weight: number;
  experience_score: number;
  experience_weight: number;
  education_score: number;
  education_weight: number;
  readability_score: number;
  explanation: string;
}

export interface MatchingSkill {
  skill: string;
  category: string;
  match_type: string;
  evidence?: string;
}

export interface MissingSkill {
  skill: string;
  category: string;
  importance: string;
  suggestion: string;
}

export interface BulletPointRewrite {
  original: string;
  rewritten: string;
  explanation: string;
}

export interface AnalysisRecommendations {
  strengths: string[];
  weaknesses: string[];
  missing_keywords: string[];
  summary_improvements: string[];
  project_improvements: string[];
  bullet_point_rewrites: BulletPointRewrite[];
  actionable_steps: string[];
  warnings: string[];
}

export interface Analysis {
  id: number;
  user_id: number;
  resume_id: number;
  resume_filename?: string;
  job_title: string;
  job_description: string;
  overall_score: number;
  score_breakdown: ScoreBreakdown;
  matching_skills: MatchingSkill[];
  missing_or_unverified_skills: MissingSkill[];
  recommendations: AnalysisRecommendations;
  analysis_method: string;
  created_at: string;
  disclaimer: string;
}

export interface AnalysisListItem {
  id: number;
  resume_id: number;
  resume_filename?: string;
  job_title: string;
  overall_score: number;
  analysis_method: string;
  created_at: string;
}

export interface DashboardStats {
  total_resumes: number;
  total_analyses: number;
  average_match_score: number;
  top_skills: { name: string; count: number }[];
  recent_analyses: {
    id: number;
    job_title: string;
    overall_score: number;
    resume_filename: string;
    created_at: string;
  }[];
}
