"use client";

import { Signal } from "@/lib/types";

interface SignalBadgeProps {
  signal: Signal;
}

export function SignalBadge({ signal }: SignalBadgeProps) {
  const typeStyles: Record<string, { bg: string; text: string; glow: string }> = {
    founder: {
      bg: "bg-accent-green/10 hover:bg-accent-green/15",
      text: "text-accent-green",
      glow: "shadow-[0_0_12px_rgba(34,197,94,0.2)]"
    },
    recent_return: {
      bg: "bg-accent-amber/10 hover:bg-accent-amber/15",
      text: "text-accent-amber",
      glow: "shadow-[0_0_12px_rgba(245,158,11,0.2)]"
    },
    tiny_company: {
      bg: "bg-accent-primary/10 hover:bg-accent-primary/15",
      text: "text-accent-primary",
      glow: "shadow-[0_0_12px_rgba(59,130,246,0.2)]"
    },
    senior: {
      bg: "bg-purple-500/10 hover:bg-purple-500/15",
      text: "text-purple-400",
      glow: "shadow-[0_0_12px_rgba(168,85,247,0.2)]"
    },
    founding_team: {
      bg: "bg-accent-green/10 hover:bg-accent-green/15",
      text: "text-accent-green",
      glow: "shadow-[0_0_12px_rgba(34,197,94,0.2)]"
    },
    large_company: {
      bg: "bg-accent-gray/10 hover:bg-accent-gray/15",
      text: "text-accent-gray",
      glow: "shadow-[0_0_12px_rgba(100,116,139,0.15)]"
    },
  };

  const style = typeStyles[signal.type] || {
    bg: "bg-bg-elevated hover:bg-bg-elevated/80",
    text: "text-text-secondary",
    glow: ""
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border border-current/20 transition-all duration-200 hover:scale-[1.02] ${style.bg} ${style.text} ${style.glow}`}>
      {signal.label}
    </span>
  );
}
