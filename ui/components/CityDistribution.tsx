"use client";

import { City } from "@/lib/types";

interface CityDistributionProps {
  cities: City[];
}

export function CityDistribution({ cities }: CityDistributionProps) {
  const maxCount = Math.max(...cities.map((c) => c.count));

  return (
    <div className="py-8">
      <h3 className="text-sm uppercase tracking-wider text-text-tertiary mb-6 text-center">
        Distribution by City
      </h3>
      <div className="max-w-xl mx-auto space-y-3">
        {cities.map((city) => (
          <div key={city.name} className="flex items-center gap-3">
            <span className="w-24 text-sm text-text-secondary text-right">
              {city.name}
            </span>
            <div className="flex-1 h-6 bg-bg-elevated rounded overflow-hidden">
              <div
                className="h-full bg-accent-india/80 rounded transition-all duration-500"
                style={{ width: `${(city.count / maxCount) * 100}%` }}
              />
            </div>
            <span className="w-10 text-sm font-mono text-text-primary">
              {city.count}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
