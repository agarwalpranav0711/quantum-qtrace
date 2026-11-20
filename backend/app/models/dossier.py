"""SQLAlchemy database models for forensic investigation dossiers, sections, and exports."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base

if TYPE_CHECKING:
    from backend.app.models.case import Case


def get_utc_now() -> datetime:
    """Return current UTC timestamp with timezone."""
    return datetime.now(timezone.utc)


class DossierModel(Base):
    """
    Forensic investigation dossier container aggregating evidence, analyses,
    regions of interest, image comparisons, quantum telemetry, and examiner conclusions.
    """

    __tablename__ = "dossiers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    dossier_number: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(
        String(128), default="Lead Forensic Examiner", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), default="DRAFT", index=True, nullable=False
    )  # DRAFT, IN_REVIEW, APPROVED, EXPORTED, SUPERSEDED
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    confidentiality_level: Mapped[str] = mapped_column(
        String(64), default="STRICTLY CONFIDENTIAL - FORENSIC EVIDENCE", nullable=False
    )
    investigation_scope: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    examiner_conclusions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    limitations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    configuration_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    case: Mapped["Case"] = relationship("Case", back_populates="dossiers")
    sections: Mapped[List["DossierSectionModel"]] = relationship(
        "DossierSectionModel",
        back_populates="dossier",
        cascade="all, delete-orphan",
        order_by="DossierSectionModel.order_index",
    )
    exports: Mapped[List["DossierExportModel"]] = relationship(
        "DossierExportModel",
        back_populates="dossier",
        cascade="all, delete-orphan",
        order_by="desc(DossierExportModel.created_at)",
    )

    def __repr__(self) -> str:
        return f"<DossierModel(dossier_number='{self.dossier_number}', status='{self.status}', version={self.version})>"


class DossierSectionModel(Base):
    """Configurable and re-orderable section within a forensic dossier."""

    __tablename__ = "dossier_sections"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    dossier_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("dossiers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    section_key: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    custom_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    dossier: Mapped["DossierModel"] = relationship("DossierModel", back_populates="sections")

    def __repr__(self) -> str:
        return f"<DossierSectionModel(key='{self.section_key}', order={self.order_index}, enabled={self.is_enabled})>"


class DossierExportModel(Base):
    """
    Immutable export record capturing the exact file path, cryptographic hash,
    and complete frozen snapshot of a generated dossier report.
    """

    __tablename__ = "dossier_exports"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    dossier_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("dossiers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    export_format: Mapped[str] = mapped_column(String(16), nullable=False)  # 'PDF' or 'JSON'
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Relationships
    dossier: Mapped["DossierModel"] = relationship("DossierModel", back_populates="exports")

    def __repr__(self) -> str:
        return f"<DossierExportModel(version={self.version}, format='{self.export_format}', sha256='{self.sha256_hash[:8]}...')>"

