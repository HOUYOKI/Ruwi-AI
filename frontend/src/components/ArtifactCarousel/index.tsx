import { useEffect, useRef, useState, type WheelEvent } from "react";
import { useTranslation } from "react-i18next";
import type { ArtifactSummary } from "../../types/artifact";
import { useCarouselNavigation } from "../../hooks/useCarouselNavigation";
import { useDragSwipe } from "../../hooks/useDragSwipe";
import CarouselTrack from "./CarouselTrack";
import CarouselControls from "./CarouselControls";

// A mouse wheel/trackpad fires many small delta events per physical gesture; without a
// cooldown a single scroll would fire next()/prev() a dozen times over. This is a fixed
// per-gesture debounce, not a rate limit - simplest way to get "one wheel notch, one step."
const WHEEL_COOLDOWN_MS = 350;
const WHEEL_THRESHOLD = 10;

export default function ArtifactCarousel({ artifacts }: { artifacts: ArtifactSummary[] }) {
  const { t } = useTranslation();
  const { currentIndex, goTo, next, prev } = useCarouselNavigation(artifacts.length);
  const { handlePointerDown, handlePointerUp, handleClickCapture } = useDragSwipe((direction) =>
    goTo(direction === "left" ? 1 : -1),
  );
  const [isNarrow, setIsNarrow] = useState(() => typeof window !== "undefined" && window.innerWidth < 640);
  const wheelLockedRef = useRef(false);

  useEffect(() => {
    function handleResize() {
      setIsNarrow(window.innerWidth < 640);
    }
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  function handleWheel(e: WheelEvent<HTMLDivElement>) {
    const delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
    if (Math.abs(delta) < WHEEL_THRESHOLD || wheelLockedRef.current) return;
    wheelLockedRef.current = true;
    if (delta > 0) next();
    else prev();
    window.setTimeout(() => {
      wheelLockedRef.current = false;
    }, WHEEL_COOLDOWN_MS);
  }

  return (
    <div className="flex flex-col items-center gap-6">
      <div
        role="group"
        aria-label={t("carousel.groupLabel")}
        className="relative w-full touch-pan-y select-none"
        style={{ height: isNarrow ? 280 : 400, perspective: 1200 }}
        onPointerDown={handlePointerDown}
        onPointerUp={handlePointerUp}
        onClickCapture={handleClickCapture}
        onWheel={handleWheel}
      >
        <CarouselTrack artifacts={artifacts} currentIndex={currentIndex} isNarrow={isNarrow} />

        <button
          type="button"
          aria-label={t("carousel.previous")}
          onClick={prev}
          className="absolute top-1/2 left-0 z-[200] -translate-y-1/2 rounded-sm border border-white/10 px-3 py-4 text-lg text-white/80 backdrop-blur-md transition-[colors,transform] duration-150 ease-out hover:text-white active:scale-[0.97]"
          style={{ background: "color-mix(in srgb, var(--bg) 25%, transparent)" }}
        >
          &#8249;
        </button>
        <button
          type="button"
          aria-label={t("carousel.next")}
          onClick={next}
          className="absolute top-1/2 right-0 z-[200] -translate-y-1/2 rounded-sm border border-white/10 px-3 py-4 text-lg text-white/80 backdrop-blur-md transition-[colors,transform] duration-150 ease-out hover:text-white active:scale-[0.97]"
          style={{ background: "color-mix(in srgb, var(--bg) 25%, transparent)" }}
        >
          &#8250;
        </button>
      </div>

      <CarouselControls current={currentIndex + 1} total={artifacts.length} />
    </div>
  );
}
