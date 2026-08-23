export interface ArtifactSummary {
  id: number;
  name: string;
  age: string;
  location: string;
  material: string;
  image_url: string;
  featured: boolean;
}

export interface ArtifactDetail extends ArtifactSummary {
  description: string;
}
