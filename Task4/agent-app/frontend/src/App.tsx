import { NavLink, Route, Routes, Navigate } from "react-router-dom";
import ChatPage from "./pages/ChatPage";
import AgentsPage from "./pages/AgentsPage";
import SettingsPage from "./pages/SettingsPage";

const shellStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  height: "100%",
};

const navStyle: React.CSSProperties = {
  position: "sticky",
  top: 0,
  zIndex: 10,
  display: "flex",
  alignItems: "center",
  gap: "var(--space-md)",
  padding: "14px var(--space-lg)",
  background: "rgba(15, 19, 32, 0.65)",
  backdropFilter: "blur(16px)",
  WebkitBackdropFilter: "blur(16px)",
  borderBottom: "1px solid var(--border)",
};

const brandStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
  marginRight: "var(--space-md)",
  fontWeight: 700,
  letterSpacing: "-0.01em",
};

const logoDot: React.CSSProperties = {
  width: 26,
  height: 26,
  borderRadius: 8,
  background: "var(--primary-grad)",
  boxShadow: "var(--primary-glow)",
};

const navLinks: { to: string; label: string }[] = [
  { to: "/chat", label: "Chat" },
  { to: "/agents", label: "Agents" },
  { to: "/settings", label: "Settings" },
];

const linkStyle = ({ isActive }: { isActive: boolean }): React.CSSProperties => ({
  color: isActive ? "var(--text)" : "var(--text-muted)",
  fontWeight: isActive ? 600 : 500,
  padding: "8px 14px",
  borderRadius: 999,
  background: isActive ? "rgba(108, 140, 255, 0.16)" : "transparent",
  border: isActive
    ? "1px solid rgba(108, 140, 255, 0.35)"
    : "1px solid transparent",
  transition: "background 0.15s ease, color 0.15s ease, border-color 0.15s ease",
});

export default function App() {
  return (
    <div style={shellStyle}>
      <nav style={navStyle} aria-label="primary">
        <div style={brandStyle}>
          <span style={logoDot} aria-hidden />
          <span>Agent System</span>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          {navLinks.map((l) => (
            <NavLink key={l.to} to={l.to} style={linkStyle}>
              {l.label}
            </NavLink>
          ))}
        </div>
        <div style={{ marginLeft: "auto", color: "var(--text-faint)", fontSize: 12 }}>
          v0.1.0
        </div>
      </nav>
      <main
        style={{
          flex: 1,
          overflow: "auto",
          padding: "var(--space-xl) var(--space-lg)",
        }}
      >
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  );
}
