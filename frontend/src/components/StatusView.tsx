// StatusView.tsx
interface StatusViewProps {
  title: string;
  detail?: string;
  tone?: "loading" | "error" | "empty";
}

export default function StatusView({ title, detail, tone = "empty" }: StatusViewProps) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 px-6 text-center">
      {tone === "loading" && (
        <div className="flex w-full max-w-xs flex-col gap-3">
          <div className="shimmer h-4 w-2/3 self-center rounded-sm" />
          <div className="shimmer h-3 w-full rounded-sm" />
          <div className="shimmer h-3 w-5/6 self-center rounded-sm" />
        </div>
      )}
      {tone === "error" && (
        <div className="flex h-10 w-10 items-center justify-center rounded-full border border-error-border bg-error-bg text-error-text">
          !
        </div>
      )}
      <p className="text-sm font-medium tracking-wide text-text">{title}</p>
      {detail && <p className="max-w-sm text-sm text-text-muted">{detail}</p>}
    </div>
  );
}
