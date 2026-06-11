import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { entrance, fadeUp, scaleIn, secToFrames } from "../anim";

interface Props {
  title: string;
  eyebrow?: string;
  background_color?: string;
  cues?: number[];
}

export const TitleCard: React.FC<Props> = ({ title, eyebrow, background_color = "#1a1a2e", cues }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const eyebrowDelay = 0;
  const titleDelay = cues && cues.length > 0 ? secToFrames(cues[0], fps) : 8;

  const eyebrowProgress = entrance(frame, fps, eyebrowDelay);
  const titleProgress = entrance(frame, fps, titleDelay);

  const eyebrowStyle = fadeUp(eyebrowProgress, 30);
  const titleStyle = scaleIn(titleProgress, 0.94);

  return (
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
        <p style={{
          color: "#aaaacc", fontSize: 36, margin: "0 0 24px",
          textTransform: "uppercase", letterSpacing: 4,
          ...eyebrowStyle,
        }}>
          {eyebrow}
        </p>
      )}
      <h1 style={{
        color: "#ffffff", fontSize: 96, margin: 0,
        textAlign: "center", lineHeight: 1.15,
        ...titleStyle,
      }}>
        {title}
      </h1>
    </div>
  );
};
