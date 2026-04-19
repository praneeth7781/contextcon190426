"use client";

export type TabType = "candidates" | "companies";

interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

const tabs: { value: TabType; label: string }[] = [
  { value: "candidates", label: "Candidates" },
  { value: "companies", label: "Companies" },
];

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  return (
    <div className="relative flex gap-0.5 bg-gradient-to-br from-bg-card to-bg-primary rounded-xl p-1 border border-black/[0.04] dark:border-white/[0.04] mb-4">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          onClick={() => onTabChange(tab.value)}
          className={`relative z-10 px-5 py-2.5 text-sm font-medium rounded-lg transition-all duration-300 ease-out ${
            activeTab === tab.value
              ? "text-text-primary"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          {activeTab === tab.value && (
            <span className="absolute inset-0 rounded-lg bg-gradient-to-br from-bg-elevated to-bg-card border border-black/[0.06] dark:border-white/[0.06] shadow-[0_2px_8px_rgba(0,0,0,0.1)] dark:shadow-[0_2px_8px_rgba(0,0,0,0.2),inset_0_1px_0_0_rgba(255,255,255,0.03)] animate-scale-in" />
          )}
          <span className="relative">{tab.label}</span>
        </button>
      ))}
    </div>
  );
}
