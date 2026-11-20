"""Unified classical forensic analysis pipeline coordinator."""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.exceptions import EntityNotFoundException, IntegrityException
from backend.app.core.logging import get_logger
from backend.app.models.evidence import Evidence
from backend.app.models.analysis import Analysis
from backend.app.models.artifact import Artifact
from backend.app.storage.service import StorageService, get_storage_service
from backend.app.services.integrity import verify_file_integrity
from backend.app.forensics.registry import get_forensic_registry
from backend.app.forensics.schemas import (
    TechniqueResult,
    ForensicStatus,
    AnalysisExecutionRequest,
    AnalysisSummaryResponse,
    ArtifactReference,
)
from backend.app.forensics.consensus_fusion import fuse_candidate_regions

logger = get_logger("forensic_pipeline")


class ForensicPipeline:
    """Orchestrates multi-technique classical digital forensic examination."""

    def __init__(self, db: Session, storage_service: Optional[StorageService] = None) -> None:
        self.db = db
        self.storage = storage_service or get_storage_service()
        self.registry = get_forensic_registry()

    def run_analysis(
        self,
        evidence_id: str,
        request: AnalysisExecutionRequest,
    ) -> AnalysisSummaryResponse:
        """
        Execute configured classical forensic analysis pipeline against an evidence item.

        Guarantees:
        - Verifies evidence existence and storage containment.
        - Verifies WORM file bitstream integrity (SHA-256) before analysis.
        - Isolates failures: an individual technique error does NOT abort the remaining suite.
        - Persists structured Analysis and Artifact records in SQLite.
        """
        start_time = time.perf_counter()

        # 1. Fetch evidence record
        evidence = self.db.query(Evidence).filter(Evidence.id == evidence_id).one_or_none()
        if not evidence:
            raise EntityNotFoundException("Evidence", evidence_id)

        # 2. Verify bitstream integrity of original evidence
        is_intact, current_sha = verify_file_integrity(
            evidence.storage_path, evidence.sha256_hash
        )
        if not is_intact:
            logger.error(f"Evidence {evidence.id} bitstream integrity mismatch before analysis!")
            evidence.status = "COMPROMISED"
            self.db.commit()
            raise IntegrityException(
                f"Evidence integrity compromised: current SHA-256 does not match original ingestion hash. Analysis aborted."
            )

        # 3. Read original evidence bytes safely through storage layer
        evidence_path = Path(evidence.storage_path)
        if not evidence_path.exists():
            raise EntityNotFoundException("EvidenceFile", str(evidence_path))

        image_bytes = evidence_path.read_bytes()

        # 4. Resolve techniques to execute
        requested_ids = request.techniques or self.registry.list_technique_ids()
        technique_results: Dict[str, TechniqueResult] = {}
        all_artifacts: List[ArtifactReference] = []

        # Unique analysis identifier generated early for artifact naming
        import uuid
        analysis_id = str(uuid.uuid4())

        succeeded = 0
        failed = 0
        unsupported = 0

        # 5. Execute each technique sequentially with isolation
        for tech_id in requested_ids:
            tech = self.registry.get(tech_id)
            if not tech:
                logger.warning(f"Requested technique '{tech_id}' is not registered; skipping.")
                continue

            tech_params = request.parameters.get(tech_id, {}) if request.parameters else {}

            # Check applicability
            is_app, reason = tech.is_applicable(evidence.mime_type, image_bytes)
            if not is_app:
                unsupported += 1
                technique_results[tech_id] = TechniqueResult(
                    technique_id=tech.id,
                    technique_name=tech.name,
                    version=tech.version,
                    category=tech.category,
                    status=ForensicStatus.UNSUPPORTED_INPUT,
                    execution_time_ms=0.0,
                    parameters_used=tech_params,
                    warnings=[reason],
                    limitations=tech.limitations,
                )
                continue

            # Execute analysis
            try:
                res = tech.analyze(
                    image_path=evidence_path,
                    image_bytes=image_bytes,
                    parameters=tech_params,
                    storage_service=self.storage,
                    analysis_id=analysis_id,
                )
                technique_results[tech_id] = res
                if res.status == ForensicStatus.ANALYSIS_FAILED:
                    failed += 1
                else:
                    succeeded += 1
                if res.artifacts:
                    all_artifacts.extend(res.artifacts)
            except Exception as e:
                failed += 1
                logger.error(f"Unhandled exception in technique '{tech_id}': {str(e)}", exc_info=True)
                technique_results[tech_id] = TechniqueResult(
                    technique_id=tech.id,
                    technique_name=tech.name,
                    version=tech.version,
                    category=tech.category,
                    status=ForensicStatus.ANALYSIS_FAILED,
                    execution_time_ms=0.0,
                    parameters_used=tech_params,
                    error_message=f"Internal failure: {str(e)}",
                    limitations=tech.limitations,
                )

        # 6. Multi-Signal Consensus Fusion
        consensus_rois = fuse_candidate_regions(technique_results)

        # 7. Determine overall pipeline outcome status
        has_indicators = any(
            r.status == ForensicStatus.POTENTIAL_INDICATOR_DETECTED for r in technique_results.values()
        )
        if has_indicators:
            overall_status = ForensicStatus.POTENTIAL_INDICATOR_DETECTED
        elif succeeded > 0:
            overall_status = ForensicStatus.NO_ANOMALY_DETECTED
        elif unsupported == len(technique_results):
            overall_status = ForensicStatus.UNSUPPORTED_INPUT
        else:
            overall_status = ForensicStatus.ANALYSIS_FAILED

        total_elapsed = (time.perf_counter() - start_time) * 1000.0

        # 8. Persist Analysis and Artifact records to Database
        db_analysis_status = "COMPLETED"
        if failed > 0 and succeeded > 0:
            db_analysis_status = "PARTIAL_SUCCESS"
        elif failed > 0 and succeeded == 0:
            db_analysis_status = "FAILED"

        # Serialize results cleanly
        results_payload = {
            "overall_status": overall_status.value,
            "techniques_run": len(technique_results),
            "techniques_succeeded": succeeded,
            "techniques_failed": failed,
            "techniques_unsupported": unsupported,
            "consensus_regions": [roi.model_dump() for roi in consensus_rois],
            "technique_results": {k: v.model_dump() for k, v in technique_results.items()},
        }

        db_analysis = Analysis(
            id=analysis_id,
            case_id=evidence.case_id,
            evidence_id=evidence.id,
            analysis_type="CLASSICAL_FORENSIC_SUITE" if len(requested_ids) > 1 else f"CLASSICAL_{requested_ids[0].upper()}",
            algorithm_name="Q-TRACE Classical Forensic Engine v1.0",
            status=db_analysis_status,
            config_json=json.dumps(request.parameters or {}),
            results_json=json.dumps(results_payload),
            execution_time_ms=round(total_elapsed, 2),
            error_message=None if failed == 0 else f"{failed} technique(s) encountered execution errors.",
        )
        self.db.add(db_analysis)

        # Persist generated artifacts
        for art in all_artifacts:
            art_id = str(uuid.uuid4())
            art_path = self.storage.get_category_dir("analysis") / art.stored_filename
            db_artifact = Artifact(
                id=art_id,
                analysis_id=analysis_id,
                artifact_type=art.artifact_type,
                file_path=str(art_path),
                stored_filename=art.stored_filename,
                sha256_hash=art.sha256_hash or "unknown",
            )
            self.db.add(db_artifact)
            art.artifact_id = art_id

        self.db.commit()
        self.db.refresh(db_analysis)

        logger.info(
            f"Forensic analysis {analysis_id} completed for evidence {evidence_id} in {total_elapsed:.1f} ms "
            f"({succeeded} succeeded, {failed} failed, {unsupported} unsupported, status: {overall_status.value})"
        )

        return AnalysisSummaryResponse(
            analysis_id=analysis_id,
            evidence_id=evidence.id,
            case_id=evidence.case_id,
            status=db_analysis_status,
            total_execution_time_ms=round(total_elapsed, 2),
            techniques_run=len(technique_results),
            techniques_succeeded=succeeded,
            techniques_failed=failed,
            techniques_unsupported=unsupported,
            overall_status=overall_status,
            technique_results=technique_results,
            consensus_regions=consensus_rois,
            artifacts=all_artifacts,
            created_at=db_analysis.created_at.isoformat(),
        )

    def get_analysis_by_id(self, analysis_id: str) -> AnalysisSummaryResponse:
        """Retrieve stored analysis record and reconstructed summary."""
        analysis = self.db.query(Analysis).filter(Analysis.id == analysis_id).one_or_none()
        if not analysis:
            raise EntityNotFoundException("Analysis", analysis_id)

        results_data = json.loads(analysis.results_json or "{}")
        technique_results_raw = results_data.get("technique_results", {})
        technique_results = {
            k: TechniqueResult(**v) for k, v in technique_results_raw.items()
        }
        consensus_rois = [
            fuse_candidate_regions(technique_results)
        ]

        artifacts_list = [
            ArtifactReference(
                artifact_id=art.id,
                artifact_type=art.artifact_type,
                stored_filename=art.stored_filename,
                description=f"Artifact {art.artifact_type}",
                sha256_hash=art.sha256_hash,
            )
            for art in analysis.artifacts
        ]

        return AnalysisSummaryResponse(
            analysis_id=analysis.id,
            evidence_id=analysis.evidence_id,
            case_id=analysis.case_id,
            status=analysis.status,
            total_execution_time_ms=analysis.execution_time_ms or 0.0,
            techniques_run=results_data.get("techniques_run", len(technique_results)),
            techniques_succeeded=results_data.get("techniques_succeeded", 0),
            techniques_failed=results_data.get("techniques_failed", 0),
            techniques_unsupported=results_data.get("techniques_unsupported", 0),
            overall_status=ForensicStatus(results_data.get("overall_status", ForensicStatus.INCONCLUSIVE.value)),
            technique_results=technique_results,
            consensus_regions=consensus_rois[0] if consensus_rois else [],
            artifacts=artifacts_list,
            created_at=analysis.created_at.isoformat(),
        )

    def list_analyses_for_evidence(self, evidence_id: str) -> List[Dict[str, Any]]:
        """List summary history of all analyses performed on a given evidence item."""
        analyses = (
            self.db.query(Analysis)
            .filter(Analysis.evidence_id == evidence_id)
            .order_by(Analysis.created_at.desc())
            .all()
        )
        output = []
        for a in analyses:
            results_data = json.loads(a.results_json or "{}")
            output.append({
                "analysis_id": a.id,
                "evidence_id": a.evidence_id,
                "analysis_type": a.analysis_type,
                "algorithm_name": a.algorithm_name,
                "status": a.status,
                "overall_status": results_data.get("overall_status", "UNKNOWN"),
                "execution_time_ms": a.execution_time_ms,
                "artifact_count": len(a.artifacts),
                "created_at": a.created_at.isoformat(),
            })
        return output
