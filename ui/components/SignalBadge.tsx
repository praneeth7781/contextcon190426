"use client";

import { Signal } from "@/lib/types";

interface SignalBadgeProps {
  signal: Signal;
}

export function SignalBadge({ signal }: SignalBadgeProps) {
  const typeStyles: Record<string, string> = {
    founder: "bg-accent-green/10 text-accent-green",
    recent_return: "bg-accent-amber/10 text-accent-amber",
    tiny_company: "bg-accent-primary/10 text-accent-primary",
    senior: "bg-purple-500/10 text-purple-400",
    founding_team: "bg-accent-green/10 text-accent-green",
    large_company: "bg-accent-gray/10 text-accent-gray",
  };

  const style = typeStyles[signal.type] || "bg-bg-elevated text-text-secondary";

  return (
    <span className={`px-2 py-0.5 text-xs rounded-md ${style}`}>
      {signal.label}
    </span>
  );
}
