import { useTranslation } from "react-i18next";
import ArtifactGrid from "../components/ArtifactGrid";

export default function GalleryPage() {
  const { t } = useTranslation();

  return (
    <main className="flex min-h-screen w-full flex-col justify-center px-6 py-16 sm:px-10 lg:px-16">
      <header className="mb-10 text-center">
        <p className="text-xs tracking-[0.3em] text-gold/80 uppercase">{t("gallery.eyebrow")}</p>
        <h1 className="mt-2 font-display text-4xl tracking-tight text-text">Ruwi — رُوي</h1>
        <p className="mx-auto mt-2 max-w-xl text-sm text-text-muted">{t("gallery.subtitleStory")}</p>
        <p className="mx-auto mt-1 max-w-xl text-sm text-text-muted">{t("gallery.subtitleGrounded")}</p>
      </header>
      <ArtifactGrid />
      <p className="mt-10 text-center text-sm text-text-muted">{t("gallery.footer")}</p>
    </main>
  );
}
