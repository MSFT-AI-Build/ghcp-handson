import { useEffect, useState } from "react";
import {
  fetchAgents,
  fetchTools,
  type AgentInfo,
  type AgentsOverview,
  type McpServerInfo,
  type ToolSpec,
  type ToolsOverview,
} from "../api";

const pageStyle: React.CSSProperties = {
  maxWidth: 980,
  margin: "0 auto",
  display: "flex",
  flexDirection: "column",
  gap: "var(--space-xl)",
};

const sectionStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "var(--space-md)",
};

const gridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
  gap: "var(--space-md)",
};

const cardStyle: React.CSSProperties = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: "var(--radius-md)",
  padding: "var(--space-md)",
  display: "flex",
  flexDirection: "column",
  gap: 6,
  boxShadow: "var(--shadow-sm)",
};

const STATUS_COLOR: Record<string, string> = {
  active: "rgba(110, 231, 183, 0.18)",
  connected: "rgba(110, 231, 183, 0.18)",
  disconnected: "rgba(255, 255, 255, 0.08)",
  error: "rgba(255, 99, 99, 0.20)",
};

function badgeStyle(status: string): React.CSSProperties {
  return {
    display: "inline-block",
    padding: "2px 8px",
    borderRadius: 999,
    fontSize: 11,
    background: STATUS_COLOR[status] ?? "rgba(255,255,255,0.06)",
    border: "1px solid var(--border)",
    color: "var(--text)",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  };
}

function ToolCard({ tool }: { tool: ToolSpec }) {
  return (
    <div style={cardStyle} data-testid={`tool-${tool.name}`}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <strong>{tool.name}</strong>
        <span style={badgeStyle(tool.status)}>{tool.status}</span>
      </div>
      <div style={{ color: "var(--text-muted)", fontSize: 12 }}>{tool.type}</div>
      <p style={{ margin: 0, color: "var(--text-muted)", fontSize: 13 }}>
        {tool.description}
      </p>
    </div>
  );
}

function McpServerCard({ srv }: { srv: McpServerInfo }) {
  return (
    <div style={cardStyle} data-testid={`mcp-${srv.name}`}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <strong>{srv.name}</strong>
        <span style={badgeStyle(srv.status)}>{srv.status}</span>
      </div>
      <div style={{ color: "var(--text-muted)", fontSize: 12 }}>
        transport: {srv.transport}
      </div>
      {srv.tools.length > 0 ? (
        <ul style={{ margin: 0, paddingLeft: 18, color: "var(--text-muted)", fontSize: 13 }}>
          {srv.tools.map((t) => (
            <li key={t.name}>{t.name}</li>
          ))}
        </ul>
      ) : (
        <div style={{ color: "var(--text-faint)", fontSize: 12 }}>
          (no tools listed)
        </div>
      )}
    </div>
  );
}

export default function AgentsPage() {
  const [data, setData] = useState<ToolsOverview | null>(null);
  const [agents, setAgents] = useState<AgentsOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([fetchTools(), fetchAgents()])
      .then(([tools, ags]) => {
        if (!cancelled) {
          setData(tools);
          setAgents(ags);
        }
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div style={pageStyle}>
      <header>
        <h1 style={{ margin: 0, fontSize: 28 }}>Agents</h1>
        <p style={{ margin: "4px 0 0", color: "var(--text-muted)" }}>
          등록된 에이전트, 도구, MCP 서버 상태를 확인하세요.
        </p>
      </header>

      {error && (
        <div role="alert" style={{ color: "var(--danger, #ff7373)" }}>
          정보를 불러오지 못했습니다: {error}
        </div>
      )}

      {agents && (
        <section style={sectionStyle}>
          <h2 style={{ margin: 0, fontSize: 18 }}>Active Agents</h2>
          <div style={gridStyle}>
            <AgentCard agent={agents.supervisor} kind="supervisor" />
            {agents.workers.map((w) => (
              <AgentCard key={w.id} agent={w} kind="worker" />
            ))}
            {agents.workers.length === 0 && (
              <div
                data-testid="no-active-workers"
                style={{
                  color: "var(--text-faint)",
                  fontSize: 13,
                  border: "1px dashed var(--border)",
                  borderRadius: "var(--radius-md)",
                  padding: "var(--space-md)",
                }}
              >
                활성 Worker 가 없습니다. Chat 에서 작업을 위임하면 여기에 표시됩니다.
              </div>
            )}
          </div>
        </section>
      )}

      <section style={sectionStyle}>
        <h2 style={{ margin: 0, fontSize: 18 }}>Native Tools</h2>
        <div style={gridStyle}>
          {(data?.tools ?? []).map((t) => (
            <ToolCard key={t.name} tool={t} />
          ))}
        </div>
      </section>

      <section style={sectionStyle}>
        <h2 style={{ margin: 0, fontSize: 18 }}>MCP Servers</h2>
        <div style={gridStyle}>
          {(data?.mcp_servers ?? []).map((s) => (
            <McpServerCard key={s.name} srv={s} />
          ))}
        </div>
      </section>
    </div>
  );
}

function AgentCard({
  agent,
  kind,
}: {
  agent: AgentInfo;
  kind: "supervisor" | "worker";
}) {
  return (
    <div style={cardStyle} data-testid={`agent-${agent.id}`}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <strong>{agent.id}</strong>
        <span style={badgeStyle(kind === "supervisor" ? "active" : "connected")}>
          {kind}
        </span>
      </div>
      <div style={{ color: "var(--text-muted)", fontSize: 13 }}>{agent.role}</div>
      <div style={{ color: "var(--text-faint)", fontSize: 12 }}>
        work_dir: <code>{agent.work_dir}</code>
      </div>
      {agent.tools && agent.tools.length > 0 && (
        <div style={{ color: "var(--text-muted)", fontSize: 12 }}>
          tools: {agent.tools.join(", ")}
        </div>
      )}
    </div>
  );
}
