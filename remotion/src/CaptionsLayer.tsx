import React from "react";
import { useCurrentFrame, useVideoConfig, AbsoluteFill } from "remotion";
import { CaptionConfig, WordTimestamp } from "./types";

interface Props { captions: CaptionConfig; }

export const CaptionsLayer: React.FC<Props> = ({ captions }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  const activeIndex = captions.word_timestamps.findIndex(
    (wt) => currentTime >= wt.start_s && currentTime < wt.end_s
  );

  // Show a window of ~7 words centered on active
  const windowSize = 7;
  const half = Math.floor(windowSize / 2);
  const start = Math.max(0, activeIndex - half);
  const end = Math.min(captions.word_timestamps.length, start + windowSize);
  const windowWords = captions.word_timestamps.slice(start, end);

  if (windowWords.length === 0) return null;

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", pointerEvents: "none" }}>
      <div style={{
        marginBottom: 60,
        background: "rgba(0,0,0,0.65)",
        borderRadius: 12,
        padding: "16px 32px",
        display: "flex",
        gap: 12,
        flexWrap: "wrap",
        justifyContent: "center",
        maxWidth: "80%",
      }}>
        {windowWords.map((wt, i) => {
          const globalIndex = start + i;
          const isActive = globalIndex === activeIndex;
          return (
            <span key={globalIndex} style={{
              fontSize: 52,
              fontFamily: "sans-serif",
              fontWeight: isActive ? "bold" : "normal",
              color: isActive ? captions.color_active : "#ffffff",
              transition: "color 0.1s",
            }}>
              {wt.word}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
