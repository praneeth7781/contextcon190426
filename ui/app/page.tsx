"use client";

import { useEffect, useState, useMemo, useCallback } from "react";
import { CandidatesData } from "@/lib/types";
import { Header } from "@/components/Header";
import { StatsBanner } from "@/components/StatsBanner";
import { CityDistribution } from "@/components/CityDistribution";
import { FilterBar, FilterType, SortType } from "@/components/FilterBar";
import { CandidateFeed } from "@/components/CandidateFeed";
import { ScanFreshButton } from "@/components/ScanFreshButton";
import { Footer } from "@/components/Footer";

export default function Home() {
  const [data, setData] = useState<CandidatesData | null>(null);
  const [filter, setFilter] = useState<FilterType>("all");
  const [sort, setSort] = useState<SortType>("score");
  const [scanningId, setScanningId] = useState<string | null>(null);
  const [visibleSignals, setVisibleSignals] = useState(0);

  useEffect(() => {
    fetch("/data/candidates.json")
      .then((res) => res.json())
      .then(setData);
  }, []);

  const filteredCandidates = useMemo(() => {
    if (!data) return [];

    let candidates = [...data.candidates];

    switch (filter) {
      case "founders":
        candidates = candidates.filter((c) =>
          c.signals?.some((s) => s.type === "founder" || s.type === "founding_team")
        );
        break;
      case "recent":
        candidates = candidates.filter(
          (c) => c.days_since_return !== undefined && c.days_since_return < 180
        );
        break;
      case "stealth":
        candidates = candidates.filter(
          (c) =>
            c.current_company?.toLowerCase().includes("stealth") ||
            (c.current_company_headcount !== undefined && c.current_company_headcount < 20)
        );
        break;
    }

    switch (sort) {
      case "score":
        candidates.sort((a, b) => b.score - a.score);
        break;
      case "return_date":
        candidates.sort(
          (a, b) => (a.days_since_return ?? 999) - (b.days_since_return ?? 999)
        );
        break;
      case "lab":
        candidates.sort((a, b) => a.former_lab.localeCompare(b.former_lab));
        break;
      case "seniority":
        const seniorityRank = (title: string | undefined) => {
          if (!title) return 0;
          const t = title.toLowerCase();
          if (t.includes("staff") || t.includes("principal") || t.includes("chief")) return 3;
          if (t.includes("senior")) return 2;
          return 1;
        };
        candidates.sort(
          (a, b) => seniorityRank(b.former_title) - seniorityRank(a.former_title)
        );
        break;
    }

    return candidates;
  }, [data, filter, sort]);

  const handleScanFresh = useCallback(() => {
    if (!data || scanningId) return;

    const candidate = data.candidates[0];
    setScanningId(candidate.id);
    setVisibleSignals(0);

    const el = document.getElementById(`candidate-${candidate.id}`);
    el?.scrollIntoView({ behavior: "smooth", block: "center" });

    const signalCount = candidate.signals?.length || 0;
    let current = 0;

    const interval = setInterval(() => {
      current++;
      setVisibleSignals(current);
      if (current >= signalCount) {
        clearInterval(interval);
        setTimeout(() => {
          setScanningId(null);
          setVisibleSignals(0);
        }, 500);
      }
    }, 300);
  }, [data, scanningId]);

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <span className="text-text-tertiary">Loading...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      <Header lastUpdated={data.meta.last_updated} />

      <main className="max-w-[1400px] mx-auto px-6 pt-20">
        <StatsBanner meta={data.meta} />

        <CityDistribution cities={data.meta.cities} />

        <FilterBar
          activeFilter={filter}
          activeSort={sort}
          onFilterChange={setFilter}
          onSortChange={setSort}
        />

        <CandidateFeed
          candidates={filteredCandidates}
          scanningId={scanningId}
          visibleSignals={visibleSignals}
        />

        <Footer />
      </main>

      <ScanFreshButton onClick={handleScanFresh} isScanning={!!scanningId} />
    </div>
  );
}
