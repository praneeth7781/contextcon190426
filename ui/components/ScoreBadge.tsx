"use client";

interface ScoreBadgeProps {
  score: number;
  tier: "HIGH" | "MED" | "LOW";
}

export function ScoreBadge({ score, tier }: ScoreBadgeProps) {
  const tierColors = {
    HIGH: "text-accent-green",
    MED: "text-accent-amber",
    LOW: "text-accent-gray",
  };

  return (
    <div className="flex items-baseline gap-1.5">
      <span className="text-2xl font-mono text-text-primary">
        {score.toFixed(1)}
      </span>
      <span
        className={`text-xs uppercase tracking-wider font-medium ${tierColors[tier]}`}
      >
        {tier}
      </span>
    </div>
  );
}
