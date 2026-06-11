import React from "react";

interface Props {
  title: string;
  body: string;
  eyebrow?: string;
  background_color?: string;
}

export const SplitLayout: React.FC<Props> = ({ title, body, eyebrow, background_color = "#1a1a2e" }) => (
  <div style={{
    width: "100%", height: "100%",
    backgroundColor: background_color,
    display: "flex",
    fontFamily: "sans-serif",
  }}>
    <div style={{
      flex: 1, display: "flex", flexDirection: "column",
      justifyContent: "center", padding: "80px 60px 80px 80px",
      borderRight: "2px solid rgba(255,255,255,0.1)",
    }}>
      {eyebrow && <p style={{ color: "#8888cc", fontSize: 32, margin: "0 0 16px", textTransform: "uppercase", letterSpacing: 3 }}>{eyebrow}</p>}
      <h2 style={{ color: "#ffffff", fontSize: 72, margin: 0, lineHeight: 1.2 }}>{title}</h2>
    </div>
    <div style={{
      flex: 1, display: "flex", alignItems: "center",
      padding: "80px 80px 80px 60px",
    }}>
      <p style={{ color: "#ccccee", fontSize: 42, lineHeight: 1.6, margin: 0 }}>{body}</p>
    </div>
  </div>
);
