from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal

class EffectConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["zoom","blur","spotlight"]
    from_: float = Field(alias="from")
    to: float
    easing: str

class TransConfig(BaseModel):
    type: Literal["wipe","fade","dissolve","circle_wipe","stack"]
    direction: Optional[str] = None
    duration_frames: int

class SlideScript(BaseModel):
    slide_index: int
    text: str
    word_count: int
    est_duration_s: float
    gen_attempts: int = 1
    status: Literal["READY","TRUNCATED","ERROR"] = "READY"
    prompt_version: str
    script_hash: str

class SlideLayout(BaseModel):
    slide_index: int
    template: Literal["title_card","bullet_list","comparison_two_col","split_layout"]
    props: dict
    effect: EffectConfig
    transition_out: TransConfig
    duration_frames: Optional[int] = None

class AudioBlob(BaseModel):
    slide_index: int
    url: str
    actual_duration_s: float
    voice_id: str
    script_hash: str

class WordTimestamp(BaseModel):
    word: str
    start_s: float
    end_s: float

class SlideEntry(BaseModel):
    slide_index: int
    start_frame: int
    duration_frames: int
    audio_url: str
    layout: SlideLayout

class CaptionConfig(BaseModel):
    style: str = "default"
    color_active: str = "#FFFF00"
    word_timestamps: list[WordTimestamp]

class RemotionSchema(BaseModel):
    slides: list[SlideEntry]
    captions: CaptionConfig
    total_frames: int
    fps: int = 30
    serve_url: str
