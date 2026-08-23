import ArtifactGrid from "../components/ArtifactGrid";
import { Link } from "react-router-dom";

export default function GalleryPage() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-12">
      <header className="mb-10 flex flex-col gap-6 border-b border-neutral-800 pb-7 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs tracking-[0.3em] text-amber-400/80 uppercase">Saudi National Museum</p>
          <h1 className="mt-2 font-serif text-4xl text-neutral-50">Ruwi — رُوي</h1>
          <p className="mt-2 max-w-xl text-sm text-neutral-500">
            Select an artifact to reveal its story — and the civilizations it quietly connects to.
          </p>
        </div>
        <Link
          to="/identify"
          className="inline-flex min-h-14 shrink-0 items-center justify-center rounded-md border border-amber-400/40 bg-amber-400/10 px-6 py-3 text-sm font-semibold text-amber-200 transition hover:bg-amber-400/20"
        >
          Scan / Upload Artifact
        </Link>
      </header>
      <ArtifactGrid />
    </main>
  );
}
