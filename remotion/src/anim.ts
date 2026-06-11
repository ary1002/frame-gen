import { spring, interpolate } from "remotion";

export type SpringConfig = { damping?: number; stiffness?: number; mass?: number };

const SMOOTH: SpringConfig = { damping: 200 };
const SNAPPY: SpringConfig = { damping: 20, stiffness: 200 };

export function entrance(
  frame: number,
  fps: number,
  delayFrames = 0,
  config: SpringConfig = SMOOTH,
): number {
  return spring({ frame: frame - delayFrames, fps, config });
}

export function fadeUp(
  progress: number,
  distancePx = 40,
): { opacity: number; transform: string } {
  const translateY = interpolate(progress, [0, 1], [distancePx, 0]);
  return { opacity: progress, transform: `translateY(${translateY}px)` };
}

export function scaleIn(progress: number, from = 0.92): { transform: string; opacity: number } {
  const scale = interpolate(progress, [0, 1], [from, 1]);
  return { transform: `scale(${scale})`, opacity: progress };
}

export function secToFrames(seconds: number, fps: number): number {
  return Math.round(seconds * fps);
}

export { SMOOTH, SNAPPY };
