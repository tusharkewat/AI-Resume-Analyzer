import React, { useEffect, useState } from 'react';
import { analysisService } from '../services/analyses';
import { Analysis } from '../types';
import { ScoreGauge } from '../components/ScoreGauge';
import { SkillsBadgeList } from '../components/SkillsBadgeList';
import {
  Download,
  ArrowLeft,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  Sparkles,
  RefreshCw,
  ShieldAlert,
  Clock,
  Layers
} from 'lucide-react';

interface AnalysisResultPageProps {
  analysisId: number;
  navigate: (path: string) => void;
}

export const AnalysisResultPage: React.FC<AnalysisResultPageProps> = ({
  analysisId,
  navigate,
}) => {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const data = await analysisService.get(analysisId);
        setAnalysis(data);
      } catch (err: any) {
        setError('Failed to load analysis report.');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalysis();
  }, [analysisId]);

  const handleDownload = async () => {
    if (!analysis) return;
    setDownloading(true);
    try {
      const safeName = `Resume_Analysis_${analysis.job_title.replace(/\s+/g, '_')}_${analysis.id}.pdf`;
      await analysisService.downloadReport(analysis.id, safeName);
    } catch {
      alert('Failed to download PDF report. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Loading comprehensive evaluation report...</p>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center space-y-4">
        <div className="p-3 w-fit mx-auto rounded-full bg-rose-100 text-rose-600">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Report Not Found</h2>
        <p className="text-sm text-slate-500">{error || 'This report does not exist or you do not have permission to view it.'}</p>
        <button
          onClick={() => navigate('/dashboard')}
          className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const sb = analysis.score_breakdown;
  const recs = analysis.recommendations;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <button
            onClick={() => navigate('/history')}
            className="inline-flex items-center space-x-1 text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to History</span>
          </button>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
            {analysis.job_title}
          </h1>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 flex items-center space-x-2">
            <span>Resume: <b>{analysis.resume_filename || 'Candidate Resume'}</b></span>
            <span>&bull;</span>
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>Evaluated on {new Date(analysis.created_at).toLocaleDateString()}</span>
            <span>&bull;</span>
            <span className="capitalize font-medium text-slate-600 dark:text-slate-300">
              Mode: {analysis.analysis_method.replace('_', ' ')}
            </span>
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate('/analyze')}
            className="px-4 py-2.5 rounded-xl text-sm font-semibold border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-colors flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>New Match</span>
          </button>

          <button
            onClick={handleDownload}
            disabled={downloading}
            className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-600/30 transition-all flex items-center space-x-2 disabled:opacity-50"
          >
            {downloading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            <span>Export Official PDF</span>
          </button>
        </div>
      </div>

      {/* Main Score & Component Breakdown Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Score Gauge */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center text-center">
          <ScoreGauge score={analysis.overall_score} size={150} />
          <p className="mt-4 text-xs text-slate-500 dark:text-slate-400 max-w-xs leading-relaxed">
            {sb.explanation}
          </p>
        </div>

        {/* Right: Component Cards Grid */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Skills Score Card */}
          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-slate-500">Skills Coverage</span>
              <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">Weight: {Math.round(sb.skills_weight * 100)}%</span>
            </div>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-slate-900 dark:text-white">{Math.round(sb.skills_score)}%</span>
              <span className="text-xs text-slate-400">Exact & Alias Match</span>
            </div>
            <div className="mt-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${sb.skills_score}%` }} />
            </div>
          </div>

          {/* Text Similarity Card */}
          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-slate-500">TF-IDF Similarity</span>
              <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">Weight: {Math.round(sb.text_similarity_weight * 100)}%</span>
            </div>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-slate-900 dark:text-white">{Math.round(sb.text_similarity_score)}%</span>
              <span className="text-xs text-slate-400">Contextual Overlap</span>
            </div>
            <div className="mt-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${sb.text_similarity_score}%` }} />
            </div>
          </div>

          {/* Experience Relevance Card */}
          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-slate-500">Experience Alignment</span>
              <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">Weight: {Math.round(sb.experience_weight * 100)}%</span>
            </div>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-slate-900 dark:text-white">{Math.round(sb.experience_score)}%</span>
              <span className="text-xs text-slate-400">Tenure & Seniority</span>
            </div>
            <div className="mt-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${sb.experience_score}%` }} />
            </div>
          </div>

          {/* Education & Readability */}
          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-slate-500">Education Alignment</span>
              <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">Weight: {Math.round(sb.education_weight * 100)}%</span>
            </div>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-slate-900 dark:text-white">{Math.round(sb.education_score)}%</span>
              <span className="text-xs text-slate-400">Readability: {Math.round(sb.readability_score)}%</span>
            </div>
            <div className="mt-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="bg-amber-500 h-2 rounded-full" style={{ width: `${sb.education_score}%` }} />
            </div>
          </div>
        </div>
      </div>

      {/* Skills Matrix Section */}
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">
            Skills Breakdown & Evidence
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Click on any item to view supporting resume quotations or coaching advice
          </p>
        </div>
        <SkillsBadgeList
          matchingSkills={analysis.matching_skills}
          missingSkills={analysis.missing_or_unverified_skills}
        />
      </div>

      {/* Grounded Recommendations & Growth Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strengths */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400">
            <CheckCircle className="w-5 h-5" />
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Profile Strengths</h3>
          </div>
          <ul className="space-y-2.5 text-sm text-slate-600 dark:text-slate-300">
            {recs.strengths.map((s, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-emerald-500 font-bold mt-0.5">&bull;</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Weaknesses / Gaps */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400">
            <AlertTriangle className="w-5 h-5" />
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Content Gaps & Opportunities</h3>
          </div>
          <ul className="space-y-2.5 text-sm text-slate-600 dark:text-slate-300">
            {recs.weaknesses.map((w, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-amber-500 font-bold mt-0.5">&bull;</span>
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Bullet Point Rewrites (Strictly Grounded, Action-Oriented, Placeholders) */}
      {recs.bullet_point_rewrites && recs.bullet_point_rewrites.length > 0 && (
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-indigo-600 dark:text-indigo-400">
            <Sparkles className="w-5 h-5" />
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Targeted Bullet-Point Enhancements (XYZ Formula)
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Suggested reformulations strictly grounded in your provided experience. Uses <i>[metric placeholders]</i> for truthful candidate calibration.
          </p>

          <div className="space-y-4">
            {recs.bullet_point_rewrites.map((rw, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Original Experience Bullet</span>
                  <p className="mt-0.5 text-sm italic text-slate-600 dark:text-slate-400">
                    "{rw.original}"
                  </p>
                </div>
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Enhanced Impact Version</span>
                  <p className="mt-0.5 text-sm font-medium text-slate-900 dark:text-white bg-emerald-50 dark:bg-emerald-950/20 p-2.5 rounded-lg border border-emerald-100 dark:border-emerald-900/40">
                    {rw.rewritten}
                  </p>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-sans">
                  <b>Why:</b> {rw.explanation}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actionable Next Steps & Warnings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Next steps */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-indigo-600 dark:text-indigo-400">
            <Lightbulb className="w-5 h-5" />
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Prioritized Next Steps</h3>
          </div>
          <ul className="space-y-2.5 text-sm text-slate-600 dark:text-slate-300">
            {recs.actionable_steps.map((step, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="w-5 h-5 rounded-full bg-indigo-100 dark:bg-indigo-950 text-indigo-600 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Missing Keywords Checklist */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-slate-700 dark:text-slate-300">
            <Layers className="w-5 h-5" />
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Recommended Target Keywords</h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Keywords prominent in the job description that may enhance ATS visibility if relevant:
          </p>
          <div className="flex flex-wrap gap-2 pt-1">
            {recs.missing_keywords.map((kw, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700"
              >
                +{kw}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Prominent Disclaimer Callout */}
      <div className="p-4 rounded-xl bg-slate-100 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 flex items-start space-x-3 text-xs text-slate-500 dark:text-slate-400">
        <ShieldAlert className="w-5 h-5 text-slate-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-slate-700 dark:text-slate-300">Algorithmic Estimation Notice:</span>{' '}
          {analysis.disclaimer}
        </div>
      </div>
    </div>
  );
};
