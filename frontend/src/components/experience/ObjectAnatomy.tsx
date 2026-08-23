import type { ExperienceArtifact, Hotspot } from "../../types/experience";
import HotspotStory from "./HotspotStory";

export default function ObjectAnatomy({
  artifact,
  parts,
}: {
  artifact: ExperienceArtifact;
  parts: Hotspot[];
}) {
  return (
    <HotspotStory
      artifact={artifact}
      hotspots={parts}
      eyebrow="Object anatomy"
      title="Explore its parts"
      instruction="Tap a labeled part"
    />
  );
}
