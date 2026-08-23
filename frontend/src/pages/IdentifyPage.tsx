import { Link, useNavigate } from "react-router-dom";
import ArtifactUpload from "../components/ArtifactUpload";
import { useTranslation } from "react-i18next";

export default function IdentifyPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <main className="mx-auto max-w-5xl px-6 py-10 text-text sm:py-14">
      <div className="flex items-center justify-between gap-4">
        <Link to="/" className="inline-flex min-h-12 items-center rounded-md px-3 text-sm tracking-[0.16em] text-text-muted uppercase hover:bg-surface hover:text-gold">
          ← {t("identify.back")}
        </Link>
        <p className="text-xs tracking-[0.22em] text-text-muted uppercase">{t("identify.recognition")}</p>
      </div>
      <header className="mt-10 max-w-3xl">
        <p className="text-xs tracking-[0.28em] text-gold/80 uppercase">{t("identify.eyebrow")}</p>
        <h1 className="mt-3 font-display text-4xl leading-tight text-text sm:text-6xl">{t("identify.title")}</h1>
        <p className="mt-5 text-lg leading-8 text-text-muted">
          {t("identify.subtitle")}
        </p>
      </header>
      <ArtifactUpload onMatched={(artifactId) => navigate(`/artifacts/${artifactId}`)} />
      <div className="mt-8 text-center">
        <Link to="/" className="inline-flex min-h-12 items-center rounded-md px-5 text-sm text-text-muted hover:text-gold">
          {t("identify.browseInstead")}
        </Link>
      </div>
    </main>
  );
}
