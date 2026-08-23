import type { ExperienceSource } from "../../types/experience";

export default function SourceList({ sources }: { sources: ExperienceSource[] }) {
  return (
    <section aria-labelledby="sources-title" className="border-t border-neutral-800 pt-7">
      <h3 id="sources-title" className="text-xs tracking-[0.24em] text-neutral-500 uppercase">Trusted sources</h3>
      <ul className="mt-4 space-y-3">
        {sources.map((source) => (
          <li key={source.id}>
            <a
              href={source.url}
              target="_blank"
              rel="noreferrer"
              className="flex min-h-12 items-center justify-between gap-4 rounded-md border border-neutral-800 px-4 py-3 text-sm text-neutral-300 transition hover:border-amber-400/40 hover:text-amber-200"
            >
              <span>
                <span className="block font-medium">{source.title}</span>
                <span className="mt-0.5 block text-xs text-neutral-500">{source.publisher}</span>
              </span>
              <span aria-hidden="true">↗</span>
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
