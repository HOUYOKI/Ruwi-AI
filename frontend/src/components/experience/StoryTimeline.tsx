import { useState } from "react";
import type { TimelineEvent } from "../../types/experience";

export default function StoryTimeline({ events }: { events: TimelineEvent[] }) {
  const [activeId, setActiveId] = useState(events[0]?.id ?? "");
  const active = events.find((event) => event.id === activeId) ?? events[0];

  if (!active) return null;

  return (
    <section aria-labelledby="timeline-title">
      <p className="text-xs tracking-[0.24em] text-amber-400/80 uppercase">Across time</p>
      <h3 id="timeline-title" className="mt-2 font-serif text-3xl text-neutral-50 sm:text-4xl">
        Follow the artifact's journey
      </h3>
      <div className="mt-7 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="relative space-y-3 before:absolute before:bottom-6 before:left-6 before:top-6 before:w-px before:bg-neutral-700">
          {events.map((event, index) => (
            <button
              key={event.id}
              type="button"
              aria-pressed={event.id === activeId}
              onClick={() => setActiveId(event.id)}
              className={`relative flex min-h-20 w-full items-center gap-5 rounded-lg border p-4 text-left transition ${
                event.id === activeId
                  ? "border-amber-300/60 bg-amber-400/10"
                  : "border-neutral-800 bg-neutral-950 hover:border-neutral-600"
              }`}
            >
              <span className={`z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border text-sm font-semibold ${
                event.id === activeId
                  ? "border-amber-200 bg-amber-300 text-neutral-950"
                  : "border-neutral-700 bg-neutral-900 text-neutral-400"
              }`}>
                {index + 1}
              </span>
              <span>
                <span className="block text-xs tracking-[0.16em] text-amber-300/80 uppercase">{event.label}</span>
                <span className="mt-1 block text-base font-medium text-neutral-100">{event.title}</span>
              </span>
            </button>
          ))}
        </div>
        <div className="flex min-h-64 flex-col justify-center rounded-lg border border-amber-400/20 bg-amber-400/[0.06] p-8" aria-live="polite">
          <p className="text-xs tracking-[0.22em] text-amber-300 uppercase">{active.label}</p>
          <h4 className="mt-3 font-serif text-3xl text-neutral-50">{active.title}</h4>
          <p className="mt-4 text-lg leading-8 text-neutral-300">{active.body}</p>
        </div>
      </div>
    </section>
  );
}
