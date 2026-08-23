import type { ExperienceArtifact, Hotspot } from "../../types/experience";
import HotspotStory from "./HotspotStory";
import { useTranslation } from "react-i18next";

export default function ObjectAnatomy({
  artifact,
  parts,
}: {
  artifact: ExperienceArtifact;
  parts: Hotspot[];
}) {
  const { t } = useTranslation();
  return (
    <HotspotStory
      artifact={artifact}
      hotspots={parts}
      eyebrow={t("experience.objectAnatomy")}
      title={t("experience.exploreParts")}
      instruction={t("experience.tapPart")}
    />
  );
}
