import { useEffect, useState } from "react";
import { ApiError, fetchArtifacts } from "../api/client";
import type { ArtifactSummary } from "../types/artifact";
import ArtifactCard from "./ArtifactCard";
import StatusView from "./StatusView";

type LoadState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; artifacts: ArtifactSummary[] };

export default function ArtifactGrid() {
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    fetchArtifacts()
      .then((artifacts) => {
        if (!cancelled) setState({ status: "ready", artifacts });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const message = err instanceof ApiError ? err.message : "Something went wrong loading the gallery.";
        setState({ status: "error", message });
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (state.status === "loading") {
    return <StatusView tone="loading" title="Loading the gallery…" />;
  }

  if (state.status === "error") {
    return (
      <StatusView
        tone="error"
        title="Couldn't load the artifact gallery"
        detail={state.message}
      />
    );
  }

  if (state.artifacts.length === 0) {
    return <StatusView tone="empty" title="No artifacts are available yet." />;
  }

  const featured = state.artifacts.filter((artifact) => artifact.featured);
  const collection = state.artifacts.filter((artifact) => !artifact.featured);

  return (
    <div className="space-y-14">
      {featured.length > 0 && (
        <section aria-labelledby="featured-heading">
          <div className="mb-5 flex items-end justify-between gap-4">
            <div>
              <p className="text-xs tracking-[0.24em] text-amber-400/80 uppercase">Curated for exploration</p>
              <h2 id="featured-heading" className="mt-2 font-serif text-3xl text-neutral-50">Featured Experiences</h2>
            </div>
            <p className="hidden text-sm text-neutral-500 sm:block">Story · Details · Quiz</p>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            {featured.map((artifact) => <ArtifactCard key={artifact.id} artifact={artifact} />)}
          </div>
        </section>
      )}
      <section aria-labelledby="collection-heading">
        <h2 id="collection-heading" className="mb-5 font-serif text-2xl text-neutral-200">Explore the Collection</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          {collection.map((artifact) => <ArtifactCard key={artifact.id} artifact={artifact} />)}
        </div>
      </section>
    </div>
  );
}
