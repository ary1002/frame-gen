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

  // When between words, find the last word that has started so the window
  // doesn't jump back to index 0 during inter-word gaps.
  const anchorIndex = activeIndex >= 0
    ? activeIndex
    : captions.word_timestamps.reduce(
        (last, wt, i) => (currentTime >= wt.start_s ? i : last),
        -1
      );

  // Show a window of ~7 words centered on anchor
  const windowSize = 7;
  const half = Math.floor(windowSize / 2);
  const start = Math.max(0, anchorIndex - half);
  const end = Math.min(captions.word_timestamps.length, start + windowSize);
  const windowWords = captions.word_timestamps.slice(start, end);

  if (anchorIndex < 0 || windowWords.length === 0) return null;

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
          const isActive = globalIndex === activeIndex && activeIndex >= 0;
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
