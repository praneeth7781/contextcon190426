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
  { value: "recent", label: "Returned recently" },
  { value: "stealth", label: "At stealth startups" },
];

const sorts: { value: SortType; label: string }[] = [
  { value: "score", label: "Score" },
  { value: "return_date", label: "Return date" },
  { value: "lab", label: "Former lab" },
  { value: "seniority", label: "Seniority" },
];

export function FilterBar({
  activeFilter,
  activeSort,
  onFilterChange,
  onSortChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 py-4">
      <div className="flex flex-wrap gap-1 bg-bg-card rounded-lg p-1">
        {filters.map((filter) => (
          <button
            key={filter.value}
            onClick={() => onFilterChange(filter.value)}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              activeFilter === filter.value
                ? "bg-bg-elevated text-text-primary"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-2">
        <span className="text-xs text-text-tertiary">Sort by</span>
        <select
          value={activeSort}
          onChange={(e) => onSortChange(e.target.value as SortType)}
          className="bg-bg-card border border-border-subtle rounded-md px-3 py-1.5 text-sm text-text-primary focus:outline-none focus:border-border-visible"
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
