import React, { useEffect, useState } from 'react';
import { dashboardService } from '../services/dashboard';
import { DashboardStats } from '../types';
import {
  FileText,
  CheckCircle,
  TrendingUp,
  Sparkles,
  ArrowRight,
  PlusCircle,
  Clock,
  Layers,
  ChevronRight
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

interface DashboardPageProps {
  navigate: (path: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ navigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await dashboardService.getStats();
        setStats(data);
      } catch (err: any) {
        setError('Failed to load dashboard metrics.');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-slate-200 dark:bg-slate-800 rounded w-1/4" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="h-32 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
            <div className="h-32 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
            <div className="h-32 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
          </div>
          <div className="h-64 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
        </div>
      </div>
    );
  }

  const isEmpty = !stats || stats.total_analyses === 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner & Quick Action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
            Candidate Analytics Dashboard
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Overview of parsed documents, skill alignment, and job-fit benchmarks
          </p>
        </div>
        <button
          onClick={() => navigate('/analyze')}
          className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-600/30 transition-all self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Resume Analysis</span>
        </button>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 dark:bg-rose-950/30 text-rose-600 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Total Resumes
            </p>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white">
              {stats?.total_resumes || 0}
            </p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Parsed PDF & DOCX docs
            </p>
          </div>
          <div className="p-3.5 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <FileText className="w-7 h-7" />
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Analyses Performed
            </p>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white">
              {stats?.total_analyses || 0}
            </p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Against specific job descriptions
            </p>
          </div>
          <div className="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
            <CheckCircle className="w-7 h-7" />
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Average Match Score
            </p>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white">
              {stats?.average_match_score ? `${stats.average_match_score}%` : 'N/A'}
            </p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Weighted composite average
            </p>
          </div>
          <div className="p-3.5 rounded-2xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400">
            <TrendingUp className="w-7 h-7" />
          </div>
        </div>
      </div>

      {isEmpty ? (
        /* Empty State */
        <div className="p-12 text-center rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4">
            <Sparkles className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">
            No Analyses Yet
          </h3>
          <p className="mt-1.5 text-sm text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            Upload your first resume and compare it against any job description to view granular skill matching and improvement recommendations.
          </p>
          <button
            onClick={() => navigate('/analyze')}
            className="mt-6 px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-600/30 transition-all inline-flex items-center space-x-2"
          >
            <span>Analyze Your First Resume</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      ) : (
        /* Dashboard Charts & Recent List */
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Skills Chart */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Top Verified Skills
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Most recurring competencies in your resume portfolio
                </p>
              </div>
              <Layers className="w-5 h-5 text-indigo-500" />
            </div>

            {stats?.top_skills && stats.top_skills.length > 0 ? (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats.top_skills} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" width={90} tick={{ fontSize: 12, fill: '#64748b' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1e293b',
                        borderColor: '#334155',
                        borderRadius: '8px',
                        color: '#f8fafc',
                        fontSize: '12px',
                      }}
                    />
                    <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-sm text-slate-500 py-12 text-center">No skills logged yet.</p>
            )}
          </div>

          {/* Recent Analyses List */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Recent Evaluations
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Latest job description comparisons
                </p>
              </div>
              <button
                onClick={() => navigate('/history')}
                className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center space-x-1"
              >
                <span>View All</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              {stats?.recent_analyses.map((item) => {
                let badgeClass = 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-400';
                if (item.overall_score >= 75) {
                  badgeClass = 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-400';
                } else if (item.overall_score >= 50) {
                  badgeClass = 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-400';
                }

                return (
                  <div
                    key={item.id}
                    onClick={() => navigate(`/analysis/${item.id}`)}
                    className="py-3.5 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-800/50 -mx-2 px-2 rounded-xl cursor-pointer transition-colors"
                  >
                    <div className="space-y-1 truncate pr-4">
                      <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                        {item.job_title}
                      </p>
                      <div className="flex items-center space-x-2 text-xs text-slate-500 dark:text-slate-400">
                        <FileText className="w-3.5 h-3.5 text-slate-400" />
                        <span className="truncate max-w-[150px]">{item.resume_filename}</span>
                        <span>&bull;</span>
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        <span>{new Date(item.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 shrink-0">
                      <span className={`px-2.5 py-1 text-xs font-bold rounded-lg ${badgeClass}`}>
                        {Math.round(item.overall_score)}%
                      </span>
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
