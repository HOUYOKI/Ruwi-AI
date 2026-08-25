import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useParams } from "react-router-dom";
import { ApiError, fetchArtifactExperience, resolveImageUrl } from "../api/apiClient";
import { fetchArtifact } from "../api/artifactApi";
import ArtifactDetail from "../components/ArtifactDetail";
import ArtifactImageViewer from "../components/ArtifactImageViewer";
import ChatPanel from "../components/ChatPanel";
import ExperienceRenderer from "../components/experience/ExperienceRenderer";
import StatusView from "../components/StatusView";
import type { ArtifactDetail as ArtifactDetailType } from "../types/artifact";
import type { ExperienceResponse } from "../types/experience";

type LoadState = { status: "loading" } | { status: "not-found" } | { status: "error"; message: string } | { status: "ready"; artifact: ArtifactDetailType };

export default function ArtifactPage({ visitId }: { visitId: string }) {
  const { t, i18n } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const [state, setState] = useState<LoadState>({ status: "loading" });
  const [experience, setExperience] = useState<ExperienceResponse | null>(null);
  const [experienceStatus, setExperienceStatus] = useState<"idle" | "loading" | "error">("idle");

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setState({ status: "loading" }); setExperience(null); setExperienceStatus("loading");
    Promise.allSettled([fetchArtifact(id, i18n.language), fetchArtifactExperience(id, i18n.language)]).then(([artifactResult, experienceResult]) => {
      if (cancelled) return;
      if (artifactResult.status === "fulfilled") setState({ status: "ready", artifact: artifactResult.value });
      else if (artifactResult.reason instanceof ApiError && artifactResult.reason.status === 404) setState({ status: "not-found" });
      else setState({ status: "error", message: artifactResult.reason instanceof ApiError ? artifactResult.reason.message : t("artifactPage.genericError") });
      if (experienceResult.status === "fulfilled") { setExperience(experienceResult.value); setExperienceStatus("idle"); }
      else if (experienceResult.reason instanceof ApiError && experienceResult.reason.status === 404) setExperienceStatus("idle");
      else setExperienceStatus("error");
    });
    return () => { cancelled = true; };
  }, [id, i18n.language, t]);

  return (
    <main className="min-h-screen w-full px-6 py-8">
      <Link to="/" className="inline-flex min-h-12 items-center text-xs tracking-[0.2em] text-text-muted uppercase hover:text-gold">← {t("artifactPage.backToGallery")}</Link>
      <div className="mt-4">
        {state.status === "loading" && <StatusView tone="loading" title={t("artifactPage.loading")} />}
        {state.status === "not-found" && <StatusView tone="error" title={t("artifactPage.notFoundTitle")} detail={t("artifactPage.notFoundDetail")} />}
        {state.status === "error" && <StatusView tone="error" title={t("artifactPage.errorTitle")} detail={state.message} />}
        {state.status === "ready" && <div className="flex flex-col gap-8">
          <div className="flex flex-col gap-3"><h1 className="font-display text-3xl tracking-tight text-text">{state.artifact.name}</h1><dl className="flex flex-wrap gap-2">
            {[[t("artifactPage.age"), state.artifact.age], [t("artifactPage.location"), state.artifact.location], [t("artifactPage.material"), state.artifact.material]].map(([label, value]) => <div key={label} className="rounded-sm border border-gold/30 bg-gold/10 px-2.5 py-1 text-xs tracking-[0.15em] text-gold"><dt className="sr-only">{label}</dt><dd>{value}</dd></div>)}
          </dl></div>
          <div className="grid grid-cols-1 gap-10 lg:grid-cols-[45%_55%] lg:items-start">
            <div className="flex min-w-0 flex-col gap-8"><ArtifactImageViewer imageUrl={`${resolveImageUrl(state.artifact.image_url)}?v=${state.artifact.id}`} alt={state.artifact.name} /><ArtifactDetail artifact={state.artifact} /></div>
            <div className="flex min-w-0 flex-col lg:border-s lg:border-border lg:ps-6"><ChatPanel artifactId={state.artifact.id} visitId={visitId} /></div>
          </div>
          {(experience || experienceStatus !== "idle") && <div className="border-t border-border pt-6 text-center">
            {experience && <a href="#interactive-experience" className="inline-flex min-h-12 items-center gap-2 text-sm font-medium text-gold hover:underline">{t("artifactPage.experienceCue")} <span aria-hidden="true">↓</span></a>}
            {experienceStatus === "loading" && <p className="text-sm text-text-muted">{t("artifactPage.experienceLoading")}</p>}
            {experienceStatus === "error" && <button type="button" onClick={() => window.location.reload()} className="min-h-11 rounded-sm border border-border px-4 text-sm text-text-muted hover:border-gold/40 hover:text-gold">{t("artifactPage.experienceError")}</button>}
          </div>}
          {experience && <div id="interactive-experience"><ExperienceRenderer experience={experience} /></div>}
        </div>}
      </div>
    </main>
  );
}
