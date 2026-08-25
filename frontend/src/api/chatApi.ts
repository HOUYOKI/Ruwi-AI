//path: frontend/src/api/chatApi.ts
import { request } from "./apiClient";
import type { ChatResponse } from "../types/chat";

export function askRuwi(
  visitId: string,
  artifactId: number,
  question: string,
): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      visit_id: visitId,
      artifact_id: artifactId,
      question,
    }),
  });
}
