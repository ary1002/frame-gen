from enum import Enum

class SlideState(str, Enum):
    PENDING = "PENDING"
    SCRIPT_READY = "SCRIPT_READY"
    AUDIO_STALE = "AUDIO_STALE"
    AUDIO_READY = "AUDIO_READY"
    RENDER_READY = "RENDER_READY"
    ERROR = "ERROR"

ALLOWED_TRANSITIONS = {
    SlideState.PENDING: {SlideState.SCRIPT_READY},
    SlideState.SCRIPT_READY: {SlideState.AUDIO_STALE, SlideState.ERROR},
    SlideState.AUDIO_STALE: {SlideState.AUDIO_READY, SlideState.ERROR},
    SlideState.AUDIO_READY: {SlideState.RENDER_READY},
    SlideState.ERROR: {SlideState.AUDIO_STALE},  # user retry
    SlideState.RENDER_READY: set(),
}
