interface StatusViewProps {
  title: string;
  detail?: string;
  tone?: "loading" | "error" | "empty";
}

export default function StatusView({ title, detail, tone = "empty" }: StatusViewProps) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 px-6 text-center">
      {tone === "loading" && (
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-neutral-700 border-t-amber-400" />
      )}
      {tone === "error" && (
        <div className="flex h-10 w-10 items-center justify-center rounded-full border border-red-900/60 bg-red-950/40 text-red-400">
          !
        </div>
      )}
      <p className="text-sm font-medium tracking-wide text-neutral-200">{title}</p>
      {detail && <p className="max-w-sm text-sm text-neutral-500">{detail}</p>}
    </div>
  );
}
