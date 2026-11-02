import React, { useState, useEffect } from 'react';
import { resumeService } from '../services/resumes';
import { analysisService } from '../services/analyses';
import { ResumeListItem } from '../types';
import { FileUploader } from '../components/FileUploader';
import {
  Briefcase,
  FileText,
  Sparkles,
  AlertCircle,
  ArrowRight,
  Check
} from 'lucide-react';

interface AnalyzePageProps {
  navigate: (path: string) => void;
}

const SAMPLE_JOB_DESCRIPTION = `We are seeking a Senior Backend Engineer to design and scale our cloud platform.

Responsibilities:
- Build high-performance REST APIs and microservices using Python and FastAPI.
- Optimize database schemas and queries in PostgreSQL.
- Containerize services with Docker and manage deployments on Kubernetes and AWS.
- Collaborate with frontend teams working in React and TypeScript.

Qualifications:
- 4+ years of professional software engineering experience.
- Strong proficiency in Python, Docker, PostgreSQL, and Git.
- Experience with Kubernetes, AWS, and CI/CD pipelines.
- Bachelor's degree in Computer Science or equivalent practical experience.`;

export const AnalyzePage: React.FC<AnalyzePageProps> = ({ navigate }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [existingResumes, setExistingResumes] = useState<ResumeListItem[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchExisting = async () => {
      try {
        const list = await resumeService.list();
        setExistingResumes(list);
        if (list.length > 0) {
          setSelectedResumeId(list[0].id);
        }
      } catch (err) {
        // Not fatal
      }
    };
    fetchExisting();
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedFile && !selectedResumeId) {
      setError('Please upload a resume file (PDF or DOCX) or select an existing one.');
      return;
    }

    if (!jobTitle.trim()) {
      setError('Please enter a target job title.');
      return;
    }

    if (jobDescription.trim().length < 30) {
      setError('Please enter a detailed job description (at least 30 characters).');
      return;
    }

    setIsProcessing(true);
    try {
      let resumeIdToUse = selectedResumeId;

      // If user provided a new file, upload it first
      if (selectedFile) {
        setStatusMessage('Extracting text & parsing entities from resume...');
        const uploaded = await resumeService.upload(selectedFile, (progress) => {
          setUploadProgress(progress);
        });
        resumeIdToUse = uploaded.id;
      }

      setStatusMessage('Evaluating skill alignment & TF-IDF content similarity...');
      const analysis = await analysisService.create({
        resume_id: resumeIdToUse!,
        job_title: jobTitle.trim(),
        job_description: jobDescription.trim(),
      });

      setStatusMessage('Finalizing recommendations...');
      navigate(`/analysis/${analysis.id}`);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Analysis failed. Please ensure file is valid and try again.';
      setError(msg);
      setIsProcessing(false);
      setStatusMessage(null);
    }
  };

  const handlePreFillSample = () => {
    setJobTitle('Senior Backend Engineer');
    setJobDescription(SAMPLE_JOB_DESCRIPTION);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
          Analyze Resume vs. Job Description
        </h1>
        <p className="mt-1.5 text-sm text-slate-500 dark:text-slate-400">
          Upload your resume and compare it against any target role to get an explainable match score and coaching insights.
        </p>
      </div>

      {error && (
        <div className="mb-6 flex items-center space-x-2 p-4 rounded-xl bg-rose-50 dark:bg-rose-950/30 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-900/40 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleAnalyze} className="space-y-8">
        {/* Step 1: Resume Upload / Selection */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <span className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center">
                1
              </span>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">
                Upload or Select Resume
              </h2>
            </div>

            {existingResumes.length > 0 && (
              <span className="text-xs text-slate-400">
                {existingResumes.length} previous resume{existingResumes.length > 1 ? 's' : ''} available
              </span>
            )}
          </div>

          {/* If existing resumes exist, offer selection tab */}
          {existingResumes.length > 0 && !selectedFile && (
            <div className="mb-4">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Use previously parsed resume:
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {existingResumes.map((r) => {
                  const isSelected = selectedResumeId === r.id;
                  return (
                    <div
                      key={r.id}
                      onClick={() => setSelectedResumeId(r.id)}
                      className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                        isSelected
                          ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/40 text-indigo-900 dark:text-indigo-200'
                          : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      <div className="flex items-center space-x-2.5 truncate">
                        <FileText className="w-4 h-4 text-indigo-500 shrink-0" />
                        <span className="text-xs font-medium truncate">{r.original_filename}</span>
                      </div>
                      {isSelected && <Check className="w-4 h-4 text-indigo-600 shrink-0" />}
                    </div>
                  );
                })}
              </div>
              <div className="relative my-4">
                <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-200 dark:border-slate-800" /></div>
                <div className="relative flex justify-center text-xs uppercase"><span className="bg-white dark:bg-slate-900 px-2 text-slate-400">Or upload a new document</span></div>
              </div>
            </div>
          )}

          <FileUploader
            onFileSelect={(file) => {
              setSelectedFile(file);
              setSelectedResumeId(null);
            }}
            selectedFile={selectedFile}
            onClearFile={() => setSelectedFile(null)}
            uploadProgress={uploadProgress}
            disabled={isProcessing}
          />
        </div>

        {/* Step 2: Job Target Details */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <span className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center">
                2
              </span>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">
                Target Role & Job Description
              </h2>
            </div>

            <button
              type="button"
              onClick={handlePreFillSample}
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center space-x-1"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Fill Sample Job Description</span>
            </button>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
              Target Job Title
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Briefcase className="w-4 h-4" />
              </div>
              <input
                type="text"
                required
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. Senior Backend Engineer"
                disabled={isProcessing}
                className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Job Description
              </label>
              <span className="text-xs text-slate-400">
                {jobDescription.length} characters
              </span>
            </div>
            <textarea
              required
              rows={8}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the full job posting requirements, responsibilities, and qualifications here..."
              disabled={isProcessing}
              className="w-full p-3.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-mono leading-relaxed resize-y"
            />
          </div>
        </div>

        {/* Submit Action */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={isProcessing}
            className="w-full py-3.5 px-6 rounded-xl text-base font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {isProcessing ? (
              <div className="flex items-center space-x-3">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>{statusMessage || 'Analyzing Document...'}</span>
              </div>
            ) : (
              <>
                <span>Run Match Analysis</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
