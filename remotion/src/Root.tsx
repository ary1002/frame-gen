import React from "react";
import { Composition } from "remotion";
import { PipelineAComposition } from "./PipelineAComposition";
import { RemotionSchema } from "./types";

const SAMPLE_SCHEMA: RemotionSchema = {
  slides: [
    {
      slide_index: 0,
      start_frame: 0,
      duration_frames: 150,
      audio_url: "",
      cues: [0.2],
      word_timestamps: [
        { word: "The", start_s: 0.0, end_s: 0.3 },
        { word: "Future", start_s: 0.3, end_s: 0.7 },
        { word: "of", start_s: 0.7, end_s: 0.9 },
        { word: "AI", start_s: 0.9, end_s: 1.4 },
        { word: "is", start_s: 1.4, end_s: 1.6 },
        { word: "here", start_s: 1.6, end_s: 2.0 },
      ],
      layout: {
        slide_index: 0,
        template: "title_card",
        props: { title: "The Future of AI", eyebrow: "Episode 1", background_color: "#1a1a2e" },
        effect: { type: "zoom", from: 1.0, to: 1.05, easing: "easeInOut" },
        transition_out: { type: "fade", duration_frames: 20 },
        duration_frames: 150,
      },
    },
    {
      slide_index: 1,
      start_frame: 130,
      duration_frames: 180,
      audio_url: "",
      // cues: when each bullet's first word is spoken (relative to this slide start)
      cues: [0.3, 1.2, 2.4],
      word_timestamps: [
        { word: "Large", start_s: 0.3, end_s: 0.7 },
        { word: "language", start_s: 0.7, end_s: 1.1 },
        { word: "models", start_s: 1.1, end_s: 1.5 },
        { word: "Multimodal", start_s: 1.5, end_s: 2.0 },
        { word: "capabilities", start_s: 2.0, end_s: 2.6 },
        { word: "Autonomous", start_s: 2.6, end_s: 3.1 },
        { word: "agents", start_s: 3.1, end_s: 3.6 },
      ],
      layout: {
        slide_index: 1,
        template: "bullet_list",
        props: {
          title: "Key Developments",
          points: ["Large language models", "Multimodal capabilities", "Autonomous agents"],
          background_color: "#16213e",
        },
        effect: { type: "blur", from: 0, to: 0, easing: "linear" },
        transition_out: { type: "wipe", direction: "from-left", duration_frames: 20 },
        duration_frames: 180,
      },
    },
    {
      slide_index: 2,
      start_frame: 290,
      duration_frames: 150,
      audio_url: "",
      // cues: col0 heading, col0 points, col1 heading, col1 points
      cues: [0.2, 0.8, 1.4, 2.0, 2.6, 3.2],
      word_timestamps: [
        { word: "Rule-based", start_s: 0.2, end_s: 0.6 },
        { word: "systems", start_s: 0.6, end_s: 1.0 },
        { word: "Narrow", start_s: 1.0, end_s: 1.4 },
        { word: "AI", start_s: 1.4, end_s: 1.7 },
        { word: "Foundation", start_s: 1.7, end_s: 2.1 },
        { word: "models", start_s: 2.1, end_s: 2.5 },
        { word: "General", start_s: 2.5, end_s: 2.9 },
        { word: "reasoning", start_s: 2.9, end_s: 3.4 },
      ],
      layout: {
        slide_index: 2,
        template: "comparison_two_col",
        props: {
          title: "Then vs Now",
          columns: [
            { heading: "2020", points: ["Rule-based systems", "Narrow AI", "Expert systems"] },
            { heading: "2025", points: ["Foundation models", "General reasoning", "Agentic pipelines"] },
          ],
          background_color: "#0f3460",
        },
        effect: { type: "spotlight", from: 0.6, to: 1.0, easing: "easeIn" },
        transition_out: { type: "circle_wipe", duration_frames: 20 },
        duration_frames: 150,
      },
    },
  ],
  captions: {
    style: "default",
    color_active: "#FFFF00",
    word_timestamps: [
      { word: "The", start_s: 0.0, end_s: 0.3 },
      { word: "Future", start_s: 0.3, end_s: 0.7 },
      { word: "of", start_s: 0.7, end_s: 0.9 },
      { word: "AI", start_s: 0.9, end_s: 1.4 },
      { word: "is", start_s: 1.4, end_s: 1.6 },
      { word: "here", start_s: 1.6, end_s: 2.0 },
      { word: "Large", start_s: 4.53, end_s: 4.87 },
      { word: "language", start_s: 4.87, end_s: 5.27 },
      { word: "models", start_s: 5.27, end_s: 5.67 },
      { word: "Multimodal", start_s: 5.67, end_s: 6.17 },
      { word: "capabilities", start_s: 6.17, end_s: 6.77 },
      { word: "Autonomous", start_s: 6.77, end_s: 7.27 },
      { word: "agents", start_s: 7.27, end_s: 7.77 },
    ],
  },
  total_frames: 440,
  fps: 30,
  serve_url: "local",
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="PipelineAComposition"
    component={PipelineAComposition}
    durationInFrames={SAMPLE_SCHEMA.total_frames}
    fps={SAMPLE_SCHEMA.fps}
    width={1920}
    height={1080}
    defaultProps={{ schema: SAMPLE_SCHEMA }}
    calculateMetadata={({ props }) => ({
      durationInFrames: (props as { schema: RemotionSchema }).schema.total_frames,
      fps: (props as { schema: RemotionSchema }).schema.fps,
    })}
  />
);
