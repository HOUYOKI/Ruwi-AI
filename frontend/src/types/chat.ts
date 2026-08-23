export interface ChatSource {
  title: string;
  publisher: string;
  url: string;
}

export interface ReflectionMetadata {
  available: boolean;
  grounded: boolean;
  relevance_score: number;
  grounding_score: number;
  source_coverage_score: number;
  flagged_for_caution: boolean;
  unsupported_claims: string[];
  warnings: string[];
}

export interface ChatResponse {
  answer: string;
  hit_iteration_cap: boolean;
  audio_url: string | null;
  sources?: ChatSource[];
  reflection?: ReflectionMetadata | null;
}

export interface Exchange {
  question: string;
  answer: string;
  hitIterationCap: boolean;
  audioUrl: string | null;
}
