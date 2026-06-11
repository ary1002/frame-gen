import React from "react";

interface Props {
  title: string;
  eyebrow?: string;
  background_color?: string;
}

export const TitleCard: React.FC<Props> = ({ title, eyebrow, background_color = "#1a1a2e" }) => (
  <div style={{
    width: "100%", height: "100%",
    backgroundColor: background_color,
    display: "flex", flexDirection: "column",
    alignItems: "center", justifyContent: "center",
    padding: "80px",
    boxSizing: "border-box",
    fontFamily: "sans-serif",
  }}>
    {eyebrow && (
      <p style={{ color: "#aaaacc", fontSize: 36, margin: "0 0 24px", textTransform: "uppercase", letterSpacing: 4 }}>
        {eyebrow}
      </p>
    )}
    <h1 style={{ color: "#ffffff", fontSize: 96, margin: 0, textAlign: "center", lineHeight: 1.15 }}>
      {title}
    </h1>
  </div>
);
