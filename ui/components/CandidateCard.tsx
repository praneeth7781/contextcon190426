"use client";

import { Candidate } from "@/lib/types";
import { getLabColor, getInitials, hashStringToColor, formatDaysAgo } from "@/lib/format";
import { ScoreBadge } from "./ScoreBadge";
import { SignalBadge } from "./SignalBadge";

interface CandidateCardProps {
  candidate: Candidate;
  isScanning?: boolean;
  visibleSignals?: number;
}

export function CandidateCard({ candidate, isScanning, visibleSignals }: CandidateCardProps) {
  const signals = candidate.signals || [];
  const displaySignals = isScanning && visibleSignals !== undefined
    ? signals.slice(0, visibleSignals)
    : signals.slice(0, 4);
  const remainingCount = signals.length - 4;

  return (
    <div
      className="bg-bg-card border border-border-subtle rounded-lg p-6 hover:border-border-visible transition-colors"
    >
      <div className="flex gap-4">
        {/* Photo */}
        <div className="flex-shrink-0">
          {candidate.photo_url ? (
            <img
              src={candidate.photo_url}
              alt={candidate.name}
              className="w-16 h-16 rounded-full object-cover"
            />
          ) : (
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center text-lg font-semibold text-white"
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
            <ScoreBadge score={candidate.score} tier={candidate.score_tier} />
          </div>

          {/* Employment arc */}
          <div className="mt-3 text-sm">
            <span>
              ex-
              <span style={{ color: getLabColor(candidate.former_lab) }}>
                {candidate.former_lab}
              </span>
              {candidate.former_title && ` ${candidate.former_title}`}
              {candidate.former_tenure_years && (
                <span className="text-text-tertiary">
                  {" "}({candidate.former_tenure_years}y)
                </span>
              )}
            </span>
          </div>

          {/* Current role */}
          {candidate.current_role && (
            <div className="mt-1 text-sm flex items-center gap-1">
              <span className="text-accent-india">&rarr;</span>
              <span className="text-text-primary">
                {candidate.current_role}
                {candidate.current_company && ` at ${candidate.current_company}`}
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
            {candidate.days_since_return !== undefined && (
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
            <p className="mt-3 text-sm text-text-secondary leading-relaxed line-clamp-3">
              {candidate.synthesis}
            </p>
          )}

          {/* LinkedIn link */}
          {candidate.linkedin_url && (
            <div className="mt-4 flex justify-end">
              <a
                href={candidate.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-accent-primary hover:underline"
              >
                View profile &rarr;
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
