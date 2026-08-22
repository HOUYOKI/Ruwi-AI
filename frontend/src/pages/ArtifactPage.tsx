import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useParams } from "react-router-dom";
import { ApiError, resolveImageUrl } from "../api/apiClient";
import { fetchArtifact } from "../api/artifactApi";
import type { ArtifactDetail as ArtifactDetailType } from "../types/artifact";
import ArtifactDetail from "../components/ArtifactDetail";
import ArtifactImageViewer from "../components/ArtifactImageViewer";
import ChatPanel from "../components/ChatPanel";
import StatusView from "../components/StatusView";

type LoadState =
  | { status: "loading" }
  | { status: "not-found" }
  | { status: "error"; message: string }
  | { status: "ready"; artifact: ArtifactDetailType };

export default function ArtifactPage() {
  const { t, i18n } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setState({ status: "loading" });

    fetchArtifact(id, i18n.language)
      .then((artifact) => {
        if (!cancelled) setState({ status: "ready", artifact });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 404) {
          setState({ status: "not-found" });
        } else {
          const message = err instanceof ApiError ? err.message : t("artifactPage.genericError");
          setState({ status: "error", message });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [id, i18n.language, t]);

  return (
    <main className="min-h-screen w-full px-6 py-8">
      <Link to="/" className="text-xs tracking-[0.2em] text-text-muted uppercase hover:text-gold">
        ← {t("artifactPage.backToGallery")}
      </Link>

      <div className="mt-4">
        {state.status === "loading" && <StatusView tone="loading" title={t("artifactPage.loading")} />}

        {state.status === "not-found" && (
          <StatusView
            tone="error"
            title={t("artifactPage.notFoundTitle")}
            detail={t("artifactPage.notFoundDetail")}
          />
        )}

        {state.status === "error" && (
          <StatusView tone="error" title={t("artifactPage.errorTitle")} detail={state.message} />
        )}

        {state.status === "ready" && (
          <div className="flex flex-col gap-8">
            <div className="flex flex-col gap-3">
              <h1 className="font-display text-3xl tracking-tight text-text">{state.artifact.name}</h1>
              <dl className="flex flex-wrap gap-2">
                <div className="rounded-sm border border-gold/30 bg-gold/10 px-2.5 py-1 text-xs tracking-[0.15em] text-gold tabular-nums">
                  <dt className="sr-only">{t("artifactPage.age")}</dt>
                  <dd className="inline">{state.artifact.age}</dd>
                </div>
                <div className="rounded-sm border border-gold/30 bg-gold/10 px-2.5 py-1 text-xs tracking-[0.15em] text-gold">
                  <dt className="sr-only">{t("artifactPage.location")}</dt>
                  <dd className="inline">{state.artifact.location}</dd>
                </div>
                <div className="rounded-sm border border-gold/30 bg-gold/10 px-2.5 py-1 text-xs tracking-[0.15em] text-gold">
                  <dt className="sr-only">{t("artifactPage.material")}</dt>
                  <dd className="inline">{state.artifact.material}</dd>
                </div>
              </dl>
            </div>

            <div className="grid grid-cols-1 gap-10 lg:grid-cols-[45%_55%] lg:items-start">
              <div className="flex min-w-0 flex-col gap-8">
                <ArtifactImageViewer
                  imageUrl={`${resolveImageUrl(state.artifact.image_url)}?v=${state.artifact.id}`}
                  alt={state.artifact.name}
                />
                <ArtifactDetail artifact={state.artifact} />
              </div>
              <div className="flex min-w-0 flex-col lg:border-l lg:border-border lg:pl-6">
                <ChatPanel artifactId={state.artifact.id} />
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
