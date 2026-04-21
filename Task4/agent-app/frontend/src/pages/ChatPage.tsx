import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  sendChat,
  streamChat,
  type ToolEvent,
  type WorkerEvent,
  type WorkerToolEvent,
  type WorkerStatus,
} from "../api";

/** Unified stream event — preserves arrival order across tool/worker sources. */
type ChatEvent =
  | { kind: "tool"; seq: number; data: ToolEvent }
  | { kind: "worker"; seq: number; workerId: string; data: WorkerEvent }
  | { kind: "worker_tool"; seq: number; workerId: string; workerRole: string; data: WorkerToolEvent };

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  message: string;
  pending?: boolean;
  events?: ChatEvent[];
};

const pageStyle: React.CSSProperties = {
  maxWidth: 880,
  margin: "0 auto",
  display: "flex",
  flexDirection: "column",
  gap: "var(--space-lg)",
};

const headerStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 4,
};

const cardStyle: React.CSSProperties = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: "var(--radius-lg)",
  boxShadow: "var(--shadow-md)",
  padding: "var(--space-lg)",
  display: "flex",
  flexDirection: "column",
  gap: "var(--space-md)",
};

const listStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "var(--space-md)",
  maxHeight: 540,
  overflowY: "auto",
  paddingRight: 4,
};

const rowStyle = (role: "user" | "assistant"): React.CSSProperties => ({
  display: "flex",
  gap: 12,
  alignItems: "flex-start",
  flexDirection: role === "user" ? "row-reverse" : "row",
});

const avatarStyle = (role: "user" | "assistant"): React.CSSProperties => ({
  width: 32,
  height: 32,
  borderRadius: "50%",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background:
    role === "user" ? "var(--primary-grad)" : "rgba(255, 255, 255, 0.06)",
  border:
    role === "user"
      ? "1px solid rgba(108, 140, 255, 0.5)"
      : "1px solid var(--border)",
  color: "var(--text)",
  flexShrink: 0,
});

const bubbleStyle = (
  role: "user" | "assistant",
  pending: boolean
): React.CSSProperties => ({
  background:
    role === "user"
      ? "linear-gradient(135deg, rgba(108,140,255,0.20), rgba(140,108,255,0.18))"
      : "rgba(255,255,255,0.04)",
  border:
    role === "user"
      ? "1px solid rgba(108, 140, 255, 0.4)"
      : "1px solid var(--border)",
  borderRadius: 14,
  padding: "10px 14px",
  maxWidth: "70%",
  whiteSpace: "pre-wrap",
  color: "var(--text)",
  opacity: pending ? 0.6 : 1,
});

const toolCardStyle: React.CSSProperties = {
  display: "inline-flex",
  gap: 8,
  padding: "6px 8px",
  border: "1px dashed rgba(255, 200, 110, 0.45)",
  background: "rgba(255, 200, 110, 0.05)",
  borderRadius: 8,
  fontSize: 11.5,
  lineHeight: 1.35,
  alignItems: "flex-start",
  maxWidth: "100%",
};

const toolListStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 4,
  marginBottom: 6,
};

const workerToolCardStyle: React.CSSProperties = {
  display: "inline-flex",
  gap: 8,
  padding: "6px 8px",
  border: "1px dashed rgba(140, 200, 255, 0.35)",
  background: "rgba(140, 200, 255, 0.04)",
  borderRadius: 8,
  fontSize: 11.5,
  lineHeight: 1.35,
  alignItems: "flex-start",
  maxWidth: "100%",
  marginLeft: 14,
};

const workerCardStyle: React.CSSProperties = {
  display: "inline-flex",
  gap: 8,
  padding: "6px 10px",
  border: "1px dashed rgba(140, 200, 255, 0.45)",
  background: "rgba(140, 200, 255, 0.06)",
  borderRadius: 8,
  fontSize: 11.5,
  lineHeight: 1.4,
  alignItems: "flex-start",
  maxWidth: "100%",
};

