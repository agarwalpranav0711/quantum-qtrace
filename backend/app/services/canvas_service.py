"""Forensic Canvas business logic: ROI management, derived crops, and image comparison."""

import io
import math
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from PIL import Image
import numpy as np
import cv2

from backend.app.core.exceptions import (
    EntityNotFoundException,
    ValidationException,
    IntegrityException,
    StorageException,
)
from backend.app.core.logging import get_logger
from backend.app.models.evidence import Evidence
from backend.app.models.analysis import Analysis
from backend.app.models.roi import RegionOfInterestModel
from backend.app.models.artifact import Artifact
from backend.app.schemas.roi import (
    ROICreate,
    ROIUpdate,
    ROICropResponse,
    ImageComparisonRequest,
    ImageComparisonResponse,
)
from backend.app.storage.service import get_storage_service, StorageService
from backend.app.services.integrity import compute_sha256_bytes, verify_file_integrity

logger = get_logger("canvas_service")


def compute_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
    """Compute Structural Similarity Index (SSIM) between two grayscale images."""
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2

    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)

    kernel = cv2.getGaussianKernel(11, 1.5)
    window = np.outer(kernel, kernel.transpose())

    mu1 = cv2.filter2D(img1, -1, window)[5:-5, 5:-5]
    mu2 = cv2.filter2D(img2, -1, window)[5:-5, 5:-5]

    mu1_sq = mu1 ** 2
    mu2_sq = mu2 ** 2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = cv2.filter2D(img1 ** 2, -1, window)[5:-5, 5:-5] - mu1_sq
    sigma2_sq = cv2.filter2D(img2 ** 2, -1, window)[5:-5, 5:-5] - mu2_sq
    sigma12 = cv2.filter2D(img1 * img2, -1, window)[5:-5, 5:-5] - mu1_mu2

    ssim_map = ((2 * mu1_mu2 + c1) * (2 * sigma12 + c2)) / (
        (mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2) + 1e-12
    )
    return float(np.mean(ssim_map))


