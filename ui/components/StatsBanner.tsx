"use client";

import { Meta } from "@/lib/types";

interface StatsBannerProps {
  meta: Meta;
}

interface StatCardProps {
  value: number;
  label: string;
}

function StatCard({ value, label }: StatCardProps) {
  return (
    <div className="flex flex-col items-center py-4">
      <span className="text-4xl md:text-5xl font-mono text-text-primary">
        {value}
      </span>
      <span className="text-xs uppercase tracking-wider text-text-tertiary mt-1">
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
    <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-border-subtle">
      {stats.map((stat, i) => (
        <StatCard key={i} value={stat.value} label={stat.label} />
      ))}
    </div>
  );
}
