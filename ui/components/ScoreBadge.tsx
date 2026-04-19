"use client";

interface ScoreBadgeProps {
  score: number;
  tier: "HIGH" | "MED" | "LOW";
}

export function ScoreBadge({ score, tier }: ScoreBadgeProps) {
  const tierConfig: Record<string, { color: string; glow: string; bg: string }> = {
    HIGH: {
      color: "text-accent-green",
      glow: "drop-shadow-[0_0_8px_rgba(34,197,94,0.4)]",
      bg: "from-accent-green/10 to-transparent"
    },
    MED: {
      color: "text-accent-amber",
      glow: "drop-shadow-[0_0_8px_rgba(245,158,11,0.4)]",
      bg: "from-accent-amber/10 to-transparent"
    },
    LOW: {
      color: "text-accent-gray",
      glow: "drop-shadow-[0_0_8px_rgba(100,116,139,0.3)]",
      bg: "from-accent-gray/10 to-transparent"
    },
  };

  const config = tierConfig[tier];

  return (
    <div className={`flex items-baseline gap-2 px-3 py-2 rounded-xl bg-gradient-to-br ${config.bg} border border-black/[0.04] dark:border-white/[0.04]`}>
      <span className="text-2xl font-mono font-semibold text-text-primary tracking-tight">
        {score.toFixed(1)}
      </span>
      <span className={`text-[10px] uppercase tracking-[0.15em] font-bold ${config.color} ${config.glow}`}>
        {tier}
      </span>
    </div>
  );
}
