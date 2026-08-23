import { lazy, Suspense, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, fetchArtifact, fetchArtifactExperience, resolveImageUrl } from "../api/client";
import type { ArtifactDetail as ArtifactDetailType } from "../types/artifact";
import type { ExperienceResponse } from "../types/experience";
import ArtifactDetail from "../components/ArtifactDetail";
import ChatPanel from "../components/ChatPanel";
import StatusView from "../components/StatusView";
import ExperienceRenderer from "../components/experience/ExperienceRenderer";

const ArtifactViewer3D = lazy(() => import("../components/ArtifactViewer3D"));

type LoadState =
  | { status: "loading" }
  | { status: "not-found" }
  | { status: "error"; message: string }
  | { status: "ready"; artifact: ArtifactDetailType };

export default function ArtifactPage() {
  const { id } = useParams<{ id: string }>();
  const [state, setState] = useState<LoadState>({ status: "loading" });
  const [experience, setExperience] = useState<ExperienceResponse | null>(null);
  const [experienceLoading, setExperienceLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setState({ status: "loading" });
    setExperience(null);
    setExperienceLoading(true);

    fetchArtifactExperience(id)
      .then((result) => {
        if (!cancelled) setExperience(result);
      })
      .catch(() => {
        // Experiences are progressive enhancement. The existing artifact
        // detail remains fully usable when one is unavailable.
      })
      .finally(() => {
        if (!cancelled) setExperienceLoading(false);
      });

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
      <Link to="/" className="inline-flex min-h-12 items-center rounded-md px-3 text-sm tracking-[0.16em] text-neutral-400 uppercase hover:bg-neutral-900 hover:text-amber-300">
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
          <div>
            <div className="grid grid-cols-1 gap-10 lg:grid-cols-2">
              <Suspense
                fallback={
                  <div className="aspect-square overflow-hidden rounded-sm border border-neutral-800 bg-neutral-950">
                    <img
                      src={resolveImageUrl(state.artifact.image_url)}
                      alt={state.artifact.name}
                      className="h-full w-full object-contain p-6"
                    />
                  </div>
                }
              >
                <ArtifactViewer3D
                  imageUrl={`${resolveImageUrl(state.artifact.image_url)}?v=${state.artifact.id}`}
                  alt={state.artifact.name}
                />
              </Suspense>
              <ArtifactDetail artifact={state.artifact} />
            </div>
            {experienceLoading && (
              <div className="mt-12 flex min-h-36 items-center justify-center gap-4 border-t border-neutral-800 pt-10 text-neutral-400">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-neutral-700 border-t-amber-400" />
                <p className="text-base">Preparing your Ruwi experience…</p>
              </div>
            )}
            {experience && <ExperienceRenderer experience={experience} />}
            <div className="mt-14 max-w-3xl border-t border-neutral-800 pt-8">
              <ChatPanel artifactId={state.artifact.id} />
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
