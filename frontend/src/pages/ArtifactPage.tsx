import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, fetchArtifact, resolveImageUrl } from "../api/client";
import type { ArtifactDetail as ArtifactDetailType } from "../types/artifact";
import ArtifactDetail from "../components/ArtifactDetail";
import ArtifactViewer3D from "../components/ArtifactViewer3D";
import ChatPanel from "../components/ChatPanel";
import StatusView from "../components/StatusView";

type LoadState =
  | { status: "loading" }
  | { status: "not-found" }
  | { status: "error"; message: string }
  | { status: "ready"; artifact: ArtifactDetailType };

export default function ArtifactPage() {
  const { id } = useParams<{ id: string }>();
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setState({ status: "loading" });

    fetchArtifact(id)
      .then((artifact) => {
        if (!cancelled) setState({ status: "ready", artifact });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 404) {
          setState({ status: "not-found" });
        } else {
          const message = err instanceof ApiError ? err.message : "Something went wrong loading this artifact.";
          setState({ status: "error", message });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [id]);

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <Link to="/" className="text-xs tracking-[0.2em] text-neutral-500 uppercase hover:text-amber-400">
        ← Back to gallery
      </Link>

      <div className="mt-6">
        {state.status === "loading" && <StatusView tone="loading" title="Loading artifact…" />}

        {state.status === "not-found" && (
          <StatusView
            tone="error"
            title="This artifact couldn't be found"
            detail="It may have been removed, or the link is incorrect."
          />
        )}

        {state.status === "error" && (
          <StatusView tone="error" title="Couldn't load this artifact" detail={state.message} />
        )}

        {state.status === "ready" && (
          <div className="grid grid-cols-1 gap-10 lg:grid-cols-2">
            <ArtifactViewer3D
              imageUrl={`${resolveImageUrl(state.artifact.image_url)}?v=${state.artifact.id}`}
              alt={state.artifact.name}
            />
            <div className="flex flex-col gap-8">
              <ArtifactDetail artifact={state.artifact} />
              <ChatPanel artifactId={state.artifact.id} />
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
