import { describe, expect, it } from "vitest";
import { getCarouselTransform, mod } from "./carouselMath";

describe("mod", () => {
  it("wraps a positive index within range unchanged", () => {
    expect(mod(3, 10)).toBe(3);
  });

  it("wraps a negative index to the end (true loop, not clamped)", () => {
    expect(mod(-1, 102)).toBe(101);
  });

  it("wraps an index past the end back to the start", () => {
    expect(mod(102, 102)).toBe(0);
  });

  it("survives a full loop back to the same index", () => {
    expect(mod(1 - 2, 102)).toBe(101);
  });
});

describe("getCarouselTransform", () => {
  it("returns an untransformed, fully opaque, topmost slot for offset 0", () => {
    const t = getCarouselTransform(0, false);
    expect(t).toEqual({ translateX: 0, scale: 1, rotateY: 0, opacity: 1, zIndex: 100 });
  });

  it("tilts left and right symmetrically for equal-magnitude offsets", () => {
    const left = getCarouselTransform(-1, false);
    const right = getCarouselTransform(1, false);
    expect(left.rotateY).toBe(-right.rotateY);
    expect(left.translateX).toBe(-right.translateX);
    expect(left.scale).toBe(right.scale);
    expect(left.opacity).toBe(right.opacity);
  });

  it("scales and fades down further at each step outward", () => {
    const near = getCarouselTransform(1, false);
    const far = getCarouselTransform(2, false);
    expect(far.scale).toBeLessThan(near.scale);
    expect(far.opacity).toBeLessThan(near.opacity);
    expect(far.zIndex).toBeLessThan(near.zIndex);
  });

  it("uses tighter spacing on narrow viewports", () => {
    const wide = getCarouselTransform(1, false);
    const narrow = getCarouselTransform(1, true);
    expect(Math.abs(narrow.translateX)).toBeLessThan(Math.abs(wide.translateX));
  });
});
