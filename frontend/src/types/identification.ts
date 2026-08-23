export type IdentificationStatus = "matched" | "partial" | "unsupported";

export interface IdentificationCandidate {
  artifact_id: number;
  artifact_name: string;
  confidence: number;
}

export interface IdentificationResponse {
  status: IdentificationStatus;
  artifact_id: number | null;
  artifact_name: string | null;
  confidence: number;
  reason: string;
  alternatives: IdentificationCandidate[];
}
