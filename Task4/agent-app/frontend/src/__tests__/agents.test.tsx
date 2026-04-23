import { describe, expect, it } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import AgentsPage from "../pages/AgentsPage";
import { server } from "../test/server";

const renderPage = () =>
  render(
    <MemoryRouter>
      <AgentsPage />
    </MemoryRouter>
  );

describe("AgentsPage", () => {
  it("renders native tools and MCP server statuses", async () => {
    renderPage();

    await waitFor(() =>
      expect(screen.getByTestId("tool-calculate")).toBeInTheDocument()
    );

    expect(screen.getByTestId("tool-mcp_list_tools")).toBeInTheDocument();
    expect(screen.getByTestId("tool-mcp_call_tool")).toBeInTheDocument();

    const notion = screen.getByTestId("mcp-notion");
    expect(within(notion).getByText(/connected/i)).toBeInTheDocument();
    expect(within(notion).getByText("search")).toBeInTheDocument();

    const fs = screen.getByTestId("mcp-fileSystem");
    expect(within(fs).getByText(/disconnected/i)).toBeInTheDocument();

    const brave = screen.getByTestId("mcp-braveSearch");
    expect(within(brave).getByText(/error/i)).toBeInTheDocument();
  });

  it("renders the supervisor agent card and empty workers placeholder", async () => {
    renderPage();
    const supervisor = await screen.findByTestId("agent-supervisor");
    expect(within(supervisor).getByText("Supervisor Agent")).toBeInTheDocument();
    expect(within(supervisor).getByText(/delegate_task/)).toBeInTheDocument();
    expect(screen.getByTestId("no-active-workers")).toBeInTheDocument();
  });

  it("shows an error when the tools endpoint fails", async () => {
    server.use(
      http.get("*/api/tools", () =>
        HttpResponse.json({ detail: "boom" }, { status: 500 })
      )
    );
    renderPage();

    expect(await screen.findByRole("alert")).toHaveTextContent(/정보를 불러오지/);
  });
});
