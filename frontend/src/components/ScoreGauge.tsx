import React from 'react';

interface ScoreGaugeProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  size = 140,
  strokeWidth = 12,
  label = "Overall Match"
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const safeScore = Math.max(0, Math.min(100, score));
  const offset = circumference - (safeScore / 100) * circumference;

  let strokeColor = '#ef4444'; // Red
  let statusText = 'Low Match';
  let badgeBg = 'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400';

  if (safeScore >= 75) {
    strokeColor = '#10b981'; // Green
    statusText = 'Strong Match';
    badgeBg = 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400';
  } else if (safeScore >= 50) {
    strokeColor = '#f59e0b'; // Amber
    statusText = 'Moderate Alignment';
    badgeBg = 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400';
  }

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        <svg className="w-full h-full transform -rotate-90" viewBox={`0 0 ${size} ${size}`}>
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-slate-200 dark:text-slate-700"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-3xl font-extrabold text-slate-900 dark:text-white">
            {Math.round(safeScore)}%
          </span>
        </div>
      </div>
      <div className="mt-3 text-center">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {label}
        </p>
        <span className={`inline-block mt-1 px-2.5 py-0.5 text-xs font-semibold rounded-full ${badgeBg}`}>
          {statusText}
        </span>
      </div>
    </div>
  );
};
