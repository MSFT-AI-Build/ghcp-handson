import { describe, expect, it, beforeEach } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import ChatPage from "../pages/ChatPage";
import { calls, setNextStreamPlan } from "../test/server";

beforeEach(() => {
  calls.length = 0;
});

const renderPage = () =>
  render(
    <MemoryRouter>
      <ChatPage />
    </MemoryRouter>
  );

describe("ChatPage", () => {
  it("sends a message and shows the assistant reply", async () => {
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText("메시지 입력"), "hello");
    await user.click(screen.getByRole("button", { name: "전송" }));

    expect(await screen.findByText(/echo:\s+hello/)).toBeInTheDocument();
    expect(calls).toHaveLength(1);
    expect(calls[0].url).toMatch(/\/api\/chat\/stream$/);
    expect(calls[0].body).toEqual({ message: "hello" });
  });

  it("disables send button when input is empty", () => {
    renderPage();
    expect(screen.getByRole("button", { name: "전송" })).toBeDisabled();
  });

  it("renders native and MCP tool events from the stream", async () => {
    const user = userEvent.setup();
    setNextStreamPlan([
      {
        kind: "tool",
        data: {
          name: "calculate",
          type: "native",
          arguments: { expression: "1+1" },
          result: "2",
        },
      },
      { kind: "delta", text: "answer is " },
      {
        kind: "tool",
        data: {
          name: "search",
          type: "mcp",
          server: "notion",
          arguments: { query: "agents" },
        },
      },
      { kind: "delta", text: "2" },
    ]);
    renderPage();

    await user.type(screen.getByLabelText("메시지 입력"), "calc");
    await user.click(screen.getByRole("button", { name: "전송" }));

    const events = await screen.findAllByTestId("tool-event");
    expect(events).toHaveLength(2);
    expect(within(events[0]).getByText(/Tool · calculate/)).toBeInTheDocument();
    expect(
      within(events[1]).getByText(/MCP · notion → search/)
    ).toBeInTheDocument();
    expect(await screen.findByText(/answer is\s*2/)).toBeInTheDocument();
  });

  it("toggles tool event arguments and result on click", async () => {
    const user = userEvent.setup();
    setNextStreamPlan([
      {
        kind: "tool",
        data: {
          name: "calculate",
          type: "native",
          arguments: { expression: "1+1" },
          result: "2",
        },
      },
      { kind: "delta", text: "done" },
    ]);
    renderPage();

    await user.type(screen.getByLabelText("메시지 입력"), "calc");
    await user.click(screen.getByRole("button", { name: "전송" }));

    const event = await screen.findByTestId("tool-event");
    // Collapsed by default
    expect(
      within(event).queryByTestId("tool-event-details")
    ).not.toBeInTheDocument();

    const toggle = within(event).getByRole("button", { name: /Tool · calculate/ });
    await user.click(toggle);

    const details = within(event).getByTestId("tool-event-details");
    expect(within(details).getByText(/expression/)).toBeInTheDocument();
    expect(within(details).getByText("2")).toBeInTheDocument();

    await user.click(toggle);
    expect(
      within(event).queryByTestId("tool-event-details")
    ).not.toBeInTheDocument();
  });
});
