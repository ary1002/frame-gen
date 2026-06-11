import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="PENDING")
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    remotion_schema_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    slides: Mapped[list["Slide"]] = relationship("Slide", back_populates="job", cascade="all, delete-orphan")


class Slide(Base):
    __tablename__ = "slides"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    slide_index: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(64), nullable=False, default="PENDING")

    # Script fields
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    est_duration_s: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    script_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Audio fields
    audio_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actual_duration_s: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    voice_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    word_timestamps: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Layout fields
    layout_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    job: Mapped["Job"] = relationship("Job", back_populates="slides")
