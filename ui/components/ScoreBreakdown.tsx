"use client";

import { Scores, ScoreBreakdown as ScoreBreakdownType } from "@/lib/types";

interface ScoreBreakdownProps {
  scores: Scores;
  breakdown: ScoreBreakdownType;
}

const dimensions: { key: keyof Omit<Scores, "composite">; label: string }[] = [
  { key: "lab_experience", label: "Lab Experience" },
  { key: "seniority", label: "Seniority" },
  { key: "recency", label: "Recency" },
  { key: "startup_fit", label: "Startup Fit" },
  { key: "education", label: "Education" },
  { key: "company_quality", label: "Company Quality" },
];

function ScoreBar({ score }: { score: number }) {
  const percentage = (score / 10) * 100;

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-black/[0.06] dark:bg-white/[0.06] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${percentage}%`,
            background: score >= 8
              ? "linear-gradient(90deg, rgba(34,197,94,0.8), rgba(34,197,94,1))"
              : score >= 5
              ? "linear-gradient(90deg, rgba(245,158,11,0.8), rgba(245,158,11,1))"
              : "linear-gradient(90deg, rgba(100,116,139,0.6), rgba(100,116,139,0.8))",
          }}
        />
      </div>
      <span className="text-xs font-mono text-text-tertiary w-8 text-right">
        {score}/10
      </span>
    </div>
  );
}

export function ScoreBreakdown({ scores, breakdown }: ScoreBreakdownProps) {
  return (
    <div className="mt-4 pt-4 border-t border-black/[0.06] dark:border-white/[0.06] space-y-3">
      {dimensions.map(({ key, label }) => (
        <div key={key} className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-text-secondary">
              {label}
            </span>
          </div>
          <ScoreBar score={scores[key]} />
          <p className="text-[11px] text-text-tertiary pl-0.5">
            {breakdown[key]}
          </p>
        </div>
      ))}
    </div>
  );
}
