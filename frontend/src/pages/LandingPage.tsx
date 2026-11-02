import React from 'react';
import {
  CheckCircle,
  Cpu,
  ShieldCheck,
  FileText,
  ArrowRight,
  Sparkles,
  BarChart3,
  Layers,
  Lock
} from 'lucide-react';

interface LandingPageProps {
  navigate: (path: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ navigate }) => {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-28 bg-gradient-to-b from-indigo-50/50 via-white to-slate-50 dark:from-slate-900/50 dark:via-slate-950 dark:to-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-indigo-50 dark:bg-indigo-950/70 border border-indigo-200/60 dark:border-indigo-800/60 text-indigo-700 dark:text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-8">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Deterministic NLP &bull; Explainable Matching &bull; Zero Paid API Reliance</span>
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight max-w-4xl mx-auto">
            Bridge the Gap Between Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600 dark:from-indigo-400 dark:to-violet-400">Resume</span> and Your Target <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600 dark:from-indigo-400 dark:to-violet-400">Job Description</span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Upload your resume in PDF or DOCX, paste any job description, and receive an explainable match breakdown, verified skill evidence, and grounded bullet-point rewrites.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => navigate('/register')}
              className="w-full sm:w-auto px-8 py-3.5 text-base font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition-all transform hover:-translate-y-0.5"
            >
              <span>Start Free Analysis</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate('/login')}
              className="w-full sm:w-auto px-8 py-3.5 text-base font-semibold text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl shadow-sm transition-all"
            >
              Explore Sample Report
            </button>
          </div>

          {/* Value Props Bar */}
          <div className="mt-14 pt-8 border-t border-slate-200/70 dark:border-slate-800/70 grid grid-cols-2 md:grid-cols-4 gap-6 text-slate-600 dark:text-slate-400 text-xs sm:text-sm font-medium">
            <div className="flex items-center justify-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-500" />
              <span>PDF & DOCX Support</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-500" />
              <span>TF-IDF Content Similarity</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-500" />
              <span>XYZ Bullet Rewrites</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-500" />
              <span>Executive PDF Downloads</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3-Step Workflow Section */}
      <section className="py-16 md:py-24 bg-white dark:bg-slate-900/60 border-y border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
              How It Works
            </h2>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white">
              Three Steps to ATS Alignment
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="relative p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 font-bold flex items-center justify-center text-lg mb-5">
                01
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                Upload Resume
              </h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Provide your existing resume in PDF or DOCX format. The backend extracts clean text, detects image-only scans, and parses structured entities.
              </p>
            </div>

            {/* Step 2 */}
            <div className="relative p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 font-bold flex items-center justify-center text-lg mb-5">
                02
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                Input Target Role & Job
              </h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Paste any live job posting. The scoring engine compares technical skills, semantic context (TF-IDF cosine similarity), and experience level.
              </p>
            </div>

            {/* Step 3 */}
            <div className="relative p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 font-bold flex items-center justify-center text-lg mb-5">
                03
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                Review & Optimize
              </h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                Inspect matching skills with exact resume citation, uncover missing keywords, review actionable bullet rewrites, and download an executive PDF report.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Breakdown Grid */}
      <section className="py-16 md:py-24 bg-slate-50 dark:bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
              Engineered For Transparency
            </h2>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white">
              No Black Boxes. Explainable Criteria.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <div className="p-3 w-fit rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 mb-4">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Weighted Scoring Architecture</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                Skills coverage (50%), TF-IDF semantic overlap (25%), experience seniority (15%), and degree requirements (10%). Reallocated dynamically if education is not specified.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <div className="p-3 w-fit rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 mb-4">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Grounded Recommendations</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                Never hallucinates fake companies or phantom metrics. Provides metric placeholders like [actual percentage] for honest candidate self-quantification.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <div className="p-3 w-fit rounded-xl bg-purple-50 dark:bg-purple-950 text-purple-600 dark:text-purple-400 mb-4">
                <Layers className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Canonical Skill Aliases</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                Normalizes aliases like "k8s" &rarr; "Kubernetes", "Postgres" &rarr; "PostgreSQL", and "TS" &rarr; "TypeScript" to prevent double-counting or false negatives.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <div className="p-3 w-fit rounded-xl bg-rose-50 dark:bg-rose-950 text-rose-600 dark:text-rose-400 mb-4">
                <Lock className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Strict Multi-Tenant Security</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                Argon2 password hashing, JWT bearer tokens, and row-level ownership authorization. A user can only access, view, or delete their own data.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <div className="p-3 w-fit rounded-xl bg-amber-50 dark:bg-amber-950 text-amber-600 dark:text-amber-400 mb-4">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Downloadable PDF Reports</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                Export comprehensive, formatted PDF summaries powered by ReportLab to take offline, share with coaches, or track revision progress.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <div className="p-3 w-fit rounded-xl bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400 mb-4">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Fair & Non-Discriminatory</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                Algorithms intentionally omit demographic, gender, age, ethnicity, and protected characteristics, focusing exclusively on skill and experience alignment.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-xs">
              RM
            </div>
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              AI Resume Analyzer & Job Matcher
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 text-center sm:text-right">
            Scores are heuristic algorithmic estimates and do not guarantee interview selection or hiring outcomes.
          </p>
        </div>
      </footer>
    </div>
  );
};
