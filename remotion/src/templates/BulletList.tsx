import React from "react";

interface Props {
  title: string;
  points: string[];
  background_color?: string;
}

export const BulletList: React.FC<Props> = ({ title, points, background_color = "#16213e" }) => (
  <div style={{
    width: "100%", height: "100%",
    backgroundColor: background_color,
    display: "flex", flexDirection: "column",
    padding: "80px 120px",
    boxSizing: "border-box",
    fontFamily: "sans-serif",
  }}>
    <h2 style={{ color: "#ffffff", fontSize: 64, margin: "0 0 60px", borderBottom: "3px solid #4444aa", paddingBottom: 24 }}>
      {title}
    </h2>
    <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 32 }}>
      {points.map((p, i) => (
        <li key={i} style={{ color: "#e0e0ff", fontSize: 48, display: "flex", alignItems: "flex-start", gap: 20 }}>
          <span style={{ color: "#8888ff", fontWeight: "bold", minWidth: 32 }}>•</span>
          {p}
        </li>
      ))}
    </ul>
  </div>
);
