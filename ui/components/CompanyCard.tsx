"use client";

import { Company } from "@/lib/types";
import { getLabColor, getInitials, hashStringToColor } from "@/lib/format";
import { ScoreBadge } from "./ScoreBadge";

interface CompanyCardProps {
  company: Company;
}

export function CompanyCard({ company }: CompanyCardProps) {
  return (
    <div className="group relative bg-gradient-to-br from-bg-card via-bg-card to-bg-primary border border-black/[0.06] dark:border-white/[0.06] rounded-xl overflow-hidden shadow-[var(--shadow-card)] transition-all duration-300 ease-out hover:border-black/[0.1] dark:hover:border-white/[0.1] hover:shadow-[var(--shadow-card-hover)] hover:-translate-y-0.5">
      {/* Top accent line */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-black/10 dark:via-white/10 to-transparent group-hover:via-black/20 dark:group-hover:via-white/20 transition-opacity duration-300" />

      {/* Inner glow on hover */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-br from-black/[0.01] dark:from-white/[0.02] via-transparent to-transparent pointer-events-none" />

      <div className="relative p-6">
        <div className="flex gap-4">
          <div className="relative flex-shrink-0">
            <div className="absolute -inset-1 rounded-lg bg-gradient-to-br from-black/10 dark:from-white/10 to-transparent opacity-0 group-hover:opacity-100 blur transition-opacity duration-300" />
            <div
              className="relative w-16 h-16 rounded-lg flex items-center justify-center text-lg font-semibold text-white ring-2 ring-black/[0.06] dark:ring-white/[0.06] group-hover:ring-black/[0.12] dark:group-hover:ring-white/[0.12] transition-all duration-300"
              style={{ backgroundColor: hashStringToColor(company.name) }}
            >
              {getInitials(company.name)}
            </div>
          </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4">
            <h3 className="text-xl font-semibold text-text-primary">
              {company.name}
            </h3>
            <ScoreBadge score={company.score} tier={company.score_tier} />
          </div>

          <div className="mt-3 flex flex-wrap gap-4 text-sm">
            {company.headcount && (
              <span className="text-text-secondary">
                {company.headcount} employees
              </span>
            )}
            <span className="text-accent-india">
              {company.ex_lab_count} ex-lab members
            </span>
            {company.has_founder_from_lab && (
              <span className="text-accent-green">Lab founder</span>
            )}
          </div>

          {company.funding_total && (
            <div className="mt-2 text-xs font-mono text-text-tertiary">
              ${(company.funding_total / 1_000_000).toFixed(1)}M raised
              {company.last_round && ` · ${company.last_round}`}
            </div>
          )}

          {company.team_highlights.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {company.team_highlights.slice(0, 3).map((member, i) => (
                <span
                  key={i}
                  className="inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full bg-bg-elevated/80 text-text-secondary border border-black/[0.04] dark:border-white/[0.04] transition-all duration-200 hover:bg-bg-elevated"
                >
                  {member.name} · ex-
                  <span className="ml-0.5" style={{ color: getLabColor(member.former_lab) }}>
                    {member.former_lab}
                  </span>
                </span>
              ))}
              {company.team_highlights.length > 3 && (
                <span className="px-2.5 py-1 text-xs text-text-tertiary">
                  +{company.team_highlights.length - 3} more
                </span>
              )}
            </div>
          )}

          {company.linkedin_url && (
            <div className="mt-4 flex justify-end">
              <a
                href={company.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="group/link inline-flex items-center gap-1 text-sm text-text-tertiary px-3 py-1.5 rounded-lg bg-black/[0.02] dark:bg-white/[0.02] border border-black/[0.04] dark:border-white/[0.04] hover:bg-black/[0.04] dark:hover:bg-white/[0.04] hover:border-black/[0.08] dark:hover:border-white/[0.08] hover:text-accent-primary transition-all duration-200"
              >
                <span>View company</span>
                <span className="transition-transform duration-200 group-hover/link:translate-x-0.5">&rarr;</span>
              </a>
            </div>
          )}
          </div>
        </div>
      </div>
    </div>
  );
}
