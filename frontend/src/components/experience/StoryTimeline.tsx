import { useState } from "react";
import type { TimelineEvent } from "../../types/experience";
import { useTranslation } from "react-i18next";

export default function StoryTimeline({ events }: { events: TimelineEvent[] }) {
  const { t } = useTranslation();
  const [activeId, setActiveId] = useState(events[0]?.id ?? "");
  const active = events.find((event) => event.id === activeId) ?? events[0];

  if (!active) return null;

  return (
    <section aria-labelledby="timeline-title">
      <p className="text-xs tracking-[0.24em] text-gold/80 uppercase">{t("experience.timeline")}</p>
      <h3 id="timeline-title" className="mt-2 font-display text-3xl text-text sm:text-4xl">
        {t("experience.followJourney")}
      </h3>
      <div className="mt-7 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="relative space-y-3 before:absolute before:bottom-6 before:start-6 before:top-6 before:w-px before:bg-border">
          {events.map((event, index) => (
            <button
              key={event.id}
              type="button"
              aria-pressed={event.id === activeId}
              onClick={() => setActiveId(event.id)}
              className={`relative flex min-h-20 w-full items-center gap-5 rounded-lg border p-4 text-start transition ${
                event.id === activeId
                  ? "border-gold/60 bg-gold/10"
                  : "border-border bg-surface hover:border-gold/30"
              }`}
            >
              <span className={`z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border text-sm font-semibold ${
                event.id === activeId
                  ? "border-gold bg-gold text-bg"
                  : "border-border bg-bg text-text-muted"
              }`}>
                {index + 1}
              </span>
              <span>
                <span className="block text-xs tracking-[0.16em] text-gold/80 uppercase">{event.label}</span>
                <span className="mt-1 block text-base font-medium text-text">{event.title}</span>
              </span>
            </button>
          ))}
        </div>
        <div className="flex min-h-64 flex-col justify-center rounded-lg border border-gold/20 bg-gold/[0.06] p-8" aria-live="polite">
          <p className="text-xs tracking-[0.22em] text-gold uppercase">{active.label}</p>
          <h4 className="mt-3 font-display text-3xl text-text">{active.title}</h4>
          <p className="mt-4 text-lg leading-8 text-text-muted">{active.body}</p>
        </div>
      </div>
    </section>
  );
}
