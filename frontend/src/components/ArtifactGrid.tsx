// ArtifactGrid.tsx
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { ApiError } from "../api/apiClient";
import { fetchArtifacts } from "../api/artifactApi";
import type { ArtifactSummary } from "../types/artifact";
import { shuffle } from "../utils/shuffle";
import ArtifactCarousel from "./ArtifactCarousel";
import StatusView from "./StatusView";

type LoadState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; artifacts: ArtifactSummary[] };

export default function ArtifactGrid() {
  const { t, i18n } = useTranslation();
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });

    fetchArtifacts(i18n.language)
      .then((artifacts) => {
        // Shuffled once per load (not persisted) - a fresh visit sees a different
        // starting order, but a single carousel session doesn't reshuffle mid-browse
        // (a language switch does re-shuffle, since it's a fresh load).
        if (!cancelled) setState({ status: "ready", artifacts: shuffle(artifacts) });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const message = err instanceof ApiError ? err.message : t("artifactGrid.genericError");
        setState({ status: "error", message });
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language]);

  if (state.status === "loading") {
    return <StatusView tone="loading" title={t("artifactGrid.loading")} />;
  }

  if (state.status === "error") {
    return (
      <StatusView
        tone="error"
        title={t("artifactGrid.errorTitle")}
        detail={state.message}
      />
    );
  }

  if (state.artifacts.length === 0) {
    return <StatusView tone="empty" title={t("artifactGrid.empty")} />;
  }

  const featured = state.artifacts.filter((artifact) => artifact.featured);

  return (
    <div className="space-y-12">
      {featured.length > 0 && (
        <section aria-labelledby="featured-heading">
          <p className="text-xs tracking-[0.24em] text-gold/80 uppercase">{t("artifactGrid.featuredEyebrow")}</p>
          <h2 id="featured-heading" className="mt-2 font-display text-3xl text-text">{t("artifactGrid.featuredTitle")}</h2>
          <div className="mt-5"><ArtifactCarousel artifacts={featured} /></div>
        </section>
      )}
      <section aria-labelledby="collection-heading">
        <h2 id="collection-heading" className="mb-5 font-display text-2xl text-text">{t("artifactGrid.collectionTitle")}</h2>
        <ArtifactCarousel artifacts={state.artifacts} />
      </section>
    </div>
  );
}
