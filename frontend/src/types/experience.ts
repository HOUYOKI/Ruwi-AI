export type ExperienceTemplate =
  | "visual_story"
  | "story_timeline"
  | "hotspot_story"
  | "object_anatomy";

export interface ExperienceArtifact {
  id: number;
  name: string;
  age: string;
  location: string;
  material: string;
  image_url: string;
}

export interface StorySection {
  id: string;
  title: string;
  body: string;
}

export interface TimelineEvent {
  id: string;
  label: string;
  title: string;
  body: string;
}

export interface ExperienceFact {
  label: string;
  value: string;
}

export interface Hotspot {
  id: string;
  x: number;
  y: number;
  title: string;
  body: string;
}

export interface QuizQuestion {
  id: string;
  prompt: string;
  choices: string[];
  correct_index: number;
  explanation: string;
}

export interface ExperienceSource {
  id: string;
  title: string;
  publisher: string;
  url: string;
  source_type: "museum_panel" | "museum" | "government" | "academic";
}

export interface ExperienceMetadata {
  language: "en" | "ar";
  confidence: number;
  generated: boolean;
  warnings: string[];
  schema_version: "1.0";
}

export interface ExperienceResponse {
  artifact: ExperienceArtifact;
  template: ExperienceTemplate;
  title: string;
  summary: string;
  narration: string;
  sources: ExperienceSource[];
  metadata: ExperienceMetadata;
  story_sections: StorySection[];
  timeline: TimelineEvent[];
  facts: ExperienceFact[];
  hotspots: Hotspot[];
  quiz: QuizQuestion[];
}