const STATUS_BADGE: Record<WorkerStatus, React.CSSProperties> = {
  pending: { background: "rgba(255,255,255,0.08)", color: "var(--text-muted)" },
  running: { background: "rgba(140, 200, 255, 0.20)", color: "#a8d2ff" },
  completed: { background: "rgba(110, 231, 183, 0.20)", color: "#7eecb6" },
  failed: { background: "rgba(255, 99, 99, 0.20)", color: "#ff8c8c" },
  cancelled: { background: "rgba(255,255,255,0.08)", color: "var(--text-muted)" },
};

const inputRow: React.CSSProperties = {
  display: "flex",
  gap: "var(--space-sm)",
};

const inputStyle: React.CSSProperties = {
  flex: 1,
  background: "rgba(255,255,255,0.04)",
  border: "1px solid var(--border)",
  borderRadius: "var(--radius-md)",
  padding: "12px 14px",
  color: "var(--text)",
  fontFamily: "inherit",
  fontSize: 15,
};

const buttonStyle: React.CSSProperties = {
  background: "var(--primary-grad)",
  border: "none",
  borderRadius: "var(--radius-md)",
  color: "white",
  fontWeight: 600,
  padding: "0 18px",
  cursor: "pointer",
  boxShadow: "var(--primary-glow)",
};

function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" width={18} height={18} fill="none" aria-hidden>
      <circle cx="12" cy="8" r="4" stroke="white" strokeWidth="1.6" />
      <path
        d="M4 20c1.5-3.5 4.5-5 8-5s6.5 1.5 8 5"
        stroke="white"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

