import { useState } from "react";
import { resolveImageUrl } from "../../api/apiClient";
import type { ExperienceArtifact, Hotspot } from "../../types/experience";
import { useTranslation } from "react-i18next";

export default function HotspotStory({
  artifact,
  hotspots,
  eyebrow,
  title,
  instruction,
}: {
  artifact: ExperienceArtifact;
  hotspots: Hotspot[];
  eyebrow?: string;
  title?: string;
  instruction?: string;
}) {
  const { t } = useTranslation();
  const [activeId, setActiveId] = useState(hotspots[0]?.id ?? "");
  const active = hotspots.find((hotspot) => hotspot.id === activeId) ?? hotspots[0];

  return (
    <section aria-labelledby="hotspot-title">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs tracking-[0.24em] text-gold/80 uppercase">{eyebrow ?? t("experience.lookCloser")}</p>
          <h3 id="hotspot-title" className="mt-2 font-display text-3xl text-text">
            {title ?? t("experience.discoverDetails")}
          </h3>
        </div>
        <p className="text-sm text-text-muted">{instruction ?? t("experience.tapMarker")}</p>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
        <div className="relative aspect-[4/3] overflow-hidden rounded-lg border border-border bg-surface">
          <img
            src={resolveImageUrl(artifact.image_url)}
            alt={artifact.name}
            className="h-full w-full object-contain"
          />
          {hotspots.map((hotspot, index) => (
            <button
              key={hotspot.id}
              type="button"
              aria-label={`${t("experience.explore")} ${hotspot.title}`}
              aria-pressed={hotspot.id === activeId}
              onClick={() => setActiveId(hotspot.id)}
              style={{ left: `${hotspot.x * 100}%`, top: `${hotspot.y * 100}%` }}
              className={`absolute flex h-12 w-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border text-base font-semibold shadow-[0_0_28px_rgba(251,191,36,0.35)] transition ${
                hotspot.id === activeId
                  ? "scale-110 border-gold bg-gold text-bg"
                  : "border-gold/70 bg-surface/90 text-gold hover:scale-110"
              }`}
            >
              {index + 1}
            </button>
          ))}
        </div>

        {active && (
          <div className="flex min-h-48 flex-col justify-center rounded-lg border border-gold/20 bg-gold/[0.06] p-7" aria-live="polite">
            <p className="text-xs tracking-[0.22em] text-gold uppercase">{t("experience.selectedDetail")}</p>
            <h4 className="mt-3 font-display text-2xl text-text">{active.title}</h4>
            <p className="mt-3 text-base leading-7 text-text-muted">{active.body}</p>
          </div>
        )}
      </div>
    </section>
  );
}
