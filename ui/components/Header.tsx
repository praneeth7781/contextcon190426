"use client";

import { relativeTime } from "@/lib/format";

interface HeaderProps {
  lastUpdated: string;
}

export function Header({ lastUpdated }: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 bg-bg-primary border-b border-white/5">
      <div className="max-w-[1400px] mx-auto h-full px-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent-india" />
          <span className="font-semibold text-lg text-text-primary">
            Homecoming
          </span>
        </div>

        <span className="text-sm text-text-tertiary hidden sm:block">
          AI talent returning home — tracked live
        </span>

        <span className="text-xs text-text-tertiary font-mono">
          Updated {relativeTime(lastUpdated)}
        </span>
      </div>
    </header>
  );
}
