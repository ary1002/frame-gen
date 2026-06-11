export interface EffectConfig {
  type: "zoom" | "blur" | "spotlight";
  from: number;
  to: number;
  easing: string;
}

export interface TransConfig {
  type: "wipe" | "fade" | "dissolve" | "circle_wipe" | "stack";
  direction?: string;
  duration_frames: number;
}

export interface SlideLayout {
  slide_index: number;
  template: "title_card" | "bullet_list" | "comparison_two_col" | "split_layout";
  props: Record<string, unknown>;
  effect: EffectConfig;
  transition_out: TransConfig;
  duration_frames: number;
}

export interface WordTimestamp {
  word: string;
  start_s: number;
  end_s: number;
}

export interface SlideEntry {
  slide_index: number;
  start_frame: number;
  duration_frames: number;
  audio_url: string;
  layout: SlideLayout;
  word_timestamps: WordTimestamp[];
  cues: number[];
}

export interface CaptionConfig {
  style: string;
  color_active: string;
  word_timestamps: WordTimestamp[];
}

export interface RemotionSchema {
  slides: SlideEntry[];
  captions: CaptionConfig;
  total_frames: number;
  fps: number;
  serve_url: string;
}
