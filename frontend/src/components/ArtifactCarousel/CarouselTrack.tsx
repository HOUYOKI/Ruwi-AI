import ArtifactCard from "../ArtifactCard";
import type { ArtifactSummary } from "../../types/artifact";
import { getCarouselTransform, mod } from "../../utils/carouselMath";

const OFFSET_RANGE = 2;
const SETTLE_TRANSITION = "transform 420ms cubic-bezier(0.77, 0, 0.175, 1), opacity 420ms ease, filter 420ms ease";
// A touch of depth-of-field on the side cards - center stays perfectly
// sharp, each step out softens slightly further.
const BLUR_BY_ABS = [0, 1, 2] as const;
const offsets = Array.from({ length: OFFSET_RANGE * 2 + 1 }, (_, i) => i - OFFSET_RANGE);

interface CarouselTrackProps {
  artifacts: ArtifactSummary[];
  currentIndex: number;
  isNarrow: boolean;
}

// Virtualized on purpose: only these 5 slots (center +/- 2) ever mount,
// regardless of how many artifacts exist (102 today). Index arithmetic
// wraps with mod() so it's a true loop, not a clamped range.
export default function CarouselTrack({ artifacts, currentIndex, isNarrow }: CarouselTrackProps) {
  return (
    <>
      {offsets.map((offset) => {
        const artifact = artifacts[mod(currentIndex + offset, artifacts.length)];
        const { translateX, scale, rotateY, opacity, zIndex } = getCarouselTransform(offset, isNarrow);
        const blur = BLUR_BY_ABS[Math.abs(offset)];

        return (
          <div
            key={artifact.id}
            className="absolute top-1/2 left-1/2"
            style={{
              width: isNarrow ? 200 : 280,
              height: isNarrow ? 280 : 400,
              zIndex,
              opacity,
              filter: blur ? `blur(${blur}px)` : "none",
              transform: `translate(-50%, -50%) translateX(${translateX}px) rotateY(${rotateY}deg) scale(${scale})`,
              transition: SETTLE_TRANSITION,
            }}
          >
            <ArtifactCard artifact={artifact} priority={offset === 0} />
          </div>
        );
      })}
    </>
  );
}
