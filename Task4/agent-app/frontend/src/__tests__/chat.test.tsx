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

  it("renders worker delegation status transitions", async () => {
    const user = userEvent.setup();
    const worker = {
      id: "worker-abc",
      role: "Researcher",
      task: "find latest news",
      instructions: "search and summarize",
    };
    setNextStreamPlan([
      { kind: "worker", data: { ...worker, status: "pending" } },
      { kind: "worker", data: { ...worker, status: "running" } },
      { kind: "delta", text: "결과를 정리했습니다." },
      {
        kind: "worker",
        data: { ...worker, status: "completed", result: "AI trends report" },
      },
    ]);
    renderPage();

    await user.type(screen.getByLabelText("메시지 입력"), "research");
    await user.click(screen.getByRole("button", { name: "전송" }));

    const card = await screen.findByTestId("worker-event");
    expect(within(card).getByText(/Worker · Researcher/)).toBeInTheDocument();
    expect(within(card).getByText(/find latest news/)).toBeInTheDocument();
    // Final status badge reflects completion (the same card was updated in place).
    expect(await within(card).findByText(/completed/i)).toBeInTheDocument();
    // Result is hidden behind toggle by default.
    expect(within(card).queryByTestId("worker-result")).not.toBeInTheDocument();
    // Click the toggle to reveal the result.
    await user.click(within(card).getByRole("button"));
    expect(within(card).getByTestId("worker-result")).toBeInTheDocument();
    expect(within(card).getByText(/AI trends report/)).toBeInTheDocument();
    // Only one worker card (id-based deduplication)
    expect(screen.getAllByTestId("worker-event")).toHaveLength(1);
  });

  it("renders worker tool events in arrival order", async () => {
    const user = userEvent.setup();
    const worker = {
      id: "worker-xyz",
      role: "Researcher",
      task: "search news",
      instructions: "search and summarize",
    };
    setNextStreamPlan([
      { kind: "worker", data: { ...worker, status: "pending" } },
      { kind: "worker", data: { ...worker, status: "running" } },
      {
        kind: "worker_tool",
        data: {
          type: "worker_tool",
          worker_id: "worker-xyz",
          worker_role: "Researcher",
          name: "search",
          server: "braveSearch",
          arguments: { query: "AI news" },
        },
      },
      {
        kind: "worker",
        data: { ...worker, status: "completed", result: "AI trends" },
      },
      { kind: "delta", text: "완료" },
    ]);
    renderPage();

    await user.type(screen.getByLabelText("메시지 입력"), "news");
    await user.click(screen.getByRole("button", { name: "전송" }));

    // Worker tool card should appear with correct label
    const workerToolCard = await screen.findByTestId("worker-tool-event");
    expect(
      within(workerToolCard).getByText(/Worker\(Researcher\) · MCP · braveSearch → search/)
    ).toBeInTheDocument();

    // Worker status card should still be present (updated in-place to completed)
    const workerCard = screen.getByTestId("worker-event");
    expect(within(workerCard).getByText(/completed/i)).toBeInTheDocument();

    // Order: worker card appears before worker_tool in the DOM
    const allCards = screen.getAllByTestId(/worker-event|worker-tool-event/);
    expect(allCards[0]).toHaveAttribute("data-testid", "worker-event");
    expect(allCards[1]).toHaveAttribute("data-testid", "worker-tool-event");
  });

  it("renders failed worker error message", async () => {
    const user = userEvent.setup();
    setNextStreamPlan([
      {
        kind: "worker",
        data: {
          id: "worker-bad",
          role: "Coder",
          task: "compile",
          instructions: "build",
          status: "failed",
          error: "compile error",
        },
      },
      { kind: "delta", text: "실패" },
    ]);
    renderPage();

    await user.type(screen.getByLabelText("메시지 입력"), "build");
    await user.click(screen.getByRole("button", { name: "전송" }));

    const card = await screen.findByTestId("worker-event");
    expect(within(card).getByText(/failed/i)).toBeInTheDocument();
    // Error is hidden behind toggle by default.
    expect(within(card).queryByTestId("worker-error")).not.toBeInTheDocument();
    // Click toggle to reveal the error.
    await user.click(within(card).getByRole("button"));
    expect(within(card).getByTestId("worker-error")).toBeInTheDocument();
    expect(within(card).getByText(/compile error/)).toBeInTheDocument();
  });
});
