import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

export const calls: { url: string; body: unknown }[] = [];

function sseStream(message: string): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  const chunks = [`echo:`, ` `, message];
  return new ReadableStream({
    start(controller) {
      for (const c of chunks) {
        controller.enqueue(
          encoder.encode(`event: delta\ndata: ${JSON.stringify({ text: c })}\n\n`)
        );
      }
      controller.enqueue(encoder.encode(`event: done\ndata: {}\n\n`));
      controller.close();
    },
  });
}

export const server = setupServer(
  http.post("*/api/chat/stream", async ({ request }) => {
    const body = (await request.json()) as { message?: string };
    calls.push({ url: request.url, body });
    return new HttpResponse(sseStream(body?.message ?? ""), {
      status: 200,
      headers: { "content-type": "text/event-stream" },
    });
  }),
  http.post("*/api/chat", async ({ request }) => {
    const body = await request.json();
    calls.push({ url: request.url, body });
    const message = (body as { message?: string })?.message ?? "";
    return HttpResponse.json({ role: "assistant", message: `echo: ${message}` });
  })
);
