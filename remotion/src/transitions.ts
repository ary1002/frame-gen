import { TransConfig } from "./types";
import { fade, wipe, slide, clockWipe, flip } from "@remotion/transitions";

export function resolveTransition(t: TransConfig) {
  switch (t.type) {
    case "fade": return fade();
    case "wipe": return wipe({ direction: (t.direction ?? "from-left") as any });
    case "dissolve": return fade(); // dissolve ≈ fade
    case "circle_wipe": return clockWipe();
    case "stack": return flip();
    default: return fade();
  }
}
