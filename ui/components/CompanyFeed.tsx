"use client";

import { Company } from "@/lib/types";
import { CompanyCard } from "./CompanyCard";

interface CompanyFeedProps {
  companies: Company[];
}

export function CompanyFeed({ companies }: CompanyFeedProps) {
  return (
    <div className="flex flex-col gap-4">
      {companies.map((company) => (
        <div key={company.id} id={`company-${company.id}`}>
          <CompanyCard company={company} />
        </div>
      ))}
    </div>
  );
}
