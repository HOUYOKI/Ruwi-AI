import { useTranslation } from "react-i18next";

interface PlayControlsProps {
  needsManualPlay: boolean;
  canReplay: boolean;
  isPlaying: boolean;
  isPaused: boolean;
  onPlay: () => void;
  onPause: () => void;
}

export default function PlayControls({ needsManualPlay, canReplay, isPlaying, isPaused, onPlay, onPause }: PlayControlsProps) {
  const { t } = useTranslation();

  if (isPlaying) {
    return (
      <button type="button" onClick={onPause} aria-label={t("playControls.pause")} className="text-xs tracking-[0.15em] text-text-muted uppercase transition-colors hover:text-gold">
        Ⅱ {t("playControls.pause")}
      </button>
    );
  }

  if (isPaused) {
    return (
      <button type="button" onClick={onPlay} aria-label={t("playControls.resume")} className="text-xs tracking-[0.15em] text-text-muted uppercase transition-colors hover:text-gold">
        ▸ {t("playControls.resume")}
      </button>
    );
  }

  if (needsManualPlay) {
    return (
      <button
        type="button"
        onClick={onPlay}
        className="text-xs tracking-[0.15em] text-text-muted uppercase transition-colors hover:text-gold"
      >
        ▸ {t("playControls.play")}
      </button>
    );
  }

  if (canReplay && !isPlaying) {
    return (
      <button
        type="button"
        onClick={onPlay}
        className="text-xs tracking-[0.15em] text-text-muted uppercase transition-colors hover:text-gold"
      >
        ↻ {t("playControls.replay")}
      </button>
    );
  }

  return null;
}
