import type { ArtifactDetail, ArtifactSummary } from "../types/artifact";

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new ApiError(0, "Could not reach the Ruwi server. Is the backend running?");
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // response had no JSON body — fall back to statusText
    }
    throw new ApiError(response.status, detail);
  }

  return (await response.json()) as T;
}

export function resolveImageUrl(imageUrl: string): string {
  return `${API_BASE_URL}${imageUrl}`;
}

export function fetchArtifacts(): Promise<ArtifactSummary[]> {
  return request<ArtifactSummary[]>("/artifacts");
}

export function fetchArtifact(id: string | number): Promise<ArtifactDetail> {
  return request<ArtifactDetail>(`/artifacts/${id}`);
}

export function askRuwi(artifactId: number, question: string): Promise<{ answer: string }> {
  return request<{ answer: string }>("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ artifact_id: artifactId, question }),
  });
}
