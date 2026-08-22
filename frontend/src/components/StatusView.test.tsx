import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import StatusView from "./StatusView";

describe("StatusView", () => {
  it("renders a shimmering skeleton for the loading tone, not a spinner", () => {
    const { container } = render(<StatusView tone="loading" title="Loading…" />);
    const shimmerBars = container.querySelectorAll(".shimmer");
    expect(shimmerBars.length).toBeGreaterThan(0);
    expect(container.querySelector(".animate-spin")).not.toBeInTheDocument();
  });

  it("renders the error icon and detail text for the error tone", () => {
    render(<StatusView tone="error" title="Couldn't load" detail="Try again later." />);
    expect(screen.getByText("Couldn't load")).toBeInTheDocument();
    expect(screen.getByText("Try again later.")).toBeInTheDocument();
  });
});
