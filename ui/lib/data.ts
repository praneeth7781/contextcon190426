import { CandidatesData } from "./types";

export async function loadCandidates(): Promise<CandidatesData> {
  const res = await fetch("/data/candidates.json");
  return res.json();
}
