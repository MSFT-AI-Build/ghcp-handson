export const theme = {
  color: {
    bg: "#0f1115",
    surface: "#171a21",
    surfaceAlt: "#1f2330",
    border: "#2a2f3d",
    text: "#e6e8ee",
    textMuted: "#9aa3b2",
    primary: "#5b8cff",
    primaryHover: "#7aa2ff",
    danger: "#ff6b6b",
    success: "#4ade80",
  },
  space: { xs: "4px", sm: "8px", md: "16px", lg: "24px", xl: "32px" },
  radius: { sm: "6px", md: "10px", lg: "16px" },
  font: {
    family:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif',
    size: { sm: "13px", md: "14px", lg: "16px", xl: "20px" },
  },
  shadow: {
    sm: "0 1px 2px rgba(0,0,0,0.3)",
    md: "0 4px 12px rgba(0,0,0,0.35)",
  },
} as const;
