import { useTranslation } from "react-i18next";
import { useChat } from "./useChat";
import TtsCenterpiece from "../TtsCenterpiece";
import QuestionComposer from "../QuestionComposer";

export default function ChatPanel({
  artifactId,
  visitId,
}: {
  artifactId: number;
  visitId: string;
}) {
  const { t } = useTranslation();
  const {
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
  } = useChat(artifactId, visitId);

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-center text-xs tracking-[0.2em] text-text-muted uppercase">{t("chat.heading")}</h2>

      <TtsCenterpiece
        audioUrl={latest?.audioUrl ?? null}
        caption={latest?.answer ?? ""}
        onPlayingChange={setIsAudioPlaying}
        showText={showText}
        onToggleShowText={toggleShowText}
      />

      {latest?.hitIterationCap && (
        <p className="text-center text-xs text-text-muted">{t("chat.hitIterationCap")}</p>
      )}

      {pending && <p className="text-center text-sm text-text-muted">{t("chat.pending")}</p>}

      {error && (
        <p className="rounded-sm border border-error-border bg-error-bg px-3 py-2 text-center text-sm text-error-text">
          {error}
        </p>
      )}

      <QuestionComposer value={question} onChange={setQuestion} onSubmit={askQuestion} disabled={composerDisabled} />

      {history.length > 0 && (
        <div className="flex flex-col gap-4 border-t border-border pt-6">
          <h3 className="text-xs tracking-[0.2em] text-text-muted uppercase">{t("chat.previouslyAsked")}</h3>
          {history.map((exchange, i) => (
            <div key={i} className="flex flex-col gap-1.5">
              <p className="text-sm font-medium text-text">{exchange.question}</p>
              <p className="text-sm leading-relaxed text-text-muted">{exchange.answer}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
