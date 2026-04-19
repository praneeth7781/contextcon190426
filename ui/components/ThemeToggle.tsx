"use client";

import { useTheme } from "@/lib/theme-context";

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();

  const cycleTheme = () => {
    const order: Array<"light" | "dark" | "system"> = ["light", "dark", "system"];
    const currentIndex = order.indexOf(theme);
    const nextIndex = (currentIndex + 1) % order.length;
    setTheme(order[nextIndex]);
  };

  return (
    <button
      onClick={cycleTheme}
      className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-black/[0.03] dark:bg-white/[0.03] border border-black/[0.06] dark:border-white/[0.06] hover:bg-black/[0.06] dark:hover:bg-white/[0.06] transition-all duration-200"
      aria-label={`Current theme: ${theme}. Click to change.`}
    >
      {/* Sun icon (light mode) */}
      <svg
        className={`absolute w-4 h-4 text-text-primary transition-all duration-300 ${
          resolvedTheme === "light"
            ? "opacity-100 rotate-0 scale-100"
            : "opacity-0 -rotate-90 scale-75"
        }`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
      </svg>

      {/* Moon icon (dark mode) */}
      <svg
        className={`absolute w-4 h-4 text-text-primary transition-all duration-300 ${
          resolvedTheme === "dark"
            ? "opacity-100 rotate-0 scale-100"
            : "opacity-0 rotate-90 scale-75"
        }`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
      </svg>

      {/* System indicator dot */}
      {theme === "system" && (
        <span className="absolute bottom-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-accent-india" />
      )}
    </button>
  );
}
