import { useRef, type MouseEvent, type PointerEvent } from "react";

const SWIPE_THRESHOLD = 50;

/**
 * Stateless drag/click disambiguation for a horizontally-swipeable
 * element. A single ref holds where THIS gesture's pointerdown started,
 * always overwritten unconditionally on every pointerdown - never gated
 * behind "is a drag already in progress".
 *
 * That gate is exactly what broke this the first time: it left a stale
 * start position stuck forever whenever a pointerdown had no matching
 * pointerup (pointer leaves the window, a touch gets cancelled by the
 * OS, or - as confirmed while debugging this - a browser-automation
 * harness's own drag simulation that never fires a pointerup at all).
 * Every plain tap after that computed its delta against that stale,
 * far-away point, read as a giant drag: it re-triggered onSwipe AND set
 * a "just dragged" flag that then suppressed that same click, and every
 * click after, since nothing ever cleared it. Root cause was the
 * persistent boolean latch, not any one handler, so the fix removes the
 * latch rather than patching around it: suppression is computed fresh,
 * per click, from that click's own release coordinates against where
 * its gesture started, so there's nothing that can get stuck.
 */
export function useDragSwipe(onSwipe: (direction: "left" | "right") => void) {
  const lastDownXRef = useRef<number | null>(null);

  function handlePointerDown(e: PointerEvent) {
    lastDownXRef.current = e.clientX;
  }

  function handlePointerUp(e: PointerEvent) {
    const startX = lastDownXRef.current;
    if (startX === null) return;
    const delta = e.clientX - startX;
    if (Math.abs(delta) > SWIPE_THRESHOLD) {
      onSwipe(delta < 0 ? "left" : "right");
    }
  }

  // A real swipe shouldn't also fire the card's own <Link> navigation.
  function handleClickCapture(e: MouseEvent) {
    const startX = lastDownXRef.current;
    if (startX === null) return;
    if (Math.abs(e.clientX - startX) > SWIPE_THRESHOLD) {
      e.preventDefault();
      e.stopPropagation();
    }
  }

  return { handlePointerDown, handlePointerUp, handleClickCapture };
}
