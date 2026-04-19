"use client";

import { useState } from "react";
import { Candidate } from "@/lib/types";
import { getLabColor, getInitials, hashStringToColor, formatDaysAgo } from "@/lib/format";
import { ScoreBadge } from "./ScoreBadge";
import { SignalBadge } from "./SignalBadge";
import { ScoreBreakdown } from "./ScoreBreakdown";

interface CandidateCardProps {
  candidate: Candidate;
  isScanning?: boolean;
  visibleSignals?: number;
}

export function CandidateCard({ candidate, isScanning, visibleSignals }: CandidateCardProps) {
  const [expanded, setExpanded] = useState(false);
  const signals = candidate.signals || [];
  const displaySignals = isScanning && visibleSignals !== undefined
    ? signals.slice(0, visibleSignals)
    : signals.slice(0, 4);
  const remainingCount = signals.length - 4;
  const hasScoreDetails = candidate.scores && candidate.score_breakdown;

  return (
    <div
      className="group relative bg-gradient-to-br from-bg-card via-bg-card to-bg-primary border border-black/[0.06] dark:border-white/[0.06] rounded-xl overflow-hidden shadow-[var(--shadow-card)] transition-all duration-300 ease-out hover:border-black/[0.1] dark:hover:border-white/[0.1] hover:shadow-[var(--shadow-card-hover)] hover:-translate-y-0.5"
    >
      {/* Top accent line */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-black/10 dark:via-white/10 to-transparent group-hover:via-black/20 dark:group-hover:via-white/20 transition-opacity duration-300" />

      {/* Inner glow on hover */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-br from-black/[0.01] dark:from-white/[0.02] via-transparent to-transparent pointer-events-none" />

      <div className="relative p-6">
        <div className="flex gap-4">
          {/* Photo */}
          <div className="relative flex-shrink-0">
            <div className="absolute -inset-1 rounded-full bg-gradient-to-br from-black/10 dark:from-white/10 to-transparent opacity-0 group-hover:opacity-100 blur transition-opacity duration-300" />
            {candidate.photo_url ? (
              <img
                src={candidate.photo_url}
                alt={candidate.name}
                className="relative w-16 h-16 rounded-full object-cover ring-2 ring-black/[0.06] dark:ring-white/[0.06] ring-offset-2 ring-offset-bg-card group-hover:ring-black/[0.12] dark:group-hover:ring-white/[0.12] transition-all duration-300"
              />
            ) : (
              <div
                className="relative w-16 h-16 rounded-full flex items-center justify-center text-lg font-semibold text-white ring-2 ring-black/[0.06] dark:ring-white/[0.06] ring-offset-2 ring-offset-bg-card group-hover:ring-black/[0.12] dark:group-hover:ring-white/[0.12] transition-all duration-300"
                style={{ backgroundColor: hashStringToColor(candidate.name) }}
              >
                {getInitials(candidate.name)}
              </div>
            )}
          </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Header row */}
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-xl font-semibold text-text-primary">
                {candidate.name}
              </h3>
              {candidate.headline && (
                <p className="text-sm text-text-secondary mt-0.5">
                  &ldquo;{candidate.headline}&rdquo;
                </p>
              )}
            </div>
            {hasScoreDetails ? (
                  <button
                    onClick={() => setExpanded(!expanded)}
                    className="flex items-center gap-1.5 group/score cursor-pointer"
                    aria-expanded={expanded}
                  >
                    <ScoreBadge score={candidate.score} tier={candidate.score_tier} />
                    <span
                      className={`text-text-tertiary transition-transform duration-200 ${
                        expanded ? "rotate-180" : ""
                      }`}
                    >
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </span>
                  </button>
                ) : (
                  <ScoreBadge score={candidate.score} tier={candidate.score_tier} />
                )}
          </div>

          {/* Employment arc */}
          <div className="mt-3 text-sm flex items-center gap-2 flex-wrap">
            <span className="text-text-tertiary">ex-</span>
            <span
              className="px-2 py-0.5 rounded-md text-xs font-medium border"
              style={{
                color: getLabColor(candidate.former_lab),
                backgroundColor: `${getLabColor(candidate.former_lab)}15`,
                borderColor: `${getLabColor(candidate.former_lab)}30`
              }}
            >
              {candidate.former_lab}
            </span>
            {candidate.former_title && (
              <span className="text-text-secondary">{candidate.former_title}</span>
            )}
            {candidate.former_tenure_years && (
              <span className="text-text-tertiary">({candidate.former_tenure_years}y)</span>
            )}
          </div>

          {/* Current role */}
          {candidate.current_role && (
            <div className="mt-1 text-sm flex items-center gap-2">
              <span className="text-accent-india transition-transform duration-300 group-hover:translate-x-0.5">&rarr;</span>
              <span className="text-text-primary">
                {candidate.current_role}
                {candidate.current_company && <span className="text-text-secondary"> at {candidate.current_company}</span>}
              </span>
            </div>
          )}

          {/* Meta line */}
          <div className="mt-2 text-xs font-mono text-text-tertiary flex flex-wrap gap-x-2">
            {candidate.current_city && <span>{candidate.current_city}</span>}
            {candidate.current_company_headcount && (
              <>
                <span>·</span>
                <span>{candidate.current_company_headcount} people</span>
              </>
            )}
            {candidate.days_since_return != null && (
              <>
                <span>·</span>
                <span>returned {formatDaysAgo(candidate.days_since_return)}</span>
              </>
            )}
          </div>

          {/* Signals */}
          {displaySignals.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {displaySignals.map((signal, i) => (
                <SignalBadge key={i} signal={signal} />
              ))}
              {remainingCount > 0 && !isScanning && (
                <span className="px-2 py-0.5 text-xs text-text-tertiary">
                  +{remainingCount} more
                </span>
              )}
            </div>
          )}

          {/* Synthesis */}
          {candidate.synthesis && (
            <p className="mt-3 text-sm text-text-secondary leading-relaxed">
              {candidate.synthesis}
            </p>
          )}

          {/* Score Breakdown */}
          {expanded && hasScoreDetails && (
            <ScoreBreakdown
              scores={candidate.scores!}
              breakdown={candidate.score_breakdown!}
            />
          )}

          {/* LinkedIn link */}
          {candidate.linkedin_url && (
            <div className="mt-4 flex justify-end">
              <a
                href={candidate.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="group/link inline-flex items-center gap-1 text-sm text-text-tertiary px-3 py-1.5 rounded-lg bg-black/[0.02] dark:bg-white/[0.02] border border-black/[0.04] dark:border-white/[0.04] hover:bg-black/[0.04] dark:hover:bg-white/[0.04] hover:border-black/[0.08] dark:hover:border-white/[0.08] hover:text-accent-primary transition-all duration-200"
              >
                <span>View profile</span>
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
