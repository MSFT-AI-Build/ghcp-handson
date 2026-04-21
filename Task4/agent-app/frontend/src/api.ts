import { loadSettings } from "./settings";

export type ChatMessage = { role: "user" | "assistant"; message: string };

export const DEFAULT_API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? "http://localhost:8000";

export function resolveApiBase(): string {
  return loadSettings()?.apiBase ?? DEFAULT_API_BASE;
}

export async function sendChat(message: string): Promise<ChatMessage> {
  const base = resolveApiBase();
  const res = await fetch(`${base}/api/chat`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`Chat request failed (${res.status}): ${detail}`);
  }
  return (await res.json()) as ChatMessage;
}

export type StreamHandlers = {
  onDelta: (text: string) => void;
  onDone?: () => void;
  signal?: AbortSignal;
};

export async function streamChat(
  message: string,
  { onDelta, onDone, signal }: StreamHandlers
): Promise<void> {
  const base = resolveApiBase();
  const res = await fetch(`${base}/api/chat/stream`, {
    method: "POST",
    headers: { "content-type": "application/json", accept: "text/event-stream" },
    body: JSON.stringify({ message }),
    signal,
  });
  if (!res.ok || !res.body) {
    const detail = await res.text().catch(() => "");
    throw new Error(`Chat stream failed (${res.status}): ${detail}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let idx: number;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const raw = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const evt = parseSseEvent(raw);
      if (!evt) continue;
      if (evt.event === "delta" && typeof evt.data?.text === "string") {
        onDelta(evt.data.text);
      } else if (evt.event === "error") {
        throw new Error(evt.data?.detail ?? "stream error");
      } else if (evt.event === "done") {
        onDone?.();
        return;
      }
    }
  }
  onDone?.();
}

function parseSseEvent(
  raw: string
): { event: string; data: any } | null {
  let event = "message";
  const dataLines: string[] = [];
  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }
  if (dataLines.length === 0) return null;
  const dataStr = dataLines.join("\n");
  try {
    return { event, data: JSON.parse(dataStr) };
  } catch {
    return { event, data: { text: dataStr } };
  }
}
