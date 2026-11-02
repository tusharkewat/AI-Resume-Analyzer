import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import { MatchingSkill, MissingSkill } from '../types';

interface SkillsBadgeListProps {
  matchingSkills: MatchingSkill[];
  missingSkills: MissingSkill[];
}

export const SkillsBadgeList: React.FC<SkillsBadgeListProps> = ({
  matchingSkills,
  missingSkills,
}) => {
  const [activeTab, setActiveTab] = useState<'matching' | 'missing'>('matching');
  const [expandedSkill, setExpandedSkill] = useState<string | null>(null);

  const toggleExpand = (skill: string) => {
    setExpandedSkill(prev => prev === skill ? null : skill);
  };

  return (
    <div className="w-full">
      {/* Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 mb-4">
        <button
          onClick={() => setActiveTab('matching')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 flex items-center space-x-2 transition-colors ${
            activeTab === 'matching'
              ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400'
              : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
          }`}
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>Matching Skills ({matchingSkills.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('missing')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 flex items-center space-x-2 transition-colors ${
            activeTab === 'missing'
              ? 'border-amber-500 text-amber-600 dark:text-amber-400'
              : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          <span>Missing or Unverified ({missingSkills.length})</span>
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'matching' && (
        <div>
          {matchingSkills.length === 0 ? (
            <p className="text-sm text-slate-500 dark:text-slate-400 py-4 text-center">
              No direct technical skills from the job description were identified in the resume text.
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {matchingSkills.map((m, idx) => {
                const isExpanded = expandedSkill === m.skill;
                return (
                  <div
                    key={idx}
                    onClick={() => toggleExpand(m.skill)}
                    className="p-3 rounded-lg border border-emerald-100 dark:border-emerald-950/40 bg-emerald-50/40 dark:bg-emerald-950/20 cursor-pointer hover:bg-emerald-50 dark:hover:bg-emerald-950/30 transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500" />
                        <span className="text-sm font-medium text-slate-900 dark:text-white">
                          {m.skill}
                        </span>
                        <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-emerald-200/60 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300">
                          {m.match_type}
                        </span>
                      </div>
                      <span className="text-slate-400 hover:text-slate-600">
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </span>
                    </div>

                    {isExpanded && m.evidence && (
                      <div className="mt-2.5 pt-2 border-t border-emerald-200/50 dark:border-emerald-900/40 text-xs text-slate-600 dark:text-slate-300">
                        <span className="font-semibold text-slate-700 dark:text-slate-200">Evidence in Resume:</span>
                        <p className="mt-0.5 italic text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                          "{m.evidence}"
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {activeTab === 'missing' && (
        <div>
          {missingSkills.length === 0 ? (
            <div className="p-4 rounded-lg bg-emerald-50 dark:bg-emerald-950/20 text-emerald-800 dark:text-emerald-300 text-sm">
              All identified job description skills are supported by evidence in your resume!
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {missingSkills.map((m, idx) => {
                const isExpanded = expandedSkill === m.skill;
                const isReq = m.importance === 'required';
                return (
                  <div
                    key={idx}
                    onClick={() => toggleExpand(m.skill)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      isReq
                        ? 'border-amber-200 dark:border-amber-950/50 bg-amber-50/40 dark:bg-amber-950/20 hover:bg-amber-50 dark:hover:bg-amber-950/30'
                        : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className={`w-2 h-2 rounded-full ${isReq ? 'bg-amber-500' : 'bg-slate-400'}`} />
                        <span className="text-sm font-medium text-slate-900 dark:text-white">
                          {m.skill}
                        </span>
                        <span
                          className={`text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded ${
                            isReq
                              ? 'bg-amber-200/70 text-amber-900 dark:bg-amber-900/40 dark:text-amber-300'
                              : 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                          }`}
                        >
                          {m.importance}
                        </span>
                      </div>
                      <span className="text-slate-400 hover:text-slate-600">
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </span>
                    </div>

                    {isExpanded && (
                      <div className="mt-2.5 pt-2 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300">
                        <span className="font-semibold text-slate-700 dark:text-slate-200">Coaching Suggestion:</span>
                        <p className="mt-0.5 text-slate-500 dark:text-slate-400">
                          {m.suggestion}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
