import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, AbsoluteFill } from "remotion";
import { SlideEntry } from "./types";
import { TitleCard } from "./templates/TitleCard";
import { BulletList } from "./templates/BulletList";
import { ComparisonTwoCol } from "./templates/ComparisonTwoCol";
import { SplitLayout } from "./templates/SplitLayout";

function renderTemplate(layout: SlideEntry["layout"]) {
  const p = layout.props as any;
  switch (layout.template) {
    case "title_card": return <TitleCard {...p} />;
    case "bullet_list": return <BulletList {...p} />;
    case "comparison_two_col": return <ComparisonTwoCol {...p} />;
    case "split_layout": return <SplitLayout {...p} />;
    default: return <TitleCard title="Unknown template" />;
  }
}

interface Props { data: SlideEntry; }

export const SlideWithEffect: React.FC<Props> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const duration = data.duration_frames;
  const effect = data.layout.effect;

  let style: React.CSSProperties = { width: "100%", height: "100%" };

  if (effect.type === "zoom") {
    const scale = interpolate(frame, [0, duration], [effect.from, effect.to], { extrapolateRight: "clamp" });
    style = { ...style, transform: `scale(${scale})`, transformOrigin: "center center" };
  } else if (effect.type === "blur") {
    const blur = interpolate(frame, [0, duration], [effect.from, effect.to], { extrapolateRight: "clamp" });
    style = { ...style, filter: `blur(${blur}px)` };
  } else if (effect.type === "spotlight") {
    const opacity = interpolate(frame, [0, duration], [effect.from, effect.to], { extrapolateRight: "clamp" });
    // spotlight = radial vignette overlay
    return (
      <AbsoluteFill>
        {renderTemplate(data.layout)}
        <div style={{
          position: "absolute", inset: 0,
          background: `radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,${1 - opacity}) 100%)`,
        }} />
      </AbsoluteFill>
    );
  }

  return <div style={style}>{renderTemplate(data.layout)}</div>;
};
