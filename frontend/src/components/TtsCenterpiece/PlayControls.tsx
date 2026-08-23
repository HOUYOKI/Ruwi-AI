import { useTranslation } from "react-i18next";

interface PlayControlsProps {
  needsManualPlay: boolean;
  canReplay: boolean;
  isPlaying: boolean;
  onPlay: () => void;
}

export default function PlayControls({ needsManualPlay, canReplay, isPlaying, onPlay }: PlayControlsProps) {
  const { t } = useTranslation();

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
