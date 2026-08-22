import { useEffect, useState } from "react";

export type Theme = "light" | "dark";
const STORAGE_KEY = "ruwi-theme";

function getInitialTheme(): Theme {
  return document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
}

/**
 * Reads/writes the app's data-theme attribute + localStorage. The initial
 * value is read from the attribute rather than localStorage directly
 * because the bootstrap script in index.html already resolved
 * localStorage/prefers-color-scheme and set the attribute before this
 * component ever mounts — re-deriving it here would risk a mismatch.
 */
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // Storage unavailable (private mode, disabled) — theme still applies
      // for this session via the attribute, it just won't persist.
    }
  }, [theme]);

  function toggle() {
    setTheme((t) => (t === "light" ? "dark" : "light"));
  }

  return { theme, toggle };
}
