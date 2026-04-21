const STORAGE_KEY = "agent-app.settings";

export type AppSettings = {
  apiBase: string;
};

export function loadSettings(): AppSettings | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as AppSettings;
    if (!parsed.apiBase) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function saveSettings(s: AppSettings): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
}

export function clearSettings(): void {
  localStorage.removeItem(STORAGE_KEY);
}
