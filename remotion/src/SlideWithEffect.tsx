import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, Easing, AbsoluteFill, spring } from "remotion";
import { SlideEntry } from "./types";
import { TitleCard } from "./templates/TitleCard";
import { BulletList } from "./templates/BulletList";
import { ComparisonTwoCol } from "./templates/ComparisonTwoCol";
import { SplitLayout } from "./templates/SplitLayout";

function renderTemplate(layout: SlideEntry["layout"], cues: number[]) {
  const p = layout.props as any;
  switch (layout.template) {
    case "title_card": return <TitleCard {...p} cues={cues} />;
    case "bullet_list": return <BulletList {...p} cues={cues} />;
    case "comparison_two_col": return <ComparisonTwoCol {...p} cues={cues} />;
    case "split_layout": return <SplitLayout {...p} cues={cues} />;
    default: return <TitleCard title="Unknown template" />;
  }
}

interface Props { data: SlideEntry; }

export const SlideWithEffect: React.FC<Props> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const duration = data.duration_frames;
  const effect = data.layout.effect;
  const cues = data.cues ?? [];

  // Subtle slide-level entrance: whole scene fades+scales in over ~12 frames
  const slideEntrance = spring({ frame, fps, config: { damping: 200 } });
  const entranceScale = interpolate(slideEntrance, [0, 1], [0.97, 1]);
  const entranceOpacity = slideEntrance;

  let effectStyle: React.CSSProperties = {};

  if (effect.type === "zoom") {
    // Gentle Ken Burns with eased motion
    const scale = interpolate(frame, [0, duration], [effect.from, effect.to], {
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.quad),
    });
    effectStyle = { transform: `scale(${scale})`, transformOrigin: "center center" };
  } else if (effect.type === "blur") {
    // Ease-out sharpen: blur clears quickly, then holds
    const sharpFrames = Math.min(Math.round(0.5 * fps), duration);
    const blur = interpolate(
      frame,
      [0, sharpFrames, duration],
      [effect.from, effect.to, effect.to],
      { extrapolateRight: "clamp", easing: Easing.out(Easing.quad) },
    );
    effectStyle = { filter: `blur(${blur}px)` };
  } else if (effect.type === "spotlight") {
    const opacity = interpolate(frame, [0, duration], [effect.from, effect.to], {
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.quad),
    });
    return (
      <AbsoluteFill style={{ opacity: entranceOpacity, transform: `scale(${entranceScale})` }}>
        {renderTemplate(data.layout, cues)}
        <div style={{
          position: "absolute", inset: 0,
          background: `radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,${1 - opacity}) 100%)`,
        }} />
      </AbsoluteFill>
    );
  }

  return (
    <div style={{
      width: "100%", height: "100%",
      opacity: entranceOpacity,
      transform: `${effectStyle.transform ? effectStyle.transform + " " : ""}scale(${entranceScale})`,
      transformOrigin: "center center",
      filter: effectStyle.filter,
    }}>
      {renderTemplate(data.layout, cues)}
    </div>
  );
};
