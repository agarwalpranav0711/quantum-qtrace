"""Region of Interest (ROI) model for forensic annotations and crop tracking."""

import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base

if TYPE_CHECKING:
    from backend.app.models.evidence import Evidence
    from backend.app.models.analysis import Analysis


def get_utc_now() -> datetime:
    """Return current UTC timestamp with timezone."""
    return datetime.now(timezone.utc)


class RegionOfInterestModel(Base):
    """
    Region of Interest (ROI) representing an examiner-selected or algorithm-generated
    bounding area on an evidence photograph with investigative annotations.
    """

    __tablename__ = "regions_of_interest"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    evidence_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evidence.id", ondelete="CASCADE"), index=True, nullable=False
    )
    analysis_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="SET NULL"), index=True, nullable=True
    )
    roi_label: Mapped[str] = mapped_column(String(128), nullable=False)
    roi_type: Mapped[str] = mapped_column(
        String(64), default="EXAMINER_CREATED", nullable=False
    )  # EXAMINER_CREATED, ALGORITHM_CANDIDATE, COMPARISON_DELTA
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(32), default="#00F2FE", nullable=False)
    observation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hypothesis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
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
    evidence: Mapped["Evidence"] = relationship("Evidence", back_populates="rois")
    analysis: Mapped[Optional["Analysis"]] = relationship("Analysis")

    def __repr__(self) -> str:
        return f"<ROI(label='{self.roi_label}', box=[{self.x},{self.y},{self.width}x{self.height}])>"

