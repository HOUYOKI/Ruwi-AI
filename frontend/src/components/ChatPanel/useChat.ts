import { useState } from "react";
import i18next from "../../i18n";
import { ApiError } from "../../api/apiClient";
import { askRuwi } from "../../api/chatApi";
import type { Exchange } from "../../types/chat";

export function useChat(artifactId: number) {
  const [question, setQuestion] = useState("");
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Real state off the <audio> element (play/pause/ended events inside
  // TtsCenterpiece), never a fake timer — this is what actually gates the
  // composer.
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);
  // Hidden by default so the audio answer isn't accompanied by an always-on
  // text dump — text must remain reachable (never audio-only), so this is
  // a one-click reveal next to the player, not a removal. Once
  // revealed it stays revealed for the rest of the visit, not per-question.
  const [showText, setShowText] = useState(false);

  const latest = exchanges[exchanges.length - 1] ?? null;
  const history = exchanges.slice(0, -1);
  const composerDisabled = pending || isAudioPlaying;

  async function askQuestion(trimmed: string) {
    if (!trimmed || composerDisabled) return;

    setPending(true);
    setError(null);
    try {
      const response = await askRuwi(artifactId, trimmed);
      setExchanges((prev) => [
        ...prev,
        {
          question: trimmed,
          answer: response.answer,
          hitIterationCap: response.hit_iteration_cap,
          audioUrl: response.audio_url,
        },
      ]);
      setQuestion("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : i18next.t("chat.fallbackError"));
    } finally {
      setPending(false);
    }
  }

  function toggleShowText() {
    setShowText((v) => !v);
  }

  return {
    question,
    setQuestion,
    latest,
    history,
    pending,
    error,
    composerDisabled,
    askQuestion,
    setIsAudioPlaying,
    showText,
    toggleShowText,
  };
}
