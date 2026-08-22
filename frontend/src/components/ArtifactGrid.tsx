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

  return <ArtifactCarousel artifacts={state.artifacts} />;
}
