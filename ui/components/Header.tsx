"use client";

import { relativeTime } from "@/lib/format";
import { ThemeToggle } from "./ThemeToggle";

interface HeaderProps {
  lastUpdated: string;
}

export function Header({ lastUpdated }: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 bg-gradient-to-b from-bg-primary/95 to-bg-primary/85 backdrop-blur-xl border-b border-black/[0.06] dark:border-white/[0.06] shadow-[0_1px_0_0_rgba(0,0,0,0.03)] dark:shadow-[0_1px_0_0_rgba(255,255,255,0.03)]">
      <div className="max-w-[1400px] mx-auto h-full px-6 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span className="relative flex items-center justify-center">
            <span className="absolute w-2.5 h-2.5 rounded-full bg-accent-india blur-sm opacity-60 animate-pulse-glow" />
            <span className="relative w-2.5 h-2.5 rounded-full bg-gradient-to-br from-accent-india to-orange-600" />
          </span>
          <span className="font-semibold text-lg bg-gradient-to-r from-text-primary to-text-secondary bg-clip-text text-transparent">
            Homecoming
          </span>
        </div>

        <span className="text-sm text-text-tertiary hidden sm:block">
          AI talent returning home — tracked live
        </span>

        <div className="flex items-center gap-3">
          <span className="text-xs text-text-tertiary font-mono px-2.5 py-1 rounded-full bg-black/[0.03] dark:bg-white/[0.03] border border-black/[0.04] dark:border-white/[0.04]">
            Updated {relativeTime(lastUpdated)}
          </span>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
