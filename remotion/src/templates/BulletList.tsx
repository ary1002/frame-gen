import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { entrance, fadeUp, scaleIn, secToFrames } from "../anim";

interface Props {
  title: string;
  points: string[];
  background_color?: string;
  cues?: number[];
}

export const BulletList: React.FC<Props> = ({ title, points, background_color = "#16213e", cues }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleProgress = entrance(frame, fps, 0);
  const titleStyle = fadeUp(titleProgress, 24);

  return (
    <div style={{
      width: "100%", height: "100%",
      backgroundColor: background_color,
      display: "flex", flexDirection: "column",
      padding: "80px 120px",
      boxSizing: "border-box",
      fontFamily: "sans-serif",
    }}>
      <h2 style={{
        color: "#ffffff", fontSize: 64, margin: "0 0 60px",
        borderBottom: "3px solid #4444aa", paddingBottom: 24,
        ...titleStyle,
      }}>
        {title}
      </h2>
      <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 32 }}>
        {points.map((p, i) => {
          const delayFrames = cues && cues.length > i
            ? secToFrames(cues[i], fps)
            : (i + 1) * 6;
          const progress = entrance(frame, fps, delayFrames);
          const itemStyle = fadeUp(progress, 36);
          const markerScale = scaleIn(progress, 0.5);
          return (
            <li key={i} style={{
              color: "#e0e0ff", fontSize: 48,
              display: "flex", alignItems: "flex-start", gap: 20,
              ...itemStyle,
            }}>
              <span style={{
                color: "#8888ff", fontWeight: "bold", minWidth: 32,
                display: "inline-block",
                ...markerScale,
              }}>•</span>
              {p}
            </li>
          );
        })}
      </ul>
    </div>
  );
};
