"use client";

import { Candidate } from "@/lib/types";
import { CandidateCard } from "./CandidateCard";

interface CandidateFeedProps {
  candidates: Candidate[];
  scanningId?: string | null;
  visibleSignals?: number;
}

export function CandidateFeed({ candidates, scanningId, visibleSignals }: CandidateFeedProps) {
  return (
    <div className="flex flex-col gap-4">
      {candidates.map((candidate) => (
        <div key={candidate.id} id={`candidate-${candidate.id}`}>
          <CandidateCard
            candidate={candidate}
            isScanning={scanningId === candidate.id}
            visibleSignals={scanningId === candidate.id ? visibleSignals : undefined}
          />
        </div>
      ))}
    </div>
  );
}
