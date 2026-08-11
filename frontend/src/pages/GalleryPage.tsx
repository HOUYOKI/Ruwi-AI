import ArtifactGrid from "../components/ArtifactGrid";

export default function GalleryPage() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-12">
      <header className="mb-10 border-b border-neutral-800 pb-6">
        <p className="text-xs tracking-[0.3em] text-amber-400/80 uppercase">Saudi National Museum</p>
        <h1 className="mt-2 font-serif text-4xl text-neutral-50">Ruwi — رُوي</h1>
        <p className="mt-2 max-w-xl text-sm text-neutral-500">
          Select an artifact to reveal its story — and the civilizations it quietly connects to.
        </p>
      </header>
      <ArtifactGrid />
    </main>
  );
}
