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

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
      {state.artifacts.map((artifact) => (
        <ArtifactCard key={artifact.id} artifact={artifact} />
      ))}
    </div>
  );
}
