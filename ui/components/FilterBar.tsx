"use client";

export type FilterType = "all" | "founders" | "recent" | "stealth";
export type SortType = "score" | "return_date" | "lab" | "seniority";

interface FilterBarProps {
  activeFilter: FilterType;
  activeSort: SortType;
  onFilterChange: (filter: FilterType) => void;
  onSortChange: (sort: SortType) => void;
}

const filters: { value: FilterType; label: string }[] = [
  { value: "all", label: "All" },
  { value: "founders", label: "Founders" },
];

const sorts: { value: SortType; label: string }[] = [
  { value: "score", label: "Score" },
  { value: "return_date", label: "Return date" },
  // { value: "lab", label: "Former lab" },
  // { value: "seniority", label: "Seniority" },
];

export function FilterBar({
  activeFilter,
  activeSort,
  onFilterChange,
  onSortChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 py-4">
      <div className="flex flex-wrap gap-0.5 bg-gradient-to-br from-bg-card to-bg-primary rounded-xl p-1 border border-black/[0.04] dark:border-white/[0.04] shadow-[inset_0_1px_0_0_rgba(0,0,0,0.02)] dark:shadow-[inset_0_1px_0_0_rgba(255,255,255,0.02)]">
        {filters.map((filter) => (
          <button
            key={filter.value}
            onClick={() => onFilterChange(filter.value)}
            className={`relative px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
              activeFilter === filter.value
                ? "bg-gradient-to-br from-bg-elevated to-bg-card text-text-primary shadow-[0_2px_8px_rgba(0,0,0,0.1)] dark:shadow-[0_2px_8px_rgba(0,0,0,0.2),inset_0_1px_0_0_rgba(255,255,255,0.04)] border border-black/[0.06] dark:border-white/[0.06]"
                : "text-text-secondary hover:text-text-primary hover:bg-black/[0.02] dark:hover:bg-white/[0.02]"
            }`}
          >
            {activeFilter === filter.value && (
              <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-accent-india" />
            )}
            {filter.label}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-3">
        <span className="text-xs text-text-tertiary font-medium">Sort by</span>
        <select
          value={activeSort}
          onChange={(e) => onSortChange(e.target.value as SortType)}
          className="appearance-none cursor-pointer bg-gradient-to-br from-bg-card to-bg-primary border border-black/[0.06] dark:border-white/[0.06] rounded-lg px-4 py-2 pr-8 text-sm text-text-primary font-medium shadow-[0_2px_8px_rgba(0,0,0,0.08)] dark:shadow-[0_2px_8px_rgba(0,0,0,0.15)] focus:outline-none focus:ring-2 focus:ring-accent-primary/30 focus:border-accent-primary/50 hover:border-black/[0.1] dark:hover:border-white/[0.1] transition-all duration-200"
        >
          {sorts.map((sort) => (
            <option key={sort.value} value={sort.value}>
              {sort.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
