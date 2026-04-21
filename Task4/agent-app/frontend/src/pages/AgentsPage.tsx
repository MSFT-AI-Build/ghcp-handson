type AgentInfo = {
  name: string;
  role: string;
  description: string;
  tag: string;
  color: string;
};

const AGENTS: AgentInfo[] = [
  {
    name: "supervisor",
    role: "Coordinator",
    description: "Routes user requests and orchestrates the right specialist.",
    tag: "active",
    color: "linear-gradient(135deg, #6c8cff, #a479ff)",
  },
];

export default function AgentsPage() {
  return (
    <section aria-label="Agents" style={{ maxWidth: 960, margin: "0 auto" }}>
      <header style={{ marginBottom: "var(--space-lg)" }}>
        <h1>Agents</h1>
        <p style={{ margin: 0, color: "var(--text-muted)" }}>
          시스템에 등록된 에이전트 목록입니다.
        </p>
      </header>

      <ul
        style={{
          listStyle: "none",
          padding: 0,
          margin: 0,
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
          gap: "var(--space-md)",
        }}
      >
        {AGENTS.map((a) => (
          <li
            key={a.name}
            className="card"
            style={{
              padding: "var(--space-lg)",
              display: "grid",
              gap: "var(--space-md)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div
                aria-hidden
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 12,
                  background: a.color,
                  boxShadow: "var(--shadow-sm)",
                }}
              />
              <div>
                <div style={{ fontWeight: 650, fontSize: 15 }}>{a.name}</div>
                <div style={{ color: "var(--text-muted)", fontSize: 12 }}>
                  {a.role}
                </div>
              </div>
              <span
                style={{
                  marginLeft: "auto",
                  fontSize: 11,
                  padding: "3px 8px",
                  borderRadius: 999,
                  background: "rgba(74, 222, 128, 0.12)",
                  color: "var(--success)",
                  border: "1px solid rgba(74, 222, 128, 0.3)",
                }}
              >
                {a.tag}
              </span>
            </div>
            <p style={{ margin: 0, color: "var(--text-muted)", lineHeight: 1.5 }}>
              {a.description}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
