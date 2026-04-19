"use client";

interface CompanyStatsBannerProps {
  totalCompanies: number;
  totalExLabMembers: number;
  companiesWithFounders: number;
  sourceCandidates: number;
}

interface StatCardProps {
  value: number;
  label: string;
  isFirst?: boolean;
}

function StatCard({ value, label, isFirst }: StatCardProps) {
  return (
    <div className="group relative flex flex-col items-center py-6 px-4 transition-all duration-300 ease-out hover:bg-white/[0.02] first:rounded-l-lg last:rounded-r-lg">
      {!isFirst && (
        <div className="absolute left-0 top-1/4 bottom-1/4 w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
      )}

      <span className="text-4xl md:text-5xl font-mono font-medium bg-gradient-to-b from-white via-text-primary to-text-secondary bg-clip-text text-transparent drop-shadow-[0_0_20px_rgba(255,255,255,0.1)] group-hover:drop-shadow-[0_0_30px_rgba(255,255,255,0.15)] transition-all duration-300">
        {value}
      </span>

      <span className="text-[10px] uppercase tracking-[0.2em] text-text-tertiary mt-2 group-hover:text-text-secondary transition-colors duration-300">
        {label}
      </span>
    </div>
  );
}

export function CompanyStatsBanner({
  totalCompanies,
  totalExLabMembers,
  companiesWithFounders,
  sourceCandidates,
}: CompanyStatsBannerProps) {
  const stats = [
    { value: totalCompanies, label: "Companies tracked" },
    { value: totalExLabMembers, label: "Ex-lab members" },
    { value: companiesWithFounders, label: "With lab founders" },
    { value: sourceCandidates, label: "Source candidates" },
  ];

  return (
    <div className="relative rounded-xl overflow-hidden bg-gradient-to-br from-bg-card via-bg-card to-bg-elevated border border-white/[0.06] shadow-[var(--shadow-card)] p-1 mb-4">
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent pointer-events-none" />

      <div className="relative grid grid-cols-2 md:grid-cols-4">
        {stats.map((stat, i) => (
          <StatCard key={i} value={stat.value} label={stat.label} isFirst={i === 0} />
        ))}
      </div>
    </div>
  );
}
