export interface Signal {
  type: string;
  label: string;
}

export interface Candidate {
  id: string;
  name: string;
  photo_url?: string;
  headline?: string;
  score: number;
  score_tier: "HIGH" | "MED" | "LOW";
  former_lab: string;
  former_title?: string;
  former_tenure_years?: number;
  former_end_date?: string;
  current_role?: string;
  current_company?: string;
  current_company_headcount?: number;
  current_company_website?: string;
  current_city?: string;
  current_start_date?: string;
  days_since_return?: number;
  signals?: Signal[];
  synthesis?: string;
  linkedin_url?: string;
}

export interface City {
  name: string;
  lat: number;
  lng: number;
  count: number;
}

export interface Meta {
  total_candidates: number;
  returned_last_12_months: number;
  at_sub_50_startups: number;
  founders_or_cofounders: number;
  last_updated: string;
  cities: City[];
}

export interface CandidatesData {
  meta: Meta;
  candidates: Candidate[];
}

export interface TeamHighlight {
  name: string;
  title: string;
  former_lab: string;
}

export interface Company {
  id: string;
  name: string;
  score: number;
  score_tier: "HIGH" | "MED" | "LOW";
  headcount: number | null;
  ex_lab_count: number;
  avg_seniority: number;
  has_founder_from_lab: boolean;
  funding_total: number | null;
  last_round: string | null;
  team_highlights: TeamHighlight[];
  linkedin_url?: string;
}

export interface CompaniesMeta {
  total_companies: number;
  last_updated: string;
  source_candidates: number;
}

export interface CompaniesData {
  meta: CompaniesMeta;
  companies: Company[];
}
