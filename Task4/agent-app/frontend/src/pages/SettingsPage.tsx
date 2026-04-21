import { useEffect, useState } from "react";
import { loadSettings, saveSettings, clearSettings } from "../settings";
import { DEFAULT_API_BASE } from "../api";

export default function SettingsPage() {
  const [apiBase, setApiBase] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const s = loadSettings();
    if (s) setApiBase(s.apiBase);
  }, []);

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!apiBase.trim()) return;
    saveSettings({ apiBase: apiBase.trim() });
    setSaved(true);
  }

  function handleClear() {
    clearSettings();
    setApiBase("");
    setSaved(false);
  }

  return (
    <section aria-label="Settings" style={{ maxWidth: 640, margin: "0 auto" }}>
      <header style={{ marginBottom: "var(--space-lg)" }}>
        <h1>Settings</h1>
        <p style={{ margin: 0, color: "var(--text-muted)" }}>
          백엔드 연결 정보를 관리합니다.
        </p>
      </header>

      <form
        onSubmit={handleSave}
        className="card"
        style={{
          display: "grid",
          gap: "var(--space-md)",
          padding: "var(--space-lg)",
        }}
      >
        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ fontWeight: 600 }}>API base URL</span>
          <span style={{ color: "var(--text-faint)", fontSize: 12 }}>
            기본값: <code>{DEFAULT_API_BASE}</code>
          </span>
          <input
            aria-label="api-base"
            placeholder={DEFAULT_API_BASE}
            value={apiBase}
            onChange={(e) => {
              setApiBase(e.target.value);
              setSaved(false);
            }}
          />
        </label>

        <div
          style={{
            display: "flex",
            gap: "var(--space-sm)",
            alignItems: "center",
          }}
        >
          <button type="submit" disabled={!apiBase.trim()}>
            Save
          </button>
          <button
            type="button"
            onClick={handleClear}
            style={{
              background: "transparent",
              color: "var(--text-muted)",
              border: "1px solid var(--border)",
              boxShadow: "none",
            }}
          >
            Clear
          </button>
          {saved && (
            <span
              role="status"
              style={{
                marginLeft: "auto",
                color: "var(--success)",
                fontSize: 13,
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <span
                aria-hidden
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: "var(--success)",
                  boxShadow: "0 0 10px rgba(74,222,128,0.6)",
                }}
              />
              Settings saved.
            </span>
          )}
        </div>
      </form>
    </section>
  );
}
