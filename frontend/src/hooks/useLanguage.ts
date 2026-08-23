import { useEffect, useState } from "react";
import i18next from "../i18n";
import type { Lang } from "../i18n";

const STORAGE_KEY = "ruwi-lang";

function getInitialLang(): Lang {
  return document.documentElement.lang === "en" ? "en" : "ar";
}

/**
 * Reads/writes the app's html lang attribute + localStorage, and keeps
 * i18next's active language in sync. Mirrors useTheme.ts: the initial value
 * is read from the attribute (already resolved by index.html's bootstrap
 * script before mount) rather than localStorage directly, to avoid a
 * mismatch.
 *
 * Keeps language and writing direction on the document root in sync.
 */
export function useLanguage() {
  const [lang, setLang] = useState<Lang>(getInitialLang);

  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    i18next.changeLanguage(lang);
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      // Storage unavailable (private mode, disabled) — language still
      // applies for this session via the attribute, it just won't persist.
    }
  }, [lang]);

  function toggle() {
    setLang((l) => (l === "ar" ? "en" : "ar"));
  }

  return { lang, toggle };
}
