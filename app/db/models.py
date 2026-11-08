from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, Float, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CurriculumRow(Base):
    __tablename__ = "curricula"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic: Mapped[str] = mapped_column(String(200))
    optional_context: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str] = mapped_column(String(100))
    generation_latency_ms: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    content: Mapped[dict] = mapped_column(JSONB)

    lessons: Mapped[list["LessonRow"]] = relationship(
        back_populates="curriculum",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class LessonRow(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    curriculum_id: Mapped[int] = mapped_column(
        ForeignKey("curricula.id", ondelete="CASCADE"), index=True
    )
    node_id: Mapped[str] = mapped_column(String(50))
    detail_level: Mapped[str] = mapped_column(String(25))
    model: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str] = mapped_column(String(100))
    generation_latency_ms: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    content: Mapped[dict] = mapped_column(JSONB)

    curriculum: Mapped["CurriculumRow"] = relationship(back_populates="lessons")