function AssistantIcon() {
  return (
    <svg viewBox="0 0 24 24" width={18} height={18} fill="none" aria-hidden>
      <rect x="3" y="6" width="18" height="13" rx="3" stroke="#8aa6ff" strokeWidth="1.6" />
      <circle cx="9" cy="12.5" r="1.4" fill="#8aa6ff" />
      <circle cx="15" cy="12.5" r="1.4" fill="#8aa6ff" />
      <path d="M12 3v3" stroke="#8aa6ff" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function WorkerToolIcon() {
  return (
    <svg viewBox="0 0 24 24" width={12} height={12} fill="none" aria-hidden style={{ flexShrink: 0, marginTop: 2 }}>
      <path
        d="M14.7 6.3a3 3 0 0 0-4 4L4 17v3h3l6.7-6.7a3 3 0 0 0 4-4l-2.3 2.3-2-2 2.3-2.3z"
        stroke="rgb(140, 200, 255)"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ToolIcon() {
  return (
    <svg viewBox="0 0 24 24" width={12} height={12} fill="none" aria-hidden style={{ flexShrink: 0, marginTop: 2 }}>
      <path
        d="M14.7 6.3a3 3 0 0 0-4 4L4 17v3h3l6.7-6.7a3 3 0 0 0 4-4l-2.3 2.3-2-2 2.3-2.3z"
        stroke="rgb(255,200,110)"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ToolCallCard({ event }: { event: ToolEvent }) {
  const title = event.server
    ? `MCP · ${event.server} → ${event.name}`
    : `Tool · ${event.name}`;
  const hasArgs =
    event.arguments !== undefined &&
    event.arguments !== null &&
    !(typeof event.arguments === "object" &&
      Object.keys(event.arguments as object).length === 0);
  const hasResult = event.result !== undefined && event.result !== null;
  const [open, setOpen] = useState(false);
  const canToggle = hasArgs || hasResult;
  return (
    <div style={toolCardStyle} data-testid="tool-event">
      <ToolIcon />
      <div style={{ flex: 1, minWidth: 0 }}>
        <button
          type="button"
          onClick={() => canToggle && setOpen((v) => !v)}
          aria-expanded={open}
          aria-label={`${title} 상세 ${open ? "접기" : "펼치기"}`}
          disabled={!canToggle}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 4,
            background: "transparent",
            border: "none",
            color: "var(--text)",
            font: "inherit",
            fontSize: "inherit",
            fontWeight: 600,
            padding: 0,
            cursor: canToggle ? "pointer" : "default",
          }}
        >
          {canToggle && (
            <span
              aria-hidden
              style={{
                display: "inline-block",
                fontSize: 9,
                transition: "transform 120ms ease",
                transform: open ? "rotate(90deg)" : "rotate(0deg)",
                color: "var(--text-muted)",
              }}
            >
              ▶
            </span>
          )}
          <span style={{ wordBreak: "break-word" }}>{title}</span>
        </button>
        {open && (
          <div
            data-testid="tool-event-details"
            style={{
              marginTop: 4,
              display: "flex",
              flexDirection: "column",
              gap: 2,
              color: "var(--text-muted)",
            }}
          >
            {hasArgs && (
              <div style={{ wordBreak: "break-word" }}>
                <span style={{ color: "var(--text-faint)" }}>args:</span>{" "}
                <code style={{ color: "var(--text)", fontSize: 11 }}>
                  {JSON.stringify(event.arguments)}
                </code>
              </div>
            )}
            {hasResult && (
              <div style={{ wordBreak: "break-word" }}>
                <span style={{ color: "var(--text-faint)" }}>result:</span>{" "}
                <code style={{ color: "var(--text)", fontSize: 11 }}>
                  {typeof event.result === "string"
                    ? event.result
                    : JSON.stringify(event.result)}
                </code>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

let nextId = 1;
const newId = () => `i${nextId++}`;

let _seq = 0;
const nextSeq = () => _seq++;

function WorkerToolCard({ workerRole, event }: { workerRole: string; event: WorkerToolEvent }) {
  const innerTitle = event.server
    ? `MCP · ${event.server} → ${event.name}`
    : `Tool · ${event.name}`;
  const title = `Worker(${workerRole}) · ${innerTitle}`;
  const hasArgs =
    event.arguments !== undefined &&
    event.arguments !== null &&
    !(typeof event.arguments === "object" &&
      Object.keys(event.arguments as object).length === 0);
  const hasResult = event.result !== undefined && event.result !== null;
  const [open, setOpen] = useState(false);
  const canToggle = hasArgs || hasResult;
  return (
    <div style={workerToolCardStyle} data-testid="worker-tool-event">
      <WorkerToolIcon />
      <div style={{ flex: 1, minWidth: 0 }}>
        <button
          type="button"
          onClick={() => canToggle && setOpen((v) => !v)}
          aria-expanded={open}
          aria-label={`${title} 상세 ${open ? "접기" : "펼치기"}`}
          disabled={!canToggle}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 4,
            background: "transparent",
            border: "none",
            color: "var(--text)",
            font: "inherit",
            fontSize: "inherit",
            fontWeight: 600,
            padding: 0,
            cursor: canToggle ? "pointer" : "default",
          }}
        >
          {canToggle && (
            <span
              aria-hidden
              style={{
                display: "inline-block",
                fontSize: 9,
                transition: "transform 120ms ease",
                transform: open ? "rotate(90deg)" : "rotate(0deg)",
                color: "var(--text-muted)",
              }}
            >
              ▶
            </span>
          )}
          <span style={{ wordBreak: "break-word" }}>{title}</span>
        </button>
        {open && (
          <div
            data-testid="worker-tool-event-details"
            style={{
              marginTop: 4,
              display: "flex",
              flexDirection: "column",
              gap: 2,
              color: "var(--text-muted)",
            }}
          >
            {hasArgs && (
              <div style={{ wordBreak: "break-word" }}>
                <span style={{ color: "var(--text-faint)" }}>args:</span>{" "}
                <code style={{ color: "var(--text)", fontSize: 11 }}>
                  {JSON.stringify(event.arguments)}
                </code>
              </div>
            )}
            {hasResult && (
              <div style={{ wordBreak: "break-word" }}>
                <span style={{ color: "var(--text-faint)" }}>result:</span>{" "}
                <code style={{ color: "var(--text)", fontSize: 11 }}>
                  {typeof event.result === "string"
                    ? event.result
                    : JSON.stringify(event.result)}
                </code>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function WorkerCard({ event }: { event: WorkerEvent }) {
  const hasDetail =
    (event.status === "completed" && !!event.result) ||
    (event.status === "failed" && !!event.error);
  const [open, setOpen] = useState(false);
  const badgeStyle: React.CSSProperties = {
    padding: "1px 6px",
    borderRadius: 6,
    fontSize: 10,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: 0.4,
    ...STATUS_BADGE[event.status],
  };
  return (
    <div style={workerCardStyle} data-testid="worker-event" data-worker-id={event.id}>
      <div style={{ display: "flex", flexDirection: "column", gap: 2, minWidth: 0 }}>
        <button
          type="button"
          onClick={() => hasDetail && setOpen((v) => !v)}
          aria-expanded={open}
          aria-label={`Worker · ${event.role} 상세 ${open ? "접기" : "펼치기"}`}
          disabled={!hasDetail}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            background: "transparent",
            border: "none",
            color: "var(--text)",
            font: "inherit",
            fontSize: "inherit",
            fontWeight: 600,
            padding: 0,
            cursor: hasDetail ? "pointer" : "default",
            textAlign: "left",
          }}
        >
          {hasDetail && (
            <span
              aria-hidden
              style={{
                display: "inline-block",
                fontSize: 9,
                transition: "transform 120ms ease",
                transform: open ? "rotate(90deg)" : "rotate(0deg)",
                color: "var(--text-muted)",
              }}
            >
              ▶
            </span>
          )}
          <span style={{ fontWeight: 600 }}>Worker · {event.role}</span>
          <span style={badgeStyle} data-testid="worker-status">
            {event.status}
          </span>
        </button>
        {event.task && (
          <div style={{ color: "var(--text-muted)", wordBreak: "break-word" }}>
            {event.task}
          </div>
        )}
        {open && event.status === "completed" && event.result && (
          <div
            data-testid="worker-result"
            style={{
              marginTop: 4,
              color: "var(--text-muted)",
              wordBreak: "break-word",
              whiteSpace: "pre-wrap",
              borderTop: "1px solid rgba(140, 200, 255, 0.15)",
              paddingTop: 6,
            }}
          >
            {event.result}
          </div>
        )}
        {open && event.status === "failed" && event.error && (
          <div
            data-testid="worker-error"
            style={{
              marginTop: 4,
              color: "#ff8c8c",
              wordBreak: "break-word",
              borderTop: "1px solid rgba(255, 99, 99, 0.2)",
              paddingTop: 6,
            }}
          >
            ✗ {event.error}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [items, setItems] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = listRef.current;
    if (el && typeof el.scrollTo === "function") {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [items]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const message = input.trim();
    if (!message || busy) return;
    setInput("");
    setError(null);
    setBusy(true);

    const userItem: ChatMessage = {
      id: newId(),
      role: "user",
      message,
    };
    const placeholder: ChatMessage = {
      id: newId(),
      role: "assistant",
      message: "",
      pending: true,
    };
    setItems((prev) => [...prev, userItem, placeholder]);

    try {
      let streamed = "";
      try {
        await streamChat(message, {
          onDelta: (chunk) => {
            streamed += chunk;
            setItems((prev) =>
              prev.map((it) =>
                it.id === placeholder.id ? { ...it, message: streamed } : it
              )
            );
          },
          onTool: (event) => {
            setItems((prev) =>
              prev.map((it) =>
                it.id !== placeholder.id
                  ? it
                  : { ...it, events: [...(it.events ?? []), { kind: "tool", seq: nextSeq(), data: event }] }
              )
            );
          },
          onWorker: (event) => {
            setItems((prev) =>
              prev.map((it) => {
                if (it.id !== placeholder.id) return it;
                const events = it.events ?? [];
                const idx = events.findIndex(
                  (e) => e.kind === "worker" && e.workerId === event.id
                );
                if (idx >= 0) {
                  // Update existing worker card in-place (preserving position).
                  const updated = [...events];
                  updated[idx] = { ...updated[idx], data: event } as ChatEvent;
                  return { ...it, events: updated };
                }
                return {
                  ...it,
                  events: [
                    ...events,
                    { kind: "worker", seq: nextSeq(), workerId: event.id, data: event },
                  ],
                };
              })
            );
          },
          onWorkerTool: (event) => {
            setItems((prev) =>
              prev.map((it) =>
                it.id !== placeholder.id
                  ? it
                  : {
                      ...it,
                      events: [
                        ...(it.events ?? []),
                        {
                          kind: "worker_tool",
                          seq: nextSeq(),
                          workerId: event.worker_id,
                          workerRole: event.worker_role ?? "",
                          data: event,
                        },
                      ],
                    }
              )
            );
          },
        });
        setItems((prev) =>
          prev.map((it) =>
            it.id === placeholder.id
              ? { ...it, pending: false, message: streamed || "(no response)" }
              : it
          )
        );
      } catch {
        const reply = await sendChat(message);
        setItems((prev) =>
          prev.map((it) =>
            it.id === placeholder.id
              ? { ...it, pending: false, message: reply.message }
              : it
          )
        );
      }
    } catch (err) {
      setError((err as Error).message);
      setItems((prev) => prev.filter((it) => it.id !== placeholder.id));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={pageStyle}>
      <header style={headerStyle}>
        <h1 style={{ margin: 0, fontSize: 28 }}>Chat</h1>
        <p style={{ margin: 0, color: "var(--text-muted)" }}>
          에이전트와 대화하세요.
        </p>
      </header>

      <section style={cardStyle}>
        <div ref={listRef} style={listStyle}>
          {items.length === 0 && (
            <div style={{ color: "var(--text-faint)", textAlign: "center", padding: "30px 0" }}>
              메시지를 입력해 대화를 시작해 보세요.
            </div>
          )}
          {items.map((it) => (
            <div key={it.id} style={rowStyle(it.role)}>
              <div style={avatarStyle(it.role)} aria-label={it.role}>
                {it.role === "user" ? <UserIcon /> : <AssistantIcon />}
              </div>
              <div style={bubbleStyle(it.role, !!it.pending)}>
                {it.role === "assistant" && it.events && it.events.length > 0 && (
                  <div style={toolListStyle}>
                    {it.events.map((evt) => {
                      if (evt.kind === "tool") {
                        return <ToolCallCard key={`t-${evt.seq}`} event={evt.data} />;
                      }
                      if (evt.kind === "worker") {
                        return <WorkerCard key={`w-${evt.workerId}`} event={evt.data} />;
                      }
                      return (
                        <WorkerToolCard
                          key={`wt-${evt.seq}`}
                          workerRole={evt.workerRole}
                          event={evt.data}
                        />
                      );
                    })}
                  </div>
                )}
                {it.role === "assistant" ? (
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => (
                        <span style={{ whiteSpace: "pre-wrap" }}>{children}</span>
                      ),
                      strong: ({ children }) => (
                        <strong style={{ color: "var(--text)", fontWeight: 700 }}>{children}</strong>
                      ),
                    }}
                  >
                    {it.message || (it.pending ? "..." : "")}
                  </ReactMarkdown>
                ) : (
                  it.message || ""
                )}
              </div>
            </div>
          ))}
        </div>

        {error && (
          <div role="alert" style={{ color: "var(--danger, #ff7373)" }}>
            {error}
          </div>
        )}

        <form style={inputRow} onSubmit={onSubmit}>
          <input
            aria-label="메시지 입력"
            style={inputStyle}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="에이전트에게 질문해 보세요"
            disabled={busy}
          />
          <button type="submit" style={buttonStyle} disabled={busy || !input.trim()}>
            전송
          </button>
        </form>
      </section>
    </div>
  );
}
