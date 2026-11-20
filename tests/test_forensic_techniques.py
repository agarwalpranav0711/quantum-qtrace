"""Unit and scientific validation tests for classical image forensic techniques."""

import io
import numpy as np
import pytest
from pathlib import Path
from PIL import Image, ImageDraw
import cv2

from backend.app.storage.service import StorageService
from backend.app.forensics.metadata_analyzer import MetadataAnalyzer
from backend.app.forensics.ela_analyzer import ErrorLevelAnalyzer
from backend.app.forensics.noise_analyzer import NoiseAnalyzer
from backend.app.forensics.copy_move_analyzer import CopyMoveAnalyzer
from backend.app.forensics.statistics_analyzer import StatisticsAnalyzer
from backend.app.forensics.perceptual_hash_analyzer import (
    PerceptualHashAnalyzer,
    compute_ahash,
    compute_dhash,
    compute_phash,
    hamming_distance,
)
from backend.app.forensics.resampling_analyzer import ResamplingAnalyzer
from backend.app.forensics.consensus_fusion import fuse_candidate_regions, calculate_iou
from backend.app.forensics.schemas import ForensicStatus, RegionOfInterest


@pytest.fixture(scope="module")
def storage(tmp_path_factory):
    """Storage service fixture with isolated temporary folder."""
    root = tmp_path_factory.mktemp("forensic_tech_storage")
    return StorageService(root_path=root)


