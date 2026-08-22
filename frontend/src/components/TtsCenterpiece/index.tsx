import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useAudioVisualizer } from "../../hooks/useAudioVisualizer";
import PulseVisualizer from "./PulseVisualizer";
import PlayControls from "./PlayControls";

interface TtsCenterpieceProps {
  audioUrl: string | null;
  caption: string;
  onPlayingChange: (isPlaying: boolean) => void;
  showText: boolean;
  onToggleShowText: () => void;
}

export default function TtsCenterpiece({
  audioUrl,
  caption,
  onPlayingChange,
  showText,
  onToggleShowText,
}: TtsCenterpieceProps) {
  const { t } = useTranslation();
  const { audioRef, coreRef, glowRef, isPlaying, needsManualPlay, canReplay, play, audioEventHandlers } =
    useAudioVisualizer(audioUrl);

  useEffect(() => {
    onPlayingChange(isPlaying);
  }, [isPlaying, onPlayingChange]);

  const hasAnswer = Boolean(audioUrl || caption);
  const showIdlePrompt = !hasAnswer;

  return (
    <div className="flex flex-col items-center gap-3">
      <PulseVisualizer coreRef={coreRef} glowRef={glowRef} isPlaying={isPlaying} />

      <div className="flex max-w-md flex-col items-center gap-2 text-center">
        <p className="text-sm leading-relaxed text-text">
          {showIdlePrompt ? t("ttsCenterpiece.idlePrompt") : showText ? caption : ""}
        </p>
        <div className="flex items-center gap-3">
          <PlayControls needsManualPlay={needsManualPlay} canReplay={canReplay} isPlaying={isPlaying} onPlay={play} />
          {hasAnswer && (
            <button
              type="button"
              onClick={onToggleShowText}
              className="text-xs tracking-[0.15em] text-text-muted uppercase transition-colors hover:text-gold"
            >
              {showText ? t("chat.hideText") : t("chat.showText")}
            </button>
          )}
        </div>
      </div>

      <audio ref={audioRef} {...audioEventHandlers} className="hidden" />
    </div>
  );
}
