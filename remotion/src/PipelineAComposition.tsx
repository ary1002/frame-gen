import React from "react";
import { Audio, AbsoluteFill, Sequence } from "remotion";
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { RemotionSchema } from "./types";
import { SlideWithEffect } from "./SlideWithEffect";
import { CaptionsLayer } from "./CaptionsLayer";
import { resolveTransition } from "./transitions";

// 9 frames (~0.3 s) of silence before each slide's audio begins.
// Must match BREATH_FRAMES in app/pipeline/timeline.py.
const BREATH_FRAMES = 9;

interface Props { schema: RemotionSchema; }

export const PipelineAComposition: React.FC<Props> = ({ schema }) => {
  return (
    <AbsoluteFill>
      <TransitionSeries>
        {schema.slides.map((slide, i) => (
          <React.Fragment key={slide.slide_index}>
            <TransitionSeries.Sequence
              durationInFrames={slide.duration_frames}
              premountFor={slide.layout.transition_out.duration_frames}
            >
              <AbsoluteFill>
                <SlideWithEffect data={slide} />
                {slide.audio_url && (
                  <Sequence from={BREATH_FRAMES}>
                    <Audio src={slide.audio_url} />
                  </Sequence>
                )}
              </AbsoluteFill>
            </TransitionSeries.Sequence>
            {i < schema.slides.length - 1 && (
              <TransitionSeries.Transition
                presentation={resolveTransition(slide.layout.transition_out)}
                timing={springTiming({
                  config: { damping: 200 },
                  durationInFrames: slide.layout.transition_out.duration_frames,
                })}
              />
            )}
          </React.Fragment>
        ))}
      </TransitionSeries>
      <CaptionsLayer captions={schema.captions} />
    </AbsoluteFill>
  );
};
