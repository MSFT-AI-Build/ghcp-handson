import { describe, expect, it, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import ChatPage from "../pages/ChatPage";
import { calls } from "../test/server";

beforeEach(() => {
  calls.length = 0;
});

describe("ChatPage", () => {
  it("sends a message and shows the assistant reply", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ChatPage />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText(/message/i), "hello");
    await user.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText(/echo:\s+hello/)).toBeInTheDocument();
    expect(screen.getByText("hello")).toBeInTheDocument();
    expect(calls).toHaveLength(1);
    expect(calls[0].url).toMatch(/\/api\/chat\/stream$/);
    expect(calls[0].body).toEqual({ message: "hello" });
  });

  it("disables send button when input is empty", () => {
    render(
      <MemoryRouter>
        <ChatPage />
      </MemoryRouter>
    );
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });
});
