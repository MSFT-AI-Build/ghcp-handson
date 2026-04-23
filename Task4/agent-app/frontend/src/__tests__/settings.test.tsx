import { describe, expect, it, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import SettingsPage from "../pages/SettingsPage";
import ChatPage from "../pages/ChatPage";
import { calls } from "../test/server";

beforeEach(() => {
  calls.length = 0;
});

describe("Settings -> Chat integration", () => {
  it("uses the saved API base URL on chat requests", async () => {
    const user = userEvent.setup();

    const { unmount } = render(
      <MemoryRouter>
        <SettingsPage />
      </MemoryRouter>
    );
    await user.type(screen.getByLabelText(/api-base/i), "http://example.test");
    await user.click(screen.getByRole("button", { name: /^save$/i }));
    expect(screen.getByRole("status")).toHaveTextContent(/saved/i);
    unmount();

    render(
      <MemoryRouter>
        <ChatPage />
      </MemoryRouter>
    );
    await user.type(screen.getByLabelText("메시지 입력"), "ping");
    await user.click(screen.getByRole("button", { name: "전송" }));

    expect(await screen.findByText(/echo:\s+ping/)).toBeInTheDocument();
    expect(calls).toHaveLength(1);
    expect(calls[0].url).toBe("http://example.test/api/chat/stream");
  });
});
