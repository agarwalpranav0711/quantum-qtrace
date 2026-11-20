"""Evidence model representing stored image files and integrity state."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base

if TYPE_CHECKING:
    from backend.app.models.case import Case
    from backend.app.models.analysis import Analysis
    from backend.app.models.note import ExaminerNote
    from backend.app.models.roi import RegionOfInterestModel


def get_utc_now() -> datetime:
    """Return current UTC timestamp with timezone."""
    return datetime.now(timezone.utc)


class Evidence(Base):
    """Evidence file record preserving chain-of-custody and cryptographic hash."""

    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=True
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False
    )
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), default="VERIFIED", index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Relationships
    case: Mapped[Optional["Case"]] = relationship("Case", back_populates="evidence_items")
    analyses: Mapped[List["Analysis"]] = relationship(
        "Analysis", back_populates="evidence", cascade="all, delete-orphan"
    )
    notes: Mapped[List["ExaminerNote"]] = relationship("ExaminerNote", back_populates="evidence")
    rois: Mapped[List["RegionOfInterestModel"]] = relationship(
        "RegionOfInterestModel", back_populates="evidence", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Evidence(filename='{self.original_filename}', sha256='{self.sha256_hash[:8]}...')>"

