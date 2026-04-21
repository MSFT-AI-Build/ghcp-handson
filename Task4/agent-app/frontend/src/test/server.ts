import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

export const calls: { url: string; body: unknown }[] = [];

export type StreamPlanItem =
  | { kind: "delta"; text: string }
  | { kind: "tool"; data: Record<string, unknown> };

export type StreamPlan = StreamPlanItem[];

let nextStreamPlan: StreamPlan | null = null;

export function setNextStreamPlan(plan: StreamPlan | null): void {
  nextStreamPlan = plan;
}

function sseStream(items: StreamPlanItem[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      for (const item of items) {
        if (item.kind === "delta") {
          controller.enqueue(
            encoder.encode(
              `event: delta\ndata: ${JSON.stringify({ text: item.text })}\n\n`
            )
          );
        } else {
          controller.enqueue(
            encoder.encode(
              `event: tool\ndata: ${JSON.stringify(item.data)}\n\n`
            )
          );
        }
      }
      controller.enqueue(encoder.encode(`event: done\ndata: {}\n\n`));
      controller.close();
    },
  });
}

export const toolsResponse = {
  tools: [
    {
      name: "calculate",
      type: "native",
      description: "Evaluate basic arithmetic expressions safely.",
      status: "active",
    },
    {
      name: "mcp_list_tools",
      type: "native",
      description: "List tools exposed by a configured MCP server.",
      status: "active",
    },
    {
      name: "mcp_call_tool",
      type: "native",
      description: "Invoke a tool on a configured MCP server.",
      status: "active",
    },
  ],
  mcp_servers: [
    {
      name: "notion",
      transport: "stdio",
      command: "npx",
      args: ["-y", "@notionhq/notion-mcp-server"],
      status: "connected",
      tools: [{ name: "search", description: "search pages" }],
    },
    {
      name: "fileSystem",
      transport: "stdio",
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-filesystem", "./"],
      status: "disconnected",
      tools: [],
    },
    {
      name: "braveSearch",
      transport: "http",
      command: "npx",
      args: ["-y", "@brave/brave-search-mcp-server", "--transport", "http"],
      status: "error",
      tools: [],
    },
  ],
};

export const server = setupServer(
  http.post("*/api/chat/stream", async ({ request }) => {
    const body = (await request.json()) as { message?: string };
    calls.push({ url: request.url, body });
    const message = body?.message ?? "";
    const plan: StreamPlan =
      nextStreamPlan ??
      [
        { kind: "delta", text: "echo:" },
        { kind: "delta", text: " " },
        { kind: "delta", text: message },
      ];
    nextStreamPlan = null;
    return new HttpResponse(sseStream(plan), {
      status: 200,
      headers: { "content-type": "text/event-stream" },
    });
  }),
  http.post("*/api/chat", async ({ request }) => {
    const body = await request.json();
    calls.push({ url: request.url, body });
    const message = (body as { message?: string })?.message ?? "";
    return HttpResponse.json({ role: "assistant", message: `echo: ${message}` });
  }),
  http.get("*/api/tools", () => HttpResponse.json(toolsResponse))
);
