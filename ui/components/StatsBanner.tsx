"use client";

import { Meta } from "@/lib/types";

interface StatsBannerProps {
  meta: Meta;
}

interface StatCardProps {
  value: number;
  label: string;
  isFirst?: boolean;
}

function StatCard({ value, label, isFirst }: StatCardProps) {
  return (
    <div className="group relative flex flex-col items-center py-6 px-4 transition-all duration-300 ease-out hover:bg-black/[0.02] dark:hover:bg-white/[0.02] first:rounded-l-lg last:rounded-r-lg">
      {/* Separator line */}
      {!isFirst && (
        <div className="absolute left-0 top-1/4 bottom-1/4 w-px bg-gradient-to-b from-transparent via-black/10 dark:via-white/10 to-transparent" />
      )}

      {/* Value with gradient */}
      <span className="text-4xl md:text-5xl font-mono font-medium bg-gradient-to-b from-text-primary via-text-primary to-text-secondary bg-clip-text text-transparent drop-shadow-[0_0_20px_rgba(0,0,0,0.05)] dark:drop-shadow-[0_0_20px_rgba(255,255,255,0.1)] group-hover:drop-shadow-[0_0_30px_rgba(0,0,0,0.08)] dark:group-hover:drop-shadow-[0_0_30px_rgba(255,255,255,0.15)] transition-all duration-300">
        {value}
      </span>

      {/* Label */}
      <span className="text-[10px] uppercase tracking-[0.2em] text-text-tertiary mt-2 group-hover:text-text-secondary transition-colors duration-300">
        {label}
      </span>
    </div>
  );
}

export function StatsBanner({ meta }: StatsBannerProps) {
  const stats = [
    { value: meta.total_candidates, label: "Alumni in India" },
    { value: meta.returned_last_12_months, label: "Returned in 12mo" },
    { value: meta.at_sub_50_startups, label: "At sub-50 startups" },
    { value: meta.founders_or_cofounders, label: "Founders/Co-founders" },
  ];

  return (
    <div className="relative rounded-xl overflow-hidden bg-gradient-to-br from-bg-card via-bg-card to-bg-elevated border border-black/[0.06] dark:border-white/[0.06] shadow-[var(--shadow-card)] p-1">
      {/* Subtle inner glow */}
      <div className="absolute inset-0 bg-gradient-to-br from-black/[0.01] dark:from-white/[0.02] to-transparent pointer-events-none" />

      <div className="relative grid grid-cols-2 md:grid-cols-4">
        {stats.map((stat, i) => (
          <StatCard key={i} value={stat.value} label={stat.label} isFirst={i === 0} />
        ))}
      </div>
    </div>
  );
}
