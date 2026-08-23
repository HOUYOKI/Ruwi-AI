import { useTranslation } from "react-i18next";
import { useTheme } from "../hooks/useTheme";

// Neutral switch, shape-matched to the app's angular language (rounded-sm,
// chamfered thumb corner) instead of a generic rounded-full pill switch —
// still undecorated with gold/chevron/shurfat, per the brief: this is a
// secondary control, not a themed surface.
export default function ThemeToggle() {
  const { t } = useTranslation();
  const { theme, toggle } = useTheme();
  const isLight = theme === "light";

  return (
    <button
      type="button"
      role="switch"
      aria-checked={isLight}
      aria-label={t("themeToggle.ariaLabel")}
      onClick={toggle}
      className="flex min-h-9 items-center gap-2 rounded-full border border-border bg-surface px-3 py-2 text-[10px] tracking-[0.2em] text-text-muted uppercase transition-colors hover:text-text"
    >
      <span aria-hidden className="relative h-4 w-8 rounded-full bg-border">
        <span
          aria-hidden
          className={`absolute top-0.5 left-0 h-3 w-3 rounded-full bg-text transition-transform ${
            isLight ? "translate-x-[18px]" : "translate-x-0.5"
          }`}
        />
      </span>
      <span className="font-display">{isLight ? t("themeToggle.light") : t("themeToggle.dark")}</span>
    </button>
  );
}
