import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="PENDING", nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    total_frames: Mapped[int | None] = mapped_column(Integer, nullable=True)
    video_url: Mapped[str | None] = mapped_column(String, nullable=True)
    article_url: Mapped[str | None] = mapped_column(String, nullable=True)
    render_progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
        nullable=False,
    )

    slides: Mapped[list["Slide"]] = relationship("Slide", back_populates="job", order_by="Slide.slide_index")


class Slide(Base):
    __tablename__ = "slides"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id"), nullable=False
    )
    slide_index: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String, default="PENDING", nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    est_duration_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_duration_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    gen_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String, default="READY", nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    script_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    layout_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String, nullable=True)
    voice_id: Mapped[str | None] = mapped_column(String, nullable=True)
    word_timestamps: Mapped[list | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
        nullable=False,
    )

    job: Mapped["Job"] = relationship("Job", back_populates="slides")
