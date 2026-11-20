"""ExaminerNote model for investigator notes and observations."""

import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base

if TYPE_CHECKING:
    from backend.app.models.case import Case
    from backend.app.models.evidence import Evidence


def get_utc_now() -> datetime:
    """Return current UTC timestamp with timezone."""
    return datetime.now(timezone.utc)


class ExaminerNote(Base):
    """Investigator note attached to a case or specific evidence item."""

    __tablename__ = "examiner_notes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("evidence.id", ondelete="SET NULL"), index=True, nullable=True
    )
    author: Mapped[str] = mapped_column(String(128), default="Lead Examiner", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False,
    )

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="notes")
    evidence: Mapped[Optional["Evidence"]] = relationship("Evidence", back_populates="notes")

    def __repr__(self) -> str:
        return f"<ExaminerNote(author='{self.author}', case_id='{self.case_id}')>"

