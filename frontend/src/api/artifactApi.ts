import { request } from "./apiClient";
import type { ArtifactDetail, ArtifactSummary } from "../types/artifact";

export function fetchArtifacts(lang: string): Promise<ArtifactSummary[]> {
  return request<ArtifactSummary[]>(`/artifacts?lang=${encodeURIComponent(lang)}`);
}

export function fetchArtifact(id: string | number, lang: string): Promise<ArtifactDetail> {
  return request<ArtifactDetail>(`/artifacts/${id}?lang=${encodeURIComponent(lang)}`);
}
