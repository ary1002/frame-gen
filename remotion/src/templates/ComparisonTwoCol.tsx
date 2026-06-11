import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { entrance, fadeUp, secToFrames } from "../anim";

interface Column { heading: string; points: string[]; }
interface Props {
  title: string;
  columns: Column[];
  background_color?: string;
  cues?: number[];
}

export const ComparisonTwoCol: React.FC<Props> = ({ title, columns, background_color = "#0f3460", cues }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleProgress = entrance(frame, fps, 0);
  const titleStyle = fadeUp(titleProgress, 24);

  // cues order: [col0_heading, col0_point0..., col1_heading, col1_point0..., ...]
  let cueIndex = 0;

  return (
    <div style={{
      width: "100%", height: "100%",
      backgroundColor: background_color,
      display: "flex", flexDirection: "column",
      padding: "60px 80px",
      boxSizing: "border-box",
      fontFamily: "sans-serif",
    }}>
      <h2 style={{
        color: "#ffffff", fontSize: 56, margin: "0 0 48px", textAlign: "center",
        ...titleStyle,
      }}>{title}</h2>
      <div style={{ display: "flex", flex: 1, gap: 40 }}>
        {columns.map((col, i) => {
          const headingDelay = cues && cues.length > cueIndex
            ? secToFrames(cues[cueIndex++], fps)
            : (cueIndex++ + 1) * 6;
          const headingProgress = entrance(frame, fps, headingDelay);
          const headingStyle = fadeUp(headingProgress, 28);

          return (
            <div key={i} style={{
              flex: 1,
              background: "rgba(255,255,255,0.05)",
              borderRadius: 16,
              padding: "40px 48px",
            }}>
              <h3 style={{
                color: "#aaccff", fontSize: 44, margin: "0 0 32px",
                ...headingStyle,
              }}>{col.heading}</h3>
              <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 20 }}>
                {col.points.map((p, j) => {
                  const pointDelay = cues && cues.length > cueIndex
                    ? secToFrames(cues[cueIndex++], fps)
                    : (cueIndex++ + 1) * 6;
                  const pointProgress = entrance(frame, fps, pointDelay);
                  const pointStyle = fadeUp(pointProgress, 24);
                  return (
                    <li key={j} style={{
                      color: "#e0e0ff", fontSize: 36,
                      display: "flex", gap: 16,
                      ...pointStyle,
                    }}>
                      <span style={{ color: "#6688ff" }}>▸</span> {p}
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
};
