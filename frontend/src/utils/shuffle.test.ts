import { describe, expect, it } from "vitest";
import { shuffle } from "./shuffle";

describe("shuffle", () => {
  it("returns a new array containing exactly the same elements", () => {
    const input = [1, 2, 3, 4, 5];
    const result = shuffle(input);
    expect(result).not.toBe(input);
    expect(result.length).toBe(input.length);
    expect([...result].sort()).toEqual([...input].sort());
  });

  it("does not mutate the input array", () => {
    const input = [1, 2, 3, 4, 5];
    const copy = [...input];
    shuffle(input);
    expect(input).toEqual(copy);
  });

  it("leaves a single-element array unchanged", () => {
    expect(shuffle([1])).toEqual([1]);
  });

  it("leaves an empty array unchanged", () => {
    expect(shuffle([])).toEqual([]);
  });
});
