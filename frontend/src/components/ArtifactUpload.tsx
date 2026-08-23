import { useEffect, useRef, useState, type DragEvent } from "react";
import { ApiError, identifyArtifact } from "../api/client";
import type { IdentificationResponse } from "../types/identification";

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_BYTES = 8 * 1024 * 1024;

export default function ArtifactUpload({ onMatched }: { onMatched: (artifactId: number) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<IdentificationResponse | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function chooseFile(nextFile: File | undefined) {
    setError(null);
    setResult(null);
    if (!nextFile) return;
    if (!ACCEPTED_TYPES.includes(nextFile.type)) {
      setError("Choose a JPEG, PNG, or WebP image.");
      return;
    }
    if (nextFile.size === 0) {
      setError("That image is empty. Please choose another one.");
      return;
    }
    if (nextFile.size > MAX_BYTES) {
      setError("Choose an image that is 8 MB or smaller.");
      return;
    }
    setFile(nextFile);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    chooseFile(event.dataTransfer.files[0]);
  }

  async function analyze() {
    if (!file || pending) return;
    setPending(true);
    setError(null);
    setResult(null);
    try {
      const response = await identifyArtifact(file);
      setResult(response);
      if (response.status === "matched" && response.artifact_id !== null) {
        onMatched(response.artifact_id);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Ruwi couldn't analyze this image. Please try again.");
    } finally {
      setPending(false);
    }
  }

  function reset() {
    setFile(null);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div className="mt-9">
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        capture="environment"
        className="sr-only"
        onChange={(event) => chooseFile(event.target.files?.[0])}
      />

      {!previewUrl ? (
        <div
          onDragEnter={(event) => { event.preventDefault(); setDragging(true); }}
          onDragOver={(event) => event.preventDefault()}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={`flex min-h-80 flex-col items-center justify-center rounded-xl border-2 border-dashed px-8 py-12 text-center transition ${
            dragging ? "border-amber-300 bg-amber-400/10" : "border-neutral-700 bg-neutral-900/30"
          }`}
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full border border-amber-400/30 bg-amber-400/10 text-3xl text-amber-200">
            ◉
          </div>
          <h2 className="mt-6 font-serif text-3xl text-neutral-50">Show Ruwi an artifact</h2>
          <p className="mt-3 max-w-md text-base leading-7 text-neutral-400">
            Take a clear photo or select an image. Ruwi will compare it only with supported showcase artifacts.
          </p>
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="mt-7 min-h-14 rounded-md bg-amber-300 px-7 py-3 text-base font-semibold text-neutral-950 transition hover:bg-amber-200"
          >
            Take photo or choose image
          </button>
          <p className="mt-4 text-xs text-neutral-600">JPEG, PNG or WebP · maximum 8 MB</p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-neutral-800 bg-neutral-900/30">
          <div className="relative flex min-h-80 items-center justify-center bg-black p-4">
            <img src={previewUrl} alt="Selected artifact preview" className="max-h-[55vh] w-full object-contain" />
          </div>
          <div className="flex flex-wrap items-center justify-between gap-4 border-t border-neutral-800 p-5">
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-neutral-200">{file?.name}</p>
              <p className="mt-1 text-xs text-neutral-500">Ready for comparison</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                disabled={pending}
                onClick={reset}
                className="min-h-12 rounded-md border border-neutral-700 px-5 py-2 text-sm text-neutral-300 hover:border-neutral-500 disabled:opacity-50"
              >
                Choose another
              </button>
              <button
                type="button"
                disabled={pending}
                onClick={analyze}
                className="min-h-12 rounded-md bg-amber-300 px-6 py-2 text-sm font-semibold text-neutral-950 hover:bg-amber-200 disabled:cursor-wait disabled:opacity-60"
              >
                {pending ? "Ruwi is looking…" : "Analyze artifact"}
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-5 rounded-lg border border-red-900/60 bg-red-950/30 p-5 text-red-300" role="alert">
          <p className="font-medium">We couldn't complete the match</p>
          <p className="mt-1 text-sm text-red-300/80">{error}</p>
          <button type="button" onClick={reset} className="mt-4 min-h-11 rounded-md border border-red-700/60 px-4 py-2 text-sm hover:bg-red-900/30">
            Try another image
          </button>
        </div>
      )}

      {result?.status === "partial" && (
        <section className="mt-7 rounded-xl border border-amber-400/25 bg-amber-400/[0.06] p-6 sm:p-8" aria-labelledby="possible-title">
          <p className="text-xs tracking-[0.22em] text-amber-300 uppercase">Possible match</p>
          <h2 id="possible-title" className="mt-2 font-serif text-3xl text-neutral-50">Does your artifact match one of these?</h2>
          <p className="mt-3 text-sm leading-6 text-neutral-400">{result.reason}</p>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {result.alternatives.map((candidate) => (
              <button
                key={candidate.artifact_id}
                type="button"
                onClick={() => onMatched(candidate.artifact_id)}
                className="min-h-20 rounded-lg border border-neutral-700 bg-neutral-950/60 p-5 text-left transition hover:border-amber-300/60"
              >
                <span className="block font-serif text-xl text-neutral-100">{candidate.artifact_name}</span>
                <span className="mt-2 block text-xs text-neutral-500">Possible match · {Math.round(candidate.confidence * 100)}%</span>
              </button>
            ))}
          </div>
          <button type="button" onClick={reset} className="mt-5 min-h-11 text-sm text-amber-200 underline-offset-4 hover:underline">
            None of these — try again
          </button>
        </section>
      )}

      {result?.status === "unsupported" && (
        <section className="mt-7 rounded-xl border border-neutral-700 bg-neutral-900/40 p-7 text-center" aria-labelledby="unsupported-title">
          <h2 id="unsupported-title" className="font-serif text-3xl text-neutral-50">No confident showcase match</h2>
          <p className="mx-auto mt-3 max-w-xl text-base leading-7 text-neutral-400">{result.reason}</p>
          <button type="button" onClick={reset} className="mt-6 min-h-12 rounded-md border border-amber-400/40 px-6 py-2 text-amber-200 hover:bg-amber-400/10">
            Try another image
          </button>
        </section>
      )}
    </div>
  );
}
