import { Link } from "react-router-dom";
import { resolveImageUrl } from "../api/client";
import type { ArtifactSummary } from "../types/artifact";

export default function ArtifactCard({ artifact }: { artifact: ArtifactSummary }) {
  return (
    <Link
      to={`/artifacts/${artifact.id}`}
      className="group flex flex-col overflow-hidden rounded-sm border border-neutral-800 bg-neutral-900/40 transition-colors hover:border-amber-400/40"
    >
      <div className="relative aspect-square overflow-hidden bg-neutral-900">
        {artifact.featured && (
          <span className="absolute left-3 top-3 z-10 rounded-full border border-amber-300/30 bg-neutral-950/85 px-3 py-1 text-[10px] font-semibold tracking-[0.16em] text-amber-200 uppercase backdrop-blur-sm">
            Ruwi Experience
          </span>
        )}
        <img
          src={resolveImageUrl(artifact.image_url)}
          alt={artifact.name}
          loading="lazy"
          className="h-full w-full object-contain p-6 transition-transform duration-500 group-hover:scale-105"
        />
      </div>
      <div className="border-t border-neutral-800 px-4 py-3">
        <h3 className="truncate font-serif text-base text-neutral-100">{artifact.name}</h3>
        <p className="mt-0.5 truncate text-xs text-neutral-500">{artifact.age}</p>
      </div>
    </Link>
  );
}
