// ArtifactImageViewer.tsx
import { useEffect, useRef, useState, type WheelEvent } from "react";
import { useTranslation } from "react-i18next";
import { useCroppedArtifactImage } from "../hooks/useCroppedArtifactImage";

const MIN_SCALE = 1;
const MAX_SCALE = 3;
const SCALE_STEP = 0.25;
// Caps how tall the frame can get for a narrow/portrait-cropped artifact (e.g. a tall cup)
// so it doesn't dominate the layout the way a landscape-cropped one wouldn't. The frame's
// width is derived from this via the aspect ratio, not fixed, so wide artifacts still get
// the full column width and short artifacts still get their full aspect-correct height.
const MAX_FRAME_HEIGHT_PX = 400;

function clampScale(scale: number): number {
  return Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale));
}

function touchDistance(touches: TouchList): number {
  const a = touches[0];
  const b = touches[1];
  return Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
}

export default function ArtifactImageViewer({ imageUrl, alt }: { imageUrl: string; alt: string }) {
  const { t } = useTranslation();
  const [scale, setScale] = useState(MIN_SCALE);
  // Some artifact PNGs have large transparent margins around the actual photo, so the
  // displayed image is auto-cropped to its real content (see the hook's own comment for
  // why), and the frame is sized to that cropped result's aspect ratio, not the raw file's.
  const { src: displaySrc, aspect } = useCroppedArtifactImage(imageUrl);
  const containerRef = useRef<HTMLDivElement>(null);
  const pinchRef = useRef<{ startDistance: number; startScale: number } | null>(null);

  // Pinch-to-zoom needs a non-passive touchmove listener to preventDefault
  // (stops the browser's own page-pinch-zoom from fighting this) — React's
  // JSX onTouchMove is passive by default and can't do that.
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    function handleTouchStart(e: TouchEvent) {
      if (e.touches.length === 2) {
        pinchRef.current = { startDistance: touchDistance(e.touches), startScale: scale };
      }
    }

    function handleTouchMove(e: TouchEvent) {
      if (e.touches.length === 2 && pinchRef.current) {
        e.preventDefault();
        const ratio = touchDistance(e.touches) / pinchRef.current.startDistance;
        setScale(clampScale(pinchRef.current.startScale * ratio));
      }
    }

    function handleTouchEnd(e: TouchEvent) {
      if (e.touches.length < 2) pinchRef.current = null;
    }

    container.addEventListener("touchstart", handleTouchStart, { passive: true });
    container.addEventListener("touchmove", handleTouchMove, { passive: false });
    container.addEventListener("touchend", handleTouchEnd);
    container.addEventListener("touchcancel", handleTouchEnd);

    return () => {
      container.removeEventListener("touchstart", handleTouchStart);
      container.removeEventListener("touchmove", handleTouchMove);
      container.removeEventListener("touchend", handleTouchEnd);
      container.removeEventListener("touchcancel", handleTouchEnd);
    };
  }, [scale]);

  function handleWheel(e: WheelEvent<HTMLDivElement>) {
    e.preventDefault();
    setScale((prev) => clampScale(prev + (e.deltaY < 0 ? SCALE_STEP : -SCALE_STEP)));
  }

  return (
    <div className="mx-auto flex max-w-sm flex-col gap-1.5">
      <div
        ref={containerRef}
        onWheel={handleWheel}
        style={{
          touchAction: "none",
          aspectRatio: aspect,
          width: `min(100%, ${MAX_FRAME_HEIGHT_PX * aspect}px)`,
          background: "linear-gradient(180deg, color-mix(in srgb, var(--surface) 100%, white 5%), var(--surface))",
        }}
        className="elevated-frame mx-auto overflow-hidden rounded-sm border border-border"
      >
        <img
          src={displaySrc}
          alt={alt}
          fetchPriority="high"
          draggable={false}
          className="h-full w-full object-contain p-4 transition-transform duration-150 ease-out"
          style={{ transform: `scale(${scale})` }}
        />
      </div>
      <div className="flex items-center justify-center gap-2">
        <button
          type="button"
          aria-label={t("imageViewer.zoomOut")}
          onClick={() => setScale((prev) => clampScale(prev - SCALE_STEP))}
          disabled={scale <= MIN_SCALE}
          className="rounded-sm border border-border/60 bg-surface px-2 py-0.5 text-xs text-text-muted transition-[colors,transform] duration-150 ease-out hover:text-text active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-40 disabled:active:scale-100"
        >
          −
        </button>
        <span className="w-8 text-center text-xs text-text-muted tabular-nums">{Math.round(scale * 100)}%</span>
        <button
          type="button"
          aria-label={t("imageViewer.zoomIn")}
          onClick={() => setScale((prev) => clampScale(prev + SCALE_STEP))}
          disabled={scale >= MAX_SCALE}
          className="rounded-sm border border-border/60 bg-surface px-2 py-0.5 text-xs text-text-muted transition-[colors,transform] duration-150 ease-out hover:text-text active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-40 disabled:active:scale-100"
        >
          +
        </button>
      </div>
    </div>
  );
}
