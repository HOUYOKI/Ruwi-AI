import { Link, useNavigate } from "react-router-dom";
import ArtifactUpload from "../components/ArtifactUpload";

export default function IdentifyPage() {
  const navigate = useNavigate();

  return (
    <main className="mx-auto max-w-5xl px-6 py-10 sm:py-14">
      <div className="flex items-center justify-between gap-4">
        <Link to="/" className="inline-flex min-h-12 items-center rounded-md px-3 text-sm tracking-[0.16em] text-neutral-400 uppercase hover:bg-neutral-900 hover:text-amber-300">
          ← Explore collection
        </Link>
        <p className="text-xs tracking-[0.22em] text-neutral-600 uppercase">Artifact recognition</p>
      </div>
      <header className="mt-10 max-w-3xl">
        <p className="text-xs tracking-[0.28em] text-amber-400/80 uppercase">Upload or take a photo</p>
        <h1 className="mt-3 font-serif text-4xl leading-tight text-neutral-50 sm:text-6xl">What story are you holding?</h1>
        <p className="mt-5 text-lg leading-8 text-neutral-400">
          Photograph an artifact and Ruwi will look for it among the museum's supported showcase pieces.
        </p>
      </header>
      <ArtifactUpload onMatched={(artifactId) => navigate(`/artifacts/${artifactId}`)} />
      <div className="mt-8 text-center">
        <Link to="/" className="inline-flex min-h-12 items-center rounded-md px-5 text-sm text-neutral-400 hover:text-amber-200">
          Browse the collection manually instead
        </Link>
      </div>
    </main>
  );
}
