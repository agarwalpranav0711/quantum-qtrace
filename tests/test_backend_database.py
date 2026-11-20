"""Unit tests for the SQLite database layer and foundational ORM models."""

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

from backend.app.database.base import Base
from backend.app.models.case import Case
from backend.app.models.evidence import Evidence
from backend.app.models.analysis import Analysis
from backend.app.models.artifact import Artifact
from backend.app.models.note import ExaminerNote


@pytest.fixture
def db_session(tmp_path):
    """Fixture providing an isolated SQLite database session."""
    db_file = tmp_path / "test_qtrace.db"
    db_url = f"sqlite:///{db_file}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    # Enforce pragmas
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.execute(text("PRAGMA foreign_keys=ON;"))

    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_sqlite_pragmas(db_session):
    """Verify that SQLite WAL mode and foreign key constraints are active."""
    mode = db_session.execute(text("PRAGMA journal_mode;")).scalar()
    fk = db_session.execute(text("PRAGMA foreign_keys;")).scalar()

    assert mode.lower() == "wal"
    assert fk == 1


def test_case_and_notes_relationship(db_session):
    """Verify Case creation and ExaminerNote relationship with cascade deletion."""
    case = Case(
        case_number="QC-2026-TEST",
        title="Insurance Vehicle Audit",
        description="Collision claim suspicious photograph check",
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    assert case.id is not None
    assert case.status == "OPEN"

    # Add Note
    note = ExaminerNote(
        case_id=case.id,
        author="Lead Inspector",
        content="Detected suspicious shadow boundaries on rear bumper.",
    )
    db_session.add(note)
    db_session.commit()

    # Re-query
    queried_case = db_session.execute(select(Case).where(Case.id == case.id)).scalar_one()
    assert len(queried_case.notes) == 1
    assert queried_case.notes[0].content == "Detected suspicious shadow boundaries on rear bumper."

    # Test Cascade Delete
    db_session.delete(queried_case)
    db_session.commit()

    notes_remaining = db_session.execute(select(ExaminerNote)).scalars().all()
    assert len(notes_remaining) == 0


def test_evidence_and_analysis_relationship(db_session):
    """Verify Evidence, Analysis, and Artifact linkage."""
    case = Case(case_number="QC-2026-EVD", title="Damage Check")
    db_session.add(case)
    db_session.commit()

    evidence = Evidence(
        case_id=case.id,
        original_filename="bumper.png",
        stored_filename="e3b0c442.png",
        storage_path="/path/to/storage/originals/e3b0c442.png",
        mime_type="image/png",
        file_size=1024,
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        width=512,
        height=512,
        status="VERIFIED",
    )
    db_session.add(evidence)
    db_session.commit()

    analysis = Analysis(
        case_id=case.id,
        evidence_id=evidence.id,
        analysis_type="QUANTUM_COMPARISON_16Q",
        algorithm_name="NEQR 16-Qubit Quantum Comparator",
        status="COMPLETED",
        config_json='{"shots": 1000}',
        results_json='{"fidelity": 1.0, "differing_pixels": 0}',
        execution_time_ms=45.2,
    )
    db_session.add(analysis)
    db_session.commit()

    artifact = Artifact(
        analysis_id=analysis.id,
        artifact_type="DIFFERENCE_MAP",
        file_path="/path/to/diff_map.png",
        stored_filename="diff_map.png",
        sha256_hash="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    )
    db_session.add(artifact)
    db_session.commit()

    # Re-query and verify relationships
    q_analysis = db_session.execute(select(Analysis).where(Analysis.id == analysis.id)).scalar_one()
    assert len(q_analysis.artifacts) == 1
    assert q_analysis.artifacts[0].artifact_type == "DIFFERENCE_MAP"
    assert q_analysis.evidence.original_filename == "bumper.png"

