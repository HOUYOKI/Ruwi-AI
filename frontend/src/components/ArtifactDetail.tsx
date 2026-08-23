// ArtifactDetail.tsx
import type { ArtifactDetail as ArtifactDetailType } from "../types/artifact";

export default function ArtifactDetail({ artifact }: { artifact: ArtifactDetailType }) {
  return <p className="text-sm leading-relaxed text-text-muted">{artifact.description}</p>;
}
