import type { ExperienceResponse } from "../../types/experience";
import HotspotStory from "./HotspotStory";
import QuizPanel from "./QuizPanel";
import SourceList from "./SourceList";
import ObjectAnatomy from "./ObjectAnatomy";
import StoryTimeline from "./StoryTimeline";

export default function ExperienceRenderer({ experience }: { experience: ExperienceResponse }) {
  return (
    <article className="mt-14 border-t border-neutral-800 pt-12">
      <header className="max-w-3xl">
        <p className="text-xs tracking-[0.28em] text-amber-400/80 uppercase">A Ruwi experience</p>
        <h2 className="mt-3 font-serif text-4xl leading-tight text-neutral-50 sm:text-5xl">{experience.title}</h2>
        <p className="mt-5 text-lg leading-8 text-neutral-300">{experience.summary}</p>
      </header>

      {experience.facts.length > 0 && (
        <dl className="mt-9 grid gap-px overflow-hidden rounded-lg border border-neutral-800 bg-neutral-800 sm:grid-cols-3">
          {experience.facts.map((fact) => (
            <div key={fact.label} className="bg-neutral-950 px-5 py-5">
              <dt className="text-xs tracking-[0.18em] text-neutral-500 uppercase">{fact.label}</dt>
              <dd className="mt-2 text-base text-neutral-100">{fact.value}</dd>
            </div>
          ))}
        </dl>
      )}

      {experience.story_sections.length > 0 && (
        <section className="my-12 grid gap-5 md:grid-cols-2" aria-label="Artifact story">
          {experience.story_sections.map((section, index) => (
            <div key={section.id} className="rounded-lg border border-neutral-800 bg-neutral-900/30 p-7">
              <p className="text-sm text-amber-300/70">0{index + 1}</p>
              <h3 className="mt-3 font-serif text-2xl text-neutral-50">{section.title}</h3>
              <p className="mt-3 text-base leading-7 text-neutral-400">{section.body}</p>
            </div>
          ))}
        </section>
      )}

      {experience.template === "hotspot_story" && experience.hotspots.length > 0 && (
        <div className="my-12">
          <HotspotStory artifact={experience.artifact} hotspots={experience.hotspots} />
        </div>
      )}

      {experience.template === "object_anatomy" && experience.hotspots.length > 0 && (
        <div className="my-12">
          <ObjectAnatomy artifact={experience.artifact} parts={experience.hotspots} />
        </div>
      )}

      {experience.template === "story_timeline" && experience.timeline.length > 0 && (
        <div className="my-12">
          <StoryTimeline events={experience.timeline} />
        </div>
      )}

      <div className="my-12">
        <QuizPanel questions={experience.quiz} />
      </div>
      <SourceList sources={experience.sources} />
    </article>
  );
}
