import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>
  );
}

describe("routing", () => {
  it("renders Chat page at /chat", () => {
    renderAt("/chat");
    expect(screen.getByRole("heading", { name: /chat/i })).toBeInTheDocument();
  });

  it("renders Agents page at /agents", () => {
    renderAt("/agents");
    expect(screen.getByRole("heading", { name: /agents/i })).toBeInTheDocument();
  });

  it("renders Settings page at /settings", () => {
    renderAt("/settings");
    expect(screen.getByRole("heading", { name: /settings/i })).toBeInTheDocument();
  });

  it("redirects / to /chat", () => {
    renderAt("/");
    expect(screen.getByRole("heading", { name: /chat/i })).toBeInTheDocument();
  });
});