class CanvasService:
    """Coordinates interactive forensic canvas operations, ROI persistence, and comparison."""

    def __init__(self, db: Session, storage_service: Optional[StorageService] = None) -> None:
        self.db = db
        self.storage = storage_service or get_storage_service()

    # --- ROI Management ---

    def create_roi(self, evidence_id: str, payload: ROICreate) -> RegionOfInterestModel:
        """Register a new Region of Interest with boundary validation."""
        evidence = self.db.execute(
            select(Evidence).where(Evidence.id == evidence_id)
        ).scalar_one_or_none()
        if not evidence:
            raise EntityNotFoundException("Evidence", evidence_id)

        # Validate coordinates against original image dimensions if known
        if evidence.width and evidence.height:
            if payload.x >= evidence.width or payload.y >= evidence.height:
                raise ValidationException(
                    f"ROI origin ({payload.x}, {payload.y}) is outside image boundaries ({evidence.width}x{evidence.height})."
                )
            # Clamp width and height to fit inside boundaries
            max_w = evidence.width - payload.x
            max_h = evidence.height - payload.y
            roi_w = min(payload.width, max_w)
            roi_h = min(payload.height, max_h)
        else:
            roi_w = payload.width
            roi_h = payload.height

        if roi_w <= 0 or roi_h <= 0:
            raise ValidationException("ROI width and height must be positive integers.")

        roi = RegionOfInterestModel(
            evidence_id=evidence.id,
            analysis_id=payload.analysis_id,
            roi_label=payload.roi_label,
            roi_type=payload.roi_type,
            x=payload.x,
            y=payload.y,
            width=roi_w,
            height=roi_h,
            color=payload.color,
            observation=payload.observation,
            hypothesis=payload.hypothesis,
            confidence=payload.confidence,
        )
        self.db.add(roi)
        self.db.commit()
        self.db.refresh(roi)

        logger.info(f"Created ROI '{roi.roi_label}' on evidence {evidence_id} (Box: [{roi.x},{roi.y},{roi.width}x{roi.height}])")
        return roi

    def get_roi_by_id(self, roi_id: str) -> RegionOfInterestModel:
        """Retrieve a specific ROI by ID."""
        roi = self.db.execute(
            select(RegionOfInterestModel).where(RegionOfInterestModel.id == roi_id)
        ).scalar_one_or_none()
        if not roi:
            raise EntityNotFoundException("RegionOfInterest", roi_id)
        return roi

    def list_rois_for_evidence(self, evidence_id: str) -> List[RegionOfInterestModel]:
        """List all ROIs associated with an evidence item."""
        evidence = self.db.execute(
            select(Evidence).where(Evidence.id == evidence_id)
        ).scalar_one_or_none()
        if not evidence:
            raise EntityNotFoundException("Evidence", evidence_id)

        items = self.db.execute(
            select(RegionOfInterestModel)
            .where(RegionOfInterestModel.evidence_id == evidence_id)
            .order_by(RegionOfInterestModel.created_at.asc())
        ).scalars().all()
        return list(items)

    def update_roi(self, roi_id: str, payload: ROIUpdate) -> RegionOfInterestModel:
        """Update an existing ROI's coordinates, label, color, or annotations."""
        roi = self.get_roi_by_id(roi_id)

        if payload.roi_label is not None:
            roi.roi_label = payload.roi_label
        if payload.x is not None:
            roi.x = payload.x
        if payload.y is not None:
            roi.y = payload.y
        if payload.width is not None and payload.width > 0:
            roi.width = payload.width
        if payload.height is not None and payload.height > 0:
            roi.height = payload.height
        if payload.color is not None:
            roi.color = payload.color
        if payload.observation is not None:
            roi.observation = payload.observation
        if payload.hypothesis is not None:
            roi.hypothesis = payload.hypothesis
        if payload.confidence is not None:
            roi.confidence = payload.confidence

        self.db.commit()
        self.db.refresh(roi)
        return roi

    def delete_roi(self, roi_id: str) -> bool:
        """Delete an ROI record."""
        roi = self.get_roi_by_id(roi_id)
        self.db.delete(roi)
        self.db.commit()
        logger.info(f"Deleted ROI {roi_id}.")
        return True

    # --- Derived ROI Crop Artifact Generation ---

    def generate_roi_crop(self, roi_id: str) -> ROICropResponse:
        """
        Extract the specified ROI as a discrete derivative crop artifact in WORM storage.
        Preserves original evidence, calculates SHA-256 hash, and generates 4x4 quantum patch.
        """
        roi = self.get_roi_by_id(roi_id)
        evidence = roi.evidence

        # 1. Read original evidence
        evidence_path = Path(evidence.storage_path)
        if not evidence_path.exists():
            raise EntityNotFoundException("EvidenceFile", str(evidence_path))

        image_bytes = evidence_path.read_bytes()

        # 2. Perform in-memory crop
        with Image.open(io.BytesIO(image_bytes)) as img:
            rgb_img = img.convert("RGB")
            # Pillow crop box: (left, upper, right, lower)
            crop_box = (roi.x, roi.y, roi.x + roi.width, roi.y + roi.height)
            cropped_img = rgb_img.crop(crop_box)

            # Extract 4x4 quantum patch from centroid
            crop_arr = np.array(cropped_img)
            gray_crop = cv2.cvtColor(crop_arr, cv2.COLOR_RGB2GRAY)
            ch, cw = gray_crop.shape

            cy, cx = ch // 2, cw // 2
            py1 = max(0, min(ch - 4, cy - 2))
            px1 = max(0, min(cw - 4, cx - 2))
            quantized_4x4 = (gray_crop[py1 : py1 + 4, px1 : px1 + 4] >> 4).tolist()

            # Save cropped PNG bytes
            buf = io.BytesIO()
            cropped_img.save(buf, format="PNG")
            crop_bytes = buf.getvalue()

        # 3. Store artifact in 'derivatives' directory
        crop_sha256 = compute_sha256_bytes(crop_bytes)
        artifact_filename = f"crop_{roi.id[:8]}_{roi.width}x{roi.height}_{crop_sha256[:8]}.png"

        target_path = self.storage.store_file(
            category="derivatives",
            filename=artifact_filename,
            file_bytes=crop_bytes,
        )

        # 4. Ensure an Analysis record exists for this crop
        analysis_id = roi.analysis_id
        if not analysis_id:
            import json
            crop_analysis = Analysis(
                id=str(uuid.uuid4()),
                evidence_id=evidence.id,
                case_id=evidence.case_id,
                analysis_type="ROI_CROP",
                algorithm_name="Q-TRACE ROI Derivative Extractor",
                status="COMPLETED",
                config_json=json.dumps({"roi_id": roi.id, "crop_box": [roi.x, roi.y, roi.width, roi.height]}),
                results_json=json.dumps({"crop_sha256": crop_sha256, "dimensions": [roi.width, roi.height]}),
                execution_time_ms=0.0,
            )
            self.db.add(crop_analysis)
            analysis_id = crop_analysis.id
            roi.analysis_id = analysis_id

        # Register Artifact in DB
        artifact = Artifact(
            analysis_id=analysis_id,
            artifact_type="ROI_CROP",
            file_path=str(target_path),
            stored_filename=artifact_filename,
            sha256_hash=crop_sha256,
        )
        self.db.add(artifact)
        self.db.commit()
        self.db.refresh(artifact)

        logger.info(f"Generated ROI crop artifact: {artifact_filename} (SHA256: {crop_sha256[:12]}...)")

        return ROICropResponse(
            roi_id=roi.id,
            evidence_id=evidence.id,
            artifact_id=artifact.id,
            stored_filename=artifact_filename,
            sha256_hash=crop_sha256,
            crop_x=roi.x,
            crop_y=roi.y,
            crop_width=roi.width,
            crop_height=roi.height,
            suggested_quantum_patch=quantized_4x4,
        )

    # --- Image Comparison Engine ---

    def compare_images(self, payload: ImageComparisonRequest) -> ImageComparisonResponse:
        """
        Execute deterministic visual difference and alignment comparison between two evidence images.

        Guarantees:
        - NEVER alters either source evidence file.
        - Calculates exact pixel difference metrics (MAE, RMSE, PSNR, SSIM).
        - Generates difference heatmap artifact in storage.
        - Produces dual 4x4 quantum matrices for Quantum Laboratory comparative verification.
        """
        ev1 = self.db.execute(select(Evidence).where(Evidence.id == payload.primary_evidence_id)).scalar_one_or_none()
        if not ev1:
            raise EntityNotFoundException("PrimaryEvidence", payload.primary_evidence_id)

        ev2 = self.db.execute(select(Evidence).where(Evidence.id == payload.comparison_evidence_id)).scalar_one_or_none()
        if not ev2:
            raise EntityNotFoundException("ComparisonEvidence", payload.comparison_evidence_id)

        # Read images into memory
        p1 = Path(ev1.storage_path)
        p2 = Path(ev2.storage_path)
        if not p1.exists():
            raise EntityNotFoundException("EvidenceFile", str(p1))
        if not p2.exists():
            raise EntityNotFoundException("EvidenceFile", str(p2))

        warnings: List[str] = []

        with Image.open(p1) as img1_pil, Image.open(p2) as img2_pil:
            arr1 = np.array(img1_pil.convert("RGB"))
            arr2 = np.array(img2_pil.convert("RGB"))

        h1, w1 = arr1.shape[:2]
        h2, w2 = arr2.shape[:2]
        identical_dims = (w1 == w2 and h1 == h2)

        alignment_performed = False
        alignment_method = "NONE"
        alignment_status = "IDENTICAL_GRID" if identical_dims else "DIMENSION_MISMATCH"
        trans_matrix = None

        # Apply manual offsets if specified
        if payload.manual_offset_x != 0 or payload.manual_offset_y != 0:
            M = np.float32([
                [1, 0, payload.manual_offset_x],
                [0, 1, payload.manual_offset_y],
            ])
            arr2 = cv2.warpAffine(arr2, M, (w1, h1), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
            alignment_performed = True
            alignment_method = "MANUAL_OFFSET"
            alignment_status = f"OFFSET_APPLIED_DX{payload.manual_offset_x}_DY{payload.manual_offset_y}"
            trans_matrix = M.tolist()
        elif payload.align_images and hasattr(cv2, "SIFT_create"):
            # Attempt SIFT feature homography
            try:
                g1 = cv2.cvtColor(arr1, cv2.COLOR_RGB2GRAY)
                g2 = cv2.cvtColor(arr2, cv2.COLOR_RGB2GRAY)
                sift = cv2.SIFT_create(nfeatures=1000)
                kp1, des1 = sift.detectAndCompute(g1, None)
                kp2, des2 = sift.detectAndCompute(g2, None)

                if des1 is not None and des2 is not None and len(kp1) >= 10 and len(kp2) >= 10:
                    bf = cv2.BFMatcher(cv2.NORM_L2)
                    raw_matches = bf.knnMatch(des1, des2, k=2)
                    good_matches = []
                    for m, n in raw_matches:
                        if m.distance < 0.72 * n.distance:
                            good_matches.append(m)

                    if len(good_matches) >= 8:
                        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                        # Find homography from image 2 to image 1
                        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 4.0)
                        if H is not None:
                            inliers = int(np.sum(mask)) if mask is not None else 0
                            if inliers >= 6:
                                arr2 = cv2.warpPerspective(arr2, H, (w1, h1))
                                alignment_performed = True
                                alignment_method = "FEATURE_SIFT_HOMOGRAPHY"
                                alignment_status = f"ALIGNED_RANSAC_{inliers}_INLIERS"
                                trans_matrix = H.tolist()
            except Exception as e:
                logger.warning(f"Homography alignment encountered error: {e}")
                warnings.append(f"Automated alignment failed: {str(e)}. Proceeding without homography.")

        # If dimensions still differ, resize arr2 to match arr1 for comparison
        if arr2.shape[:2] != (h1, w1):
            arr2 = cv2.resize(arr2, (w1, h1), interpolation=cv2.INTER_LINEAR)
            warnings.append(
                f"Comparison image dimensions ({w2}x{h2}) differed from primary ({w1}x{h1}). "
                "Rescaled comparison image to primary dimensions for delta calculation."
            )

        # Compute Absolute Pixel Difference
        diff_arr = np.abs(arr1.astype(np.float32) - arr2.astype(np.float32))
        gray1 = cv2.cvtColor(arr1, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(arr2, cv2.COLOR_RGB2GRAY)
        gray_diff = np.abs(gray1.astype(np.float32) - gray2.astype(np.float32))

        # Metrics
        total_pixels = h1 * w1
        diff_mask = gray_diff > payload.difference_threshold
        diff_count = int(np.sum(diff_mask))
        diff_pct = float((diff_count / total_pixels) * 100.0)

        mae = float(np.mean(gray_diff))
        rmse = float(np.sqrt(np.mean(gray_diff ** 2)))
        psnr = float(20 * math.log10(255.0 / (rmse + 1e-6))) if rmse > 0 else 100.0
        ssim_val = compute_ssim(gray1, gray2)

        # Generate Visual Difference Heatmap Artifact
        norm_diff = np.clip(gray_diff * 4.0, 0, 255).astype(np.uint8)  # amplify difference by 4x
        colorized = cv2.applyColorMap(norm_diff, cv2.COLORMAP_JET)
        # Alpha blend 50% with primary image
        blend = cv2.addWeighted(arr1, 0.5, cv2.cvtColor(colorized, cv2.COLOR_BGR2RGB), 0.5, 0)
        diff_img = Image.fromarray(blend)

        diff_buf = io.BytesIO()
        diff_img.save(diff_buf, format="PNG")
        diff_bytes = diff_buf.getvalue()
        diff_sha = compute_sha256_bytes(diff_bytes)

        artifact_filename = f"diff_{ev1.id[:6]}_{ev2.id[:6]}_{diff_sha[:8]}.png"
        target_path = self.storage.store_file(
            category="derivatives",
            filename=artifact_filename,
            file_bytes=diff_bytes,
        )

        import json
        comparison_analysis = Analysis(
            id=str(uuid.uuid4()),
            evidence_id=ev1.id,
            case_id=ev1.case_id,
            analysis_type="IMAGE_COMPARISON",
            algorithm_name=f"Q-TRACE Image Comparison ({alignment_method})",
            status="COMPLETED",
            config_json=json.dumps({"comparison_evidence_id": ev2.id, "alignment": alignment_method}),
            results_json=json.dumps({"mae": mae, "rmse": rmse, "psnr": psnr, "ssim": ssim_val, "diff_pct": diff_pct}),
            execution_time_ms=0.0,
        )
        self.db.add(comparison_analysis)

        artifact = Artifact(
            analysis_id=comparison_analysis.id,
            artifact_type="DIFFERENCE_MAP",
            file_path=str(target_path),
            stored_filename=artifact_filename,
            sha256_hash=diff_sha,
        )
        self.db.add(artifact)
        self.db.commit()
        self.db.refresh(artifact)

        # Extract Dual 4x4 Quantum Patches from highest discrepancy centroid
        if np.any(diff_mask):
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
                diff_mask.astype(np.uint8), connectivity=8
            )
            # Find largest connected difference blob
            if num_labels > 1:
                largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
                cx, cy = int(centroids[largest_label][0]), int(centroids[largest_label][1])
            else:
                cy, cx = h1 // 2, w1 // 2
        else:
            cy, cx = h1 // 2, w1 // 2

        py1 = max(0, min(h1 - 4, cy - 2))
        px1 = max(0, min(w1 - 4, cx - 2))

        q_patch_a = (gray1[py1 : py1 + 4, px1 : px1 + 4] >> 4).tolist()
        q_patch_b = (gray2[py1 : py1 + 4, px1 : px1 + 4] >> 4).tolist()

        return ImageComparisonResponse(
            primary_evidence_id=ev1.id,
            comparison_evidence_id=ev2.id,
            identical_dimensions=identical_dims,
            primary_dimensions={"width": w1, "height": h1},
            comparison_dimensions={"width": w2, "height": h2},
            alignment_performed=alignment_performed,
            alignment_method=alignment_method,
            alignment_status=alignment_status,
            transformation_matrix=trans_matrix,
            difference_pixel_count=diff_count,
            difference_percentage=round(diff_pct, 2),
            mean_absolute_error=round(mae, 3),
            root_mean_square_error=round(rmse, 3),
            psnr_db=round(psnr, 2),
            ssim_score=round(ssim_val, 4),
            artifact_id=artifact.id,
            artifact_filename=artifact_filename,
            suggested_quantum_patch_a=q_patch_a,
            suggested_quantum_patch_b=q_patch_b,
            warnings=warnings,
        )
