import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import ArtifactCard from "./ArtifactCard";
import type { ArtifactSummary } from "../types/artifact";

const artifact: ArtifactSummary = {
  id: 1,
  name: "Ancient Human Finger Bone",
  age: "85,000 BCE",
  location: "Tell Al-Ghada, Tayma, Tabuk Region",
  material: "Fossilized Bone",
  image_url: "/images/1.png",
};

function renderCard(priority = false) {
  return render(
    <MemoryRouter>
      <ArtifactCard artifact={artifact} priority={priority} />
    </MemoryRouter>,
  );
}

describe("ArtifactCard", () => {
  it("shows only the image (name stays as accessible alt text, not visible), linking to its detail route", () => {
    renderCard();
    expect(screen.queryByText(artifact.name)).not.toBeInTheDocument();
    expect(screen.queryByText(artifact.age)).not.toBeInTheDocument();
    expect(screen.getByRole("img", { name: artifact.name })).toBeInTheDocument();
    expect(screen.getByRole("link")).toHaveAttribute("href", "/artifacts/1");
  });

  it("loads eagerly at high priority only when asked (the carousel's center slot)", () => {
    renderCard(true);
    const img = screen.getByRole("img");
    expect(img).toHaveAttribute("loading", "eager");
    expect(img.getAttribute("fetchpriority")).toBe("high");
  });

  it("defaults to lazy, auto-priority loading", () => {
    renderCard(false);
    const img = screen.getByRole("img");
    expect(img).toHaveAttribute("loading", "lazy");
    expect(img.getAttribute("fetchpriority")).toBe("auto");
  });

  it("matches its last-known rendered structure", () => {
    const { container } = renderCard();
    expect(container).toMatchSnapshot();
  });
});
