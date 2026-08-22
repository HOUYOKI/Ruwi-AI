import { useTranslation } from "react-i18next";
import { useLanguage } from "../hooks/useLanguage";

// Same neutral switch shape as ThemeToggle, placed beside it — a secondary
// control, not a themed surface.
export default function LanguageToggle() {
  const { t } = useTranslation();
  const { lang, toggle } = useLanguage();
  const isEnglish = lang === "en";

  return (
    <button
      type="button"
      role="switch"
      aria-checked={isEnglish}
      aria-label={t("languageToggle.ariaLabel")}
      onClick={toggle}
      className="flex min-h-9 items-center gap-2 rounded-full border border-border bg-surface px-3 py-2 text-[10px] tracking-[0.2em] text-text-muted uppercase transition-colors hover:text-text"
    >
      <span aria-hidden className="relative h-4 w-8 rounded-full bg-border">
        <span
          aria-hidden
          className={`absolute top-0.5 left-0 h-3 w-3 rounded-full bg-text transition-transform ${
            isEnglish ? "translate-x-[18px]" : "translate-x-0.5"
          }`}
        />
      </span>
      <span className="font-display">{isEnglish ? t("languageToggle.en") : t("languageToggle.ar")}</span>
    </button>
  );
}
