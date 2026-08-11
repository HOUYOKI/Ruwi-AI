import type { ArtifactDetail as ArtifactDetailType } from "../types/artifact";

export default function ArtifactDetail({ artifact }: { artifact: ArtifactDetailType }) {
  const facts: Array<[string, string]> = [
    ["Age", artifact.age],
    ["Location", artifact.location],
    ["Material", artifact.material],
  ];

  return (
    <div>
      <h1 className="font-serif text-3xl text-neutral-50">{artifact.name}</h1>
      <dl className="mt-4 grid grid-cols-1 gap-x-6 gap-y-2 border-y border-neutral-800 py-4 sm:grid-cols-3">
        {facts.map(([label, value]) => (
          <div key={label}>
            <dt className="text-xs tracking-[0.2em] text-neutral-500 uppercase">{label}</dt>
            <dd className="mt-0.5 text-sm text-neutral-200">{value}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-4 text-sm leading-relaxed text-neutral-400">{artifact.description}</p>
    </div>
  );
}
