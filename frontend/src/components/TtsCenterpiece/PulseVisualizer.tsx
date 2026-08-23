import type { RefObject } from "react";

const CORE_REST = 0.55;
const GLOW_REST = 0.8;

interface PulseVisualizerProps {
  coreRef: RefObject<HTMLDivElement | null>;
  glowRef: RefObject<HTMLDivElement | null>;
  isPlaying: boolean;
}

// Narrow, explicit exception to the app's angular language (shurfat/
// chevron/ThemeToggle stay angular) - this one element goes circular/
// glowing per direct instruction. Still --gold, still real Web Audio
// amplitude (see useAudioVisualizer), still direct-DOM transform/opacity
// mutation only (no layout properties) for the 60fps-updating scale.
export default function PulseVisualizer({ coreRef, glowRef, isPlaying }: PulseVisualizerProps) {
  return (
    <div
      className={`relative flex aspect-square w-full max-w-xs items-center justify-center sm:max-w-sm ${
        isPlaying ? "" : "motion-safe:animate-[tts-breathe_4.5s_ease-in-out_infinite]"
      }`}
    >
      <div
        ref={glowRef}
        aria-hidden
        className="absolute inset-0 rounded-full"
        style={{
          background: "radial-gradient(circle, color-mix(in srgb, var(--gold) 70%, transparent) 0%, transparent 70%)",
          filter: "blur(18px)",
          transform: `scale(${GLOW_REST})`,
          opacity: 0.6,
        }}
      />
      <div
        ref={coreRef}
        aria-hidden
        className="relative h-[60%] w-[60%] rounded-full"
        style={{
          background:
            "radial-gradient(circle at 35% 30%, color-mix(in srgb, var(--gold) 85%, white) 0%, var(--gold) 45%, color-mix(in srgb, var(--gold) 55%, var(--bg)) 100%)",
          boxShadow: "0 0 30px color-mix(in srgb, var(--gold) 45%, transparent)",
          transform: `scale(${CORE_REST})`,
        }}
      />
    </div>
  );
}
