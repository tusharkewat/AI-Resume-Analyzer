import React, { useEffect, useState } from 'react';
import { analysisService } from '../services/analyses';
import { AnalysisListItem } from '../types';
import { ConfirmationModal } from '../components/ConfirmationModal';
import {
  History,
  Search,
  FileText,
  Clock,
  Trash2,
  Download,
  PlusCircle
} from 'lucide-react';

interface HistoryPageProps {
  navigate: (path: string) => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ navigate }) => {
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [itemToDelete, setItemToDelete] = useState<AnalysisListItem | null>(null);

  const fetchAnalyses = async () => {
    try {
      const data = await analysisService.list();
      setAnalyses(data);
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const handleDelete = async () => {
    if (!itemToDelete) return;
    try {
      await analysisService.delete(itemToDelete.id);
      setAnalyses(prev => prev.filter(a => a.id !== itemToDelete.id));
      setItemToDelete(null);
    } catch {
      alert('Failed to delete report.');
    }
  };

  const handleDownload = async (item: AnalysisListItem, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const safeName = `Resume_Analysis_${item.job_title.replace(/\s+/g, '_')}_${item.id}.pdf`;
      await analysisService.downloadReport(item.id, safeName);
    } catch {
      alert('Failed to download PDF report.');
    }
  };

  const filtered = analyses.filter(a =>
    a.job_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (a.resume_filename && a.resume_filename.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
            Analysis History
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            View, search, download, or delete past resume evaluations
          </p>
        </div>

        <button
          onClick={() => navigate('/analyze')}
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition-all self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Analysis</span>
        </button>
      </div>

      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
          <Search className="w-4 h-4" />
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by job title or resume filename..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400">Loading history...</div>
      ) : analyses.length === 0 ? (
        <div className="p-12 text-center rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 bg-white dark:bg-slate-900">
          <History className="w-12 h-12 mx-auto text-slate-400 mb-3" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white">No Previous Evaluations</h3>
          <p className="mt-1 text-sm text-slate-500 max-w-sm mx-auto">
            Run your first match to start compiling evaluation records and tracking resume optimization progress.
          </p>
          <button
            onClick={() => navigate('/analyze')}
            className="mt-5 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Run Resume Match
          </button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-8 text-center text-slate-500">
          No evaluations matched "{searchQuery}".
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {filtered.map((item) => {
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
                  className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center space-x-3">
                      <span className={`px-2.5 py-0.5 text-xs font-bold rounded-md ${badgeClass}`}>
                        {Math.round(item.overall_score)}%
                      </span>
                      <h3 className="text-base font-bold text-slate-900 dark:text-white hover:text-indigo-600 transition-colors">
                        {item.job_title}
                      </h3>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
                      <span className="flex items-center space-x-1">
                        <FileText className="w-3.5 h-3.5" />
                        <span>{item.resume_filename || 'Uploaded Resume'}</span>
                      </span>
                      <span>&bull;</span>
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{new Date(item.created_at).toLocaleDateString()}</span>
                      </span>
                      <span>&bull;</span>
                      <span className="capitalize">{item.analysis_method.replace('_', ' ')}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 self-end sm:self-center">
                    <button
                      onClick={(e) => handleDownload(item, e)}
                      title="Download PDF Report"
                      className="p-2 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setItemToDelete(item);
                      }}
                      title="Delete Evaluation"
                      className="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={!!itemToDelete}
        title="Delete Analysis Report"
        message={`Are you sure you want to delete the evaluation report for "${itemToDelete?.job_title}"? This action cannot be undone.`}
        confirmLabel="Delete Report"
        onConfirm={handleDelete}
        onCancel={() => setItemToDelete(null)}
      />
    </div>
  );
};
