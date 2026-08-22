import i18next from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./locales/en.json";
import ar from "./locales/ar.json";

export const LANG_STORAGE_KEY = "ruwi-lang";
export type Lang = "ar" | "en";

// The bootstrap script in index.html already resolved localStorage before
// first paint (same pattern as the theme bootstrap) and set
// document.documentElement.lang — read it back here rather than
// re-deriving from localStorage, so this never mismatches the attribute
// the page already painted with.
function getInitialLang(): Lang {
  return document.documentElement.lang === "en" ? "en" : "ar";
}

i18next.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    ar: { translation: ar },
  },
  lng: getInitialLang(),
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18next;
