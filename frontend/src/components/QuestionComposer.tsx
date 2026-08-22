// QuestionComposer.tsx
import type { FormEvent } from "react";
import { useTranslation } from "react-i18next";

const QUESTION_MAX_LENGTH = 2000;

interface QuestionComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (question: string) => void;
  disabled: boolean;
}

export default function QuestionComposer({ value, onChange, onSubmit, disabled }: QuestionComposerProps) {
  const { t } = useTranslation();
  // Generic, not per-artifact — there's no backend-driven suggestion data yet.
  // FLAG (functional, not taste): these should eventually come from the
  // artifact record or the Narrator itself, so they're actually relevant to
  // what's on screen instead of always the same four prompts.
  const suggestions = t("composer.suggestions", { returnObjects: true }) as string[];

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
  }

  function handleSuggestion(suggestion: string) {
    if (disabled) return;
    onSubmit(suggestion);
  }

  return (
    <div className="flex flex-col gap-3">
      {/* Input + submit share one bordered box (focus ring on the box, not
          each piece) so they read as one integrated control, not a form
          field bolted to a separate button. */}
      <form
        onSubmit={handleSubmit}
        className="me-6 flex items-center rounded-sm border border-border bg-surface/60 pr-2 transition-colors focus-within:border-gold/50"
      >
        <input
          type="text"
          dir="auto"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          maxLength={QUESTION_MAX_LENGTH}
          placeholder={t("composer.placeholder")}
          className="min-h-11 flex-1 bg-transparent px-3 text-sm text-text placeholder:text-text-muted outline-none disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="rounded-sm bg-accent-red/10 px-3.5 py-1.5 text-sm font-medium text-accent-red transition-[colors,transform] duration-150 ease-out hover:bg-accent-red/20 active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-40 disabled:active:scale-100"
        >
          {t("composer.submit")}
        </button>
      </form>

      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => handleSuggestion(suggestion)}
            disabled={disabled}
            className="rounded-sm border border-border/60 bg-surface/60 px-3 py-1.5 text-xs text-text-muted transition-[colors,transform] duration-150 ease-out hover:border-gold/40 hover:text-text active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-40 disabled:active:scale-100"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
