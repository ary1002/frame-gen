import { TransConfig } from "./types";
// Import presentation functions from their explicit subpaths. The package's
// ESM entry doesn't re-export these presentations, so importing from the
// subpaths ensures we get the functions at runtime.
import { fade } from "@remotion/transitions/fade";
import { wipe } from "@remotion/transitions/wipe";
import { slide } from "@remotion/transitions/slide";
import { clockWipe } from "@remotion/transitions/clock-wipe";
import { flip } from "@remotion/transitions/flip";

export function resolveTransition(t: TransConfig) {
  switch (t.type) {
    case "fade": return fade();
    case "wipe": return wipe({ direction: (t.direction ?? "from-left") as any });
    case "dissolve": return fade(); // dissolve ≈ fade
  case "circle_wipe": return clockWipe({ width: 1920, height: 1080 });
    case "stack": return flip();
    default: return fade();
  }
}
