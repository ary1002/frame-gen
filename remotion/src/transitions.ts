import { TransConfig } from "./types";
import { fade } from "@remotion/transitions/fade";
import { wipe } from "@remotion/transitions/wipe";
import { slide } from "@remotion/transitions/slide";
import { clockWipe } from "@remotion/transitions/clock-wipe";
import { flip } from "@remotion/transitions/flip";

export function resolveTransition(t: TransConfig) {
  switch (t.type) {
    case "fade": return fade();
    case "dissolve": return fade();
    case "wipe": return wipe({ direction: (t.direction ?? "from-left") as any });
    case "circle_wipe": return clockWipe({ width: 1920, height: 1080 });
    case "stack": return slide({ direction: (t.direction ?? "from-right") as any });
    default: return fade();
  }
}
