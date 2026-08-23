export interface ChatResponse {
  answer: string;
  hit_iteration_cap: boolean;
  audio_url: string | null;
}

export interface Exchange {
  question: string;
  answer: string;
  hitIterationCap: boolean;
  audioUrl: string | null;
}
