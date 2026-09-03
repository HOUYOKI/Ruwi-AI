import type { ExperienceResponse } from "../types/experience";
import type { IdentificationResponse } from "../types/identification";
import i18next from "../i18n";

// In production the FastAPI service hosts the built frontend as well, so API
// requests stay on the current origin. Local Vite development can still point
// at the backend explicitly with VITE_API_BASE_URL=http://localhost:8000.
const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new ApiError(0, i18next.t("api.serverUnreachable"));
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

export function fetchArtifactExperience(id: string | number, lang: string): Promise<ExperienceResponse> {
  return request<ExperienceResponse>(`/artifacts/${id}/experience?lang=${encodeURIComponent(lang)}`);
}

export function identifyArtifact(file: File): Promise<IdentificationResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return request<IdentificationResponse>("/identify", {
    method: "POST",
    body: formData,
  });
}

export function resolveAudioUrl(audioUrl: string): string {
  return `${API_BASE_URL}${audioUrl}`;
}