def make_clean_jpeg(width=256, height=256, quality=95) -> bytes:
    """Create a realistic synthetic vehicle panel photograph (smooth gradient + texture)."""
    img = Image.new("RGB", (width, height), color=(180, 180, 180))
    draw = ImageDraw.Draw(img)
    # Draw body panel lines
    draw.line([(0, 100), (width, 100)], fill=(40, 40, 40), width=3)
    draw.line([(50, 0), (50, height)], fill=(40, 40, 40), width=2)
    # Add some textured noise
    arr = np.array(img, dtype=np.int16)
    noise = np.random.normal(0, 4, arr.shape).astype(np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    res = Image.fromarray(arr)

    buf = io.BytesIO()
    res.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def make_spliced_jpeg(width=256, height=256) -> bytes:
    """Create an image with a foreign spliced high-compression block inserted."""
    # Base image at quality 95
    base = Image.new("RGB", (width, height), color=(200, 200, 200))
    buf_base = io.BytesIO()
    base.save(buf_base, format="JPEG", quality=95)
    base_loaded = Image.open(buf_base).copy()

    # Foreign patch created and saved at low quality 40
    patch = Image.new("RGB", (64, 64), color=(50, 50, 220))
    buf_patch = io.BytesIO()
    patch.save(buf_patch, format="JPEG", quality=40)
    patch_loaded = Image.open(buf_patch)

    # Paste patch onto base image
    base_loaded.paste(patch_loaded, (100, 100))

    # Re-save final composite at quality 95
    final_buf = io.BytesIO()
    base_loaded.save(final_buf, format="JPEG", quality=95)
    return final_buf.getvalue()


def make_cloned_image(width=300, height=300) -> bytes:
    """Create an image with a duplicated high-texture patch (copy-move forgery)."""
    rng = np.random.default_rng(42)
    arr = np.full((height, width, 3), 150, dtype=np.uint8)
    # Create high-texture feature patch with deterministic RNG (dent/scratch pattern)
    patch = rng.integers(20, 230, (40, 40, 3), dtype=np.uint8)

    # Source location
    arr[40:80, 40:80] = patch
    # Cloned destination location (shift by dx=120, dy=100)
    arr[140:180, 160:200] = patch

    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# --- Unit Tests ---

def test_metadata_analyzer_clean_and_exif(storage: StorageService):
    """Test metadata analysis on clean image and image with simulated EXIF software tag."""
    analyzer = MetadataAnalyzer()

    # 1. Clean image without EXIF
    clean_bytes = make_clean_jpeg()
    res_clean = analyzer.analyze(Path("dummy.jpg"), clean_bytes, {}, storage, "a1")
    assert res_clean.status == ForensicStatus.NO_ANOMALY_DETECTED
    assert res_clean.metrics["format"] == "JPEG"
    assert res_clean.metrics["has_exif"] is False

    # 2. Image with EXIF software tag indicating Photoshop
    img = Image.new("RGB", (128, 128), color=(100, 100, 100))
    exif = img.getexif()
    exif[0x0131] = "Adobe Photoshop 2024 (Windows)"
    exif[0x010F] = "Nikon"
    exif[0x0110] = "D850"

    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    exif_bytes = buf.getvalue()

    res_exif = analyzer.analyze(Path("ps.jpg"), exif_bytes, {}, storage, "a2")
    assert res_exif.status == ForensicStatus.POTENTIAL_INDICATOR_DETECTED
    assert res_exif.metrics["has_exif"] is True
    assert len(res_exif.indicators) >= 1
    assert "Adobe Photoshop" in res_exif.indicators[0].description


def test_ela_analyzer_clean_vs_spliced(storage: StorageService):
    """Test ELA on clean JPEG vs image with foreign spliced patch."""
    analyzer = ErrorLevelAnalyzer()

    # 1. Clean JPEG
    clean_bytes = make_clean_jpeg()
    res_clean = analyzer.analyze(Path("clean.jpg"), clean_bytes, {"quality": 95, "scale": 15}, storage, "a3")
    assert res_clean.status in [ForensicStatus.NO_ANOMALY_DETECTED, ForensicStatus.POTENTIAL_INDICATOR_DETECTED]
    assert len(res_clean.artifacts) == 1
    assert res_clean.artifacts[0].artifact_type == "ELA_HEATMAP"
    assert res_clean.metrics["quality_setting"] == 95

    # 2. Spliced JPEG (contains low-quality patch in high-quality base)
    spliced_bytes = make_spliced_jpeg()
    res_spliced = analyzer.analyze(Path("spliced.jpg"), spliced_bytes, {"quality": 95, "scale": 15}, storage, "a4")
    assert res_spliced.metrics["mean_error"] >= 0.0
    assert len(res_spliced.artifacts) == 1
    # Check that quantized 4x4 patch values are in [0, 15]
    if res_spliced.candidate_regions:
        q_patch = res_spliced.candidate_regions[0].suggested_quantum_patch
        assert len(q_patch) == 4
        assert len(q_patch[0]) == 4
        assert all(0 <= v <= 15 for row in q_patch for v in row)


def test_noise_analyzer(storage: StorageService):
    """Test noise analysis and variance metrics."""
    analyzer = NoiseAnalyzer()
    img_bytes = make_clean_jpeg(width=160, height=160)

    res = analyzer.analyze(Path("noise.jpg"), img_bytes, {"block_size": 16}, storage, "a5")
    assert res.status in [ForensicStatus.NO_ANOMALY_DETECTED, ForensicStatus.POTENTIAL_INDICATOR_DETECTED]
    assert res.metrics["global_median_noise_variance"] >= 0.0
    assert len(res.artifacts) == 1
    assert res.artifacts[0].artifact_type == "NOISE_HEATMAP"


def test_copy_move_analyzer_cloned_regions(storage: StorageService):
    """Test Copy-Move detection on image with cloned feature patches."""
    analyzer = CopyMoveAnalyzer()
    cloned_bytes = make_cloned_image()

    res = analyzer.analyze(Path("cloned.png"), cloned_bytes, {"min_spatial_distance": 25.0, "min_cluster_size": 2}, storage, "a6")
    assert res.metrics["feature_detector"] in ["SIFT", "ORB"]
    assert len(res.artifacts) == 1
    assert res.artifacts[0].artifact_type == "CMFD_MATCHES"
    # Should detect cloned keypoints
    assert res.metrics["keypoint_count"] > 10


def test_statistics_analyzer(storage: StorageService):
    """Test multi-channel statistics and histogram plotting."""
    analyzer = StatisticsAnalyzer()
    clean_bytes = make_clean_jpeg()

    res = analyzer.analyze(Path("stats.jpg"), clean_bytes, {}, storage, "a7")
    assert res.status in [ForensicStatus.NO_ANOMALY_DETECTED, ForensicStatus.POTENTIAL_INDICATOR_DETECTED]
    assert "luminance" in res.metrics["channels"]
    assert res.metrics["channels"]["luminance"]["entropy_bits"] > 2.0
    assert len(res.artifacts) == 1
    assert res.artifacts[0].artifact_type == "HISTOGRAM_PLOT"


def test_perceptual_hash_analyzer(storage: StorageService):
    """Test perceptual hashes: identity, compression invariance, and divergence on distinct scenes."""
    analyzer = PerceptualHashAnalyzer()

    # 1. Base image
    img1_bytes = make_clean_jpeg(width=128, height=128, quality=90)
    res1 = analyzer.analyze(Path("img1.jpg"), img1_bytes, {}, storage, "a8")
    phash1 = res1.metrics["phash"]
    assert len(phash1) == 16

    # 2. Re-compressed version of exact same scene
    loaded = Image.open(io.BytesIO(img1_bytes))
    buf2 = io.BytesIO()
    loaded.save(buf2, format="JPEG", quality=60)
    img1_recompressed = buf2.getvalue()
    res2 = analyzer.analyze(Path("img2.jpg"), img1_recompressed, {"reference_phash": phash1}, storage, "a9")
    phash2 = res2.metrics["phash"]

    # Hamming distance between re-compressed versions of same image should be low (<= 14)
    dist = hamming_distance(phash1, phash2)
    assert dist <= 14

    # 3. Completely different scene
    img3 = Image.new("RGB", (128, 128), color=(0, 0, 0))
    draw = ImageDraw.Draw(img3)
    draw.polygon([(10, 10), (100, 20), (50, 100)], fill=(255, 255, 255))
    buf3 = io.BytesIO()
    img3.save(buf3, format="JPEG")
    res3 = analyzer.analyze(Path("img3.jpg"), buf3.getvalue(), {"reference_phash": phash1}, storage, "a10")
    phash3 = res3.metrics["phash"]
    dist_diff = hamming_distance(phash1, phash3)
    assert dist_diff >= 20
    assert dist < dist_diff


def test_resampling_analyzer(storage: StorageService):
    """Test edge gradient magnitude and Laplacian variance analysis."""
    analyzer = ResamplingAnalyzer()
    clean_bytes = make_clean_jpeg()

    res = analyzer.analyze(Path("edge.jpg"), clean_bytes, {}, storage, "a11")
    assert res.metrics["global_laplacian_variance"] >= 0.0
    assert len(res.artifacts) == 1
    assert res.artifacts[0].artifact_type == "EDGE_GRADIENT_MAP"


def test_consensus_fusion_iou():
    """Test IoU calculation and consensus region clustering."""
    box1 = RegionOfInterest(roi_id="R1", x=10, y=10, width=50, height=50, score=0.8, contributing_techniques=["ELA"])
    box2 = RegionOfInterest(roi_id="R2", x=20, y=20, width=50, height=50, score=0.7, contributing_techniques=["Noise"])
    box_far = RegionOfInterest(roi_id="R3", x=200, y=200, width=40, height=40, score=0.6, contributing_techniques=["ELA"])

    iou = calculate_iou(box1, box2)
    assert iou > 0.3  # Overlapping

    iou_far = calculate_iou(box1, box_far)
    assert iou_far == 0.0
