import { useEffect, useRef, useState } from "react";
import { streamChat, type ChatMessage } from "../api";

const SUGGESTIONS = [
  "오늘 일정 정리해줘",
  "이 코드 리뷰해줘",
  "여행 계획 도와줘",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = logRef.current;
    if (el && typeof el.scrollTo === "function") {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [messages, loading]);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed) return;
    setError(null);
    setMessages((m) => [
      ...m,
      { role: "user", message: trimmed },
      { role: "assistant", message: "" },
    ]);
    setInput("");
    setLoading(true);
    try {
      await streamChat(trimmed, {
        onDelta: (chunk) => {
          setMessages((m) => {
            const next = m.slice();
            const last = next[next.length - 1];
            if (last && last.role === "assistant") {
              next[next.length - 1] = { ...last, message: last.message + chunk };
            }
            return next;
          });
        },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setMessages((m) => {
        const last = m[m.length - 1];
        if (last && last.role === "assistant" && last.message === "") {
          return m.slice(0, -1);
        }
        return m;
      });
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    send(input);
  }

  const empty = messages.length === 0;

  return (
    <section
      aria-label="Chat"
      style={{
        display: "grid",
        gridTemplateRows: "auto 1fr auto",
        gap: "var(--space-md)",
        height: "100%",
        maxWidth: 860,
        margin: "0 auto",
      }}
    >
      <header>
        <h1>Chat</h1>
        <p style={{ margin: 0, color: "var(--text-muted)" }}>
          에이전트와 대화하세요.
        </p>
      </header>

      <div
        ref={logRef}
        role="log"
        aria-live="polite"
        className="card"
        style={{
          padding: "var(--space-lg)",
          overflow: "auto",
          display: "flex",
          flexDirection: "column",
          gap: "var(--space-md)",
        }}
      >
        {empty && (
          <div
            style={{
              display: "grid",
              placeItems: "center",
              gap: "var(--space-md)",
              padding: "var(--space-xl) 0",
              color: "var(--text-muted)",
              textAlign: "center",
            }}
          >
            <div
              aria-hidden
              style={{
                width: 56,
                height: 56,
                borderRadius: 16,
                background: "var(--primary-grad)",
                boxShadow: "var(--primary-glow)",
              }}
            />
            <div style={{ fontSize: 16, color: "var(--text)", fontWeight: 600 }}>
              무엇을 도와드릴까요?
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => send(s)}
                  style={{
                    background: "var(--surface-alt)",
                    color: "var(--text)",
                    border: "1px solid var(--border)",
                    fontWeight: 500,
                    padding: "8px 14px",
                    borderRadius: 999,
                    boxShadow: "none",
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => {
          const isLast = i === messages.length - 1;
          if (
            isLast &&
            loading &&
            m.role === "assistant" &&
            m.message === ""
          ) {
            return <TypingIndicator key={i} />;
          }
          return <MessageBubble key={i} message={m} streaming={isLast && loading} />;
        })}

        {error && (
          <div
            role="alert"
            style={{
              color: "var(--danger)",
              background: "rgba(255, 107, 129, 0.08)",
              border: "1px solid rgba(255, 107, 129, 0.3)",
              borderRadius: "var(--radius-sm)",
              padding: "10px 14px",
            }}
          >
            {error}
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="card"
        style={{
          display: "flex",
          gap: "var(--space-sm)",
          padding: 8,
          alignItems: "center",
        }}
      >
        <input
          aria-label="message"
          placeholder="메시지를 입력하세요…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          style={{ background: "transparent", border: "none", boxShadow: "none" }}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? "Sending…" : "Send"}
        </button>
      </form>
    </section>
  );
}

function MessageBubble({
  message,
  streaming,
}: {
  message: ChatMessage;
  streaming?: boolean;
}) {
  const isUser = message.role === "user";
  return (
    <div
      data-role={message.role}
      style={{
        display: "flex",
        gap: 10,
        alignItems: "flex-end",
        flexDirection: isUser ? "row-reverse" : "row",
        animation: "fade-in-up 0.18s ease",
      }}
    >
      <Avatar role={message.role} />
      <div
        style={{
          background: isUser ? "var(--primary-grad)" : "var(--surface-alt)",
          color: isUser ? "white" : "var(--text)",
          padding: "10px 14px",
          borderRadius: 16,
          borderBottomRightRadius: isUser ? 4 : 16,
          borderBottomLeftRadius: isUser ? 16 : 4,
          maxWidth: "78%",
          boxShadow: isUser ? "var(--primary-glow)" : "var(--shadow-sm)",
          lineHeight: 1.5,
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
        }}
      >
        {message.message}
        {streaming && !isUser && (
          <span
            aria-hidden
            style={{
              display: "inline-block",
              width: 8,
              height: 14,
              marginLeft: 4,
              verticalAlign: "-2px",
              background: "var(--text-muted)",
              borderRadius: 2,
              animation: "blink 1s infinite",
            }}
          />
        )}
      </div>
    </div>
  );
}

function Avatar({ role }: { role: ChatMessage["role"] }) {
  const isUser = role === "user";
  return (
    <div
      aria-label={isUser ? "User" : "Assistant"}
      title={isUser ? "User" : "Assistant"}
      style={{
        width: 30,
        height: 30,
        borderRadius: 10,
        flexShrink: 0,
        display: "grid",
        placeItems: "center",
        color: "white",
        background: isUser
          ? "linear-gradient(135deg, #4ade80, #22c55e)"
          : "var(--primary-grad)",
        boxShadow: "var(--shadow-sm)",
      }}
    >
      {isUser ? <UserIcon /> : <AssistantIcon />}
    </div>
  );
}

function UserIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" />
    </svg>
  );
}

function AssistantIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <rect x="4" y="7" width="16" height="12" rx="3" />
      <path d="M12 3v4" />
      <circle cx="9" cy="13" r="1.2" fill="currentColor" stroke="none" />
      <circle cx="15" cy="13" r="1.2" fill="currentColor" stroke="none" />
      <path d="M2 13h2M20 13h2" />
    </svg>
  );
}

function TypingIndicator() {
  const dot: React.CSSProperties = {
    width: 6,
    height: 6,
    borderRadius: "50%",
    background: "var(--text-muted)",
    display: "inline-block",
    animation: "blink 1.2s infinite both",
  };
  return (
    <div style={{ display: "flex", gap: 10, alignItems: "flex-end" }}>
      <Avatar role="assistant" />
      <div
        style={{
          background: "var(--surface-alt)",
          padding: "12px 14px",
          borderRadius: 16,
          borderBottomLeftRadius: 4,
          display: "inline-flex",
          gap: 4,
        }}
      >
        <span style={dot} />
        <span style={{ ...dot, animationDelay: "0.2s" }} />
        <span style={{ ...dot, animationDelay: "0.4s" }} />
      </div>
    </div>
  );
}
