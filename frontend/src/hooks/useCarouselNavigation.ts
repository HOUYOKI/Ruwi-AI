import { useEffect, useState } from "react";
import { mod } from "../utils/carouselMath";

export function useCarouselNavigation(total: number) {
  const [currentIndex, setCurrentIndex] = useState(0);

  function goTo(delta: number) {
    setCurrentIndex((i) => mod(i + delta, total));
  }

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "ArrowRight") goTo(1);
      else if (e.key === "ArrowLeft") goTo(-1);
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [total]);

  return { currentIndex, goTo, next: () => goTo(1), prev: () => goTo(-1) };
}
