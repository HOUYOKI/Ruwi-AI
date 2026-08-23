import { useState } from "react";
import { resolveImageUrl } from "../../api/client";
import type { ExperienceArtifact, Hotspot } from "../../types/experience";

export default function HotspotStory({
  artifact,
  hotspots,
  eyebrow = "Look closer",
  title = "Discover the details",
  instruction = "Tap a glowing marker",
}: {
  artifact: ExperienceArtifact;
  hotspots: Hotspot[];
  eyebrow?: string;
  title?: string;
  instruction?: string;
}) {
  const [activeId, setActiveId] = useState(hotspots[0]?.id ?? "");
  const active = hotspots.find((hotspot) => hotspot.id === activeId) ?? hotspots[0];

  return (
    <section aria-labelledby="hotspot-title">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs tracking-[0.24em] text-amber-400/80 uppercase">{eyebrow}</p>
          <h3 id="hotspot-title" className="mt-2 font-serif text-3xl text-neutral-50">
            {title}
          </h3>
        </div>
        <p className="text-sm text-neutral-500">{instruction}</p>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
        <div className="relative aspect-[4/3] overflow-hidden rounded-lg border border-neutral-800 bg-black">
          <img
            src={resolveImageUrl(artifact.image_url)}
            alt={artifact.name}
            className="h-full w-full object-contain"
          />
          {hotspots.map((hotspot, index) => (
            <button
              key={hotspot.id}
              type="button"
              aria-label={`Explore ${hotspot.title}`}
              aria-pressed={hotspot.id === activeId}
              onClick={() => setActiveId(hotspot.id)}
              style={{ left: `${hotspot.x * 100}%`, top: `${hotspot.y * 100}%` }}
              className={`absolute flex h-12 w-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border text-base font-semibold shadow-[0_0_28px_rgba(251,191,36,0.35)] transition ${
                hotspot.id === activeId
                  ? "scale-110 border-amber-200 bg-amber-300 text-neutral-950"
                  : "border-amber-300/80 bg-neutral-950/80 text-amber-200 hover:scale-110"
              }`}
            >
              {index + 1}
            </button>
          ))}
        </div>

        {active && (
          <div className="flex min-h-48 flex-col justify-center rounded-lg border border-amber-400/20 bg-amber-400/[0.06] p-7" aria-live="polite">
            <p className="text-xs tracking-[0.22em] text-amber-300 uppercase">Selected detail</p>
            <h4 className="mt-3 font-serif text-2xl text-neutral-50">{active.title}</h4>
            <p className="mt-3 text-base leading-7 text-neutral-300">{active.body}</p>
          </div>
        )}
      </div>
    </section>
  );
}
