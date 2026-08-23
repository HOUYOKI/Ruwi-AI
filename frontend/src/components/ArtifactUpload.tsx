import { useEffect, useRef, useState, type DragEvent } from "react";
import { ApiError, identifyArtifact } from "../api/apiClient";
import type { IdentificationResponse } from "../types/identification";
import { useTranslation } from "react-i18next";

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_BYTES = 8 * 1024 * 1024;

export default function ArtifactUpload({ onMatched }: { onMatched: (artifactId: number) => void }) {
  const { t } = useTranslation();
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
      setError(t("identify.invalidType"));
      return;
    }
    if (nextFile.size === 0) {
      setError(t("identify.emptyFile"));
      return;
    }
    if (nextFile.size > MAX_BYTES) {
      setError(t("identify.tooLarge"));
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
      setError(err instanceof ApiError && err.status !== 0 ? t("identify.analysisFailed") : t("identify.serverError"));
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
            dragging ? "border-gold bg-gold/10" : "border-border bg-surface/30"
          }`}
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full border border-gold/30 bg-gold/10 text-3xl text-gold">
            ◉
          </div>
          <h2 className="mt-6 font-display text-3xl text-text">{t("identify.uploadTitle")}</h2>
          <p className="mt-3 max-w-md text-base leading-7 text-text-muted">
            {t("identify.uploadInstructions")}
          </p>
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="mt-7 min-h-14 rounded-md bg-gold px-7 py-3 text-base font-semibold text-bg transition hover:opacity-90"
          >
            {t("identify.choosePhoto")}
          </button>
          <p className="mt-4 text-xs text-text-muted">{t("identify.fileRules")}</p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-border bg-surface/30">
          <div className="relative flex min-h-80 items-center justify-center bg-black p-4">
            <img src={previewUrl} alt={t("identify.previewAlt")} className="max-h-[55vh] w-full object-contain" />
          </div>
          <div className="flex flex-wrap items-center justify-between gap-4 border-t border-border p-5">
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-text">{file?.name}</p>
              <p className="mt-1 text-xs text-text-muted">{t("identify.ready")}</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                disabled={pending}
                onClick={reset}
                className="min-h-12 rounded-md border border-border px-5 py-2 text-sm text-text-muted hover:border-gold/40 disabled:opacity-50"
              >
                {t("identify.chooseAnother")}
              </button>
              <button
                type="button"
                disabled={pending}
                onClick={analyze}
                className="min-h-12 rounded-md bg-gold px-6 py-2 text-sm font-semibold text-bg hover:opacity-90 disabled:cursor-wait disabled:opacity-60"
              >
                {pending ? t("identify.analyzing") : t("identify.analyze")}
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-5 rounded-lg border border-error-border bg-error-bg p-5 text-error-text" role="alert">
          <p className="font-medium">{t("identify.matchFailed")}</p>
          <p className="mt-1 text-sm">{error}</p>
          <button type="button" onClick={reset} className="mt-4 min-h-11 rounded-md border border-error-border px-4 py-2 text-sm hover:bg-surface/40">
            {t("identify.tryAnother")}
          </button>
        </div>
      )}

      {result?.status === "partial" && (
        <section className="mt-7 rounded-xl border border-gold/25 bg-gold/[0.06] p-6 sm:p-8" aria-labelledby="possible-title">
          <p className="text-xs tracking-[0.22em] text-gold uppercase">{t("identify.possibleMatch")}</p>
          <h2 id="possible-title" className="mt-2 font-display text-3xl text-text">{t("identify.confirmMatch")}</h2>
          <p className="mt-3 text-sm leading-6 text-text-muted">{t("identify.partialReason")}</p>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {result.alternatives.map((candidate) => (
              <button
                key={candidate.artifact_id}
                type="button"
                onClick={() => onMatched(candidate.artifact_id)}
                className="min-h-20 rounded-lg border border-border bg-surface/60 p-5 text-start transition hover:border-gold/60"
              >
                <span className="block font-display text-xl text-text">{candidate.artifact_name}</span>
                <span className="mt-2 block text-xs text-text-muted">{t("identify.possibleMatch")} · {Math.round(candidate.confidence * 100)}%</span>
              </button>
            ))}
          </div>
          <button type="button" onClick={reset} className="mt-5 min-h-11 text-sm text-gold underline-offset-4 hover:underline">
            {t("identify.noneTryAgain")}
          </button>
        </section>
      )}

      {result?.status === "unsupported" && (
        <section className="mt-7 rounded-xl border border-border bg-surface/40 p-7 text-center" aria-labelledby="unsupported-title">
          <h2 id="unsupported-title" className="font-display text-3xl text-text">{t("identify.unsupportedTitle")}</h2>
          <p className="mx-auto mt-3 max-w-xl text-base leading-7 text-text-muted">{t("identify.unsupportedReason")}</p>
          <button type="button" onClick={reset} className="mt-6 min-h-12 rounded-md border border-gold/40 px-6 py-2 text-gold hover:bg-gold/10">
            {t("identify.tryAnother")}
          </button>
        </section>
      )}
    </div>
  );
}
