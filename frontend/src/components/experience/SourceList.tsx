import type { ExperienceSource } from "../../types/experience";
import { useTranslation } from "react-i18next";

export default function SourceList({ sources }: { sources: ExperienceSource[] }) {
  const { t } = useTranslation();
  return (
    <section aria-labelledby="sources-title" className="border-t border-border pt-7">
      <h3 id="sources-title" className="text-xs tracking-[0.24em] text-text-muted uppercase">{t("experience.sources")}</h3>
      <ul className="mt-4 space-y-3">
        {sources.map((source) => (
          <li key={source.id}>
            <a
              href={source.url}
              target="_blank"
              rel="noreferrer"
              className="flex min-h-12 items-center justify-between gap-4 rounded-md border border-border px-4 py-3 text-sm text-text-muted transition hover:border-gold/40 hover:text-gold"
            >
              <span>
                <span className="block font-medium">{source.title}</span>
                <span className="mt-0.5 block text-xs text-text-muted">{source.publisher}</span>
              </span>
              <span aria-hidden="true">↗</span>
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
