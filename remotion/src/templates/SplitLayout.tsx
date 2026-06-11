import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { entrance, fadeUp, secToFrames } from "../anim";

interface Props {
  title: string;
  body: string;
  eyebrow?: string;
  background_color?: string;
  cues?: number[];
}

export const SplitLayout: React.FC<Props> = ({ title, body, eyebrow, background_color = "#1a1a2e", cues }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleDelay = 0;
  const bodyDelay = cues && cues.length > 1
    ? secToFrames(cues[1], fps)
    : cues && cues.length > 0
    ? secToFrames(cues[0], fps)
    : 10;

  const titleProgress = entrance(frame, fps, titleDelay);
  const bodyProgress = entrance(frame, fps, bodyDelay);

  const titleStyle = fadeUp(titleProgress, 28);
  const bodyStyle = fadeUp(bodyProgress, 36);

  return (
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
        {eyebrow && (
          <p style={{
            color: "#8888cc", fontSize: 32, margin: "0 0 16px",
            textTransform: "uppercase", letterSpacing: 3,
            ...fadeUp(titleProgress, 20),
          }}>{eyebrow}</p>
        )}
        <h2 style={{
          color: "#ffffff", fontSize: 72, margin: 0, lineHeight: 1.2,
          ...titleStyle,
        }}>{title}</h2>
      </div>
      <div style={{
        flex: 1, display: "flex", alignItems: "center",
        padding: "80px 80px 80px 60px",
      }}>
        <p style={{
          color: "#ccccee", fontSize: 42, lineHeight: 1.6, margin: 0,
          ...bodyStyle,
        }}>{body}</p>
      </div>
    </div>
  );
};
