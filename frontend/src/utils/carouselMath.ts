export function mod(n: number, m: number): number {
  return ((n % m) + m) % m;
}

export interface CarouselTransform {
  translateX: number;
  scale: number;
  rotateY: number;
  opacity: number;
  zIndex: number;
}

// Coverflow arrangement values are not linear on purpose - matches the
// reference this was built from, where the outer step packs in tighter
// than a straight multiple of the inner one.
const SPACING_X = { wide: [0, 280, 440], narrow: [0, 160, 280] } as const;
// Side cards were shrinking to near-illegible slivers at the outer step (0.58x);
// bumped both steps up so they still read as recognizable, sized artifacts.
const SCALE_BY_ABS = [1, 0.85, 0.72] as const;
const ROTATE_Y_BY_ABS = [0, 22, 32] as const;
const OPACITY_BY_ABS = [1, 0.85, 0.6] as const;

export function getCarouselTransform(offset: number, isNarrow: boolean): CarouselTransform {
  const abs = Math.abs(offset);
  const sign = Math.sign(offset);
  const spacing = isNarrow ? SPACING_X.narrow : SPACING_X.wide;

  return {
    // `|| 0` normalizes -0 to 0 (Math.sign(0) is 0, but 0 * -1 is -0, and
    // -0 !== 0 under Object.is / toEqual, even though they render and
    // compare identically as numbers otherwise).
    translateX: sign * spacing[abs] || 0,
    scale: SCALE_BY_ABS[abs],
    rotateY: -sign * ROTATE_Y_BY_ABS[abs] || 0,
    opacity: OPACITY_BY_ABS[abs],
    zIndex: 100 - abs,
  };
}
