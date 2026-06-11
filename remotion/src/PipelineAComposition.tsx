import React from "react";
import { Audio, AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { RemotionSchema } from "./types";
import { SlideWithEffect } from "./SlideWithEffect";
import { CaptionsLayer } from "./CaptionsLayer";
import { resolveTransition } from "./transitions";

interface Props { schema: RemotionSchema; }

export const PipelineAComposition: React.FC<Props> = ({ schema }) => {
  return (
    <AbsoluteFill>
      <TransitionSeries>
        {schema.slides.map((slide, i) => (
          <React.Fragment key={slide.slide_index}>
            <TransitionSeries.Sequence durationInFrames={slide.duration_frames}>
              <AbsoluteFill>
                <SlideWithEffect data={slide} />
                {slide.audio_url && <Audio src={slide.audio_url} />}
              </AbsoluteFill>
            </TransitionSeries.Sequence>
            {i < schema.slides.length - 1 && (
              <TransitionSeries.Transition
                presentation={resolveTransition(slide.layout.transition_out)}
                timing={linearTiming({ durationInFrames: slide.layout.transition_out.duration_frames })}
              />
            )}
          </React.Fragment>
        ))}
      </TransitionSeries>
      <CaptionsLayer captions={schema.captions} />
    </AbsoluteFill>
  );
};
