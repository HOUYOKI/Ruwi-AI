//artifact card component for displaying artifact summary information in a card format
import { Link } from "react-router-dom";
import { resolveImageUrl } from "../api/apiClient";
import { useCroppedArtifactImage } from "../hooks/useCroppedArtifactImage";
import type { ArtifactSummary } from "../types/artifact";

export default function ArtifactCard({ artifact, priority = false }: { artifact: ArtifactSummary; priority?: boolean }) {
  // Cropped to the artifact's real content first (see the hook's own comment on why -
  // these PNGs carry large transparent margins), then object-contain rather than cover:
  // a hard cover-crop into a tall tile would zoom past recognizable shape for anything
  // that isn't already portrait-shaped (a landscape bone read as unrecognizable texture).
  const { src } = useCroppedArtifactImage(resolveImageUrl(artifact.image_url));

  return (
    <Link
      to={`/artifacts/${artifact.id}`}
      className="group relative block h-full w-full overflow-hidden"
      style={{ background: "linear-gradient(180deg, color-mix(in srgb, var(--surface) 100%, white 5%), var(--surface))" }}
    >
      <img
        src={src}
        alt={artifact.name}
        loading={priority ? "eager" : "lazy"}
        fetchPriority={priority ? "high" : "auto"}
        className="h-full w-full object-contain transition-transform duration-500 group-hover:scale-105"
      />
    </Link>
  );
}
