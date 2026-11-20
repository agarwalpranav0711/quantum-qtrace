"""
Q-TRACE Part 9: End-to-End System Performance & Throughput Benchmark
Measures latency across pipeline stages across multiple image resolutions:
256x256, 512x512, 1024x1024, 1920x1080.
Evaluates: Ingestion, SHA-256 Hashing, Forensic Suite (ELA, Noise, CMFD), Canvas Crop/SIFT, and Dossier PDF Generation.
"""

import time
import json
import csv
import sys
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import cv2

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.storage.service import StorageService
from backend.app.services.integrity import compute_sha256_file
from backend.app.forensics.ela_analyzer import ErrorLevelAnalyzer
from backend.app.forensics.noise_analyzer import NoiseAnalyzer
from backend.app.forensics.copy_move_analyzer import CopyMoveAnalyzer
from backend.app.forensics.consensus_fusion import fuse_candidate_regions
from backend.app.services.pdf_generator import ForensicPDFGenerator


def generate_benchmark_image(width: int, height: int) -> bytes:
    """Generate a realistic test image with vehicle textures."""
    y, x = np.mgrid[0:height, 0:width]
    base = 130 + 35 * (np.sin(x / 60.0) * np.cos(y / 70.0))
    img = np.dstack([base, base + 10, base + 20]).astype(np.float32)
    noise = np.random.normal(0, 3.0, (height, width, 3))
    arr = np.clip(img + noise, 0, 255).astype(np.uint8)
    # Add high-contrast lines simulating vehicle contours
    cv2.line(arr, (0, int(height * 0.3)), (width, int(height * 0.3)), (30, 30, 40), 2)
    cv2.line(arr, (int(width * 0.5), 0), (int(width * 0.5), height), (40, 40, 50), 2)

    _, enc = cv2.imencode(".jpg", arr, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    return enc.tobytes()


def main():
    print("=" * 70)
    print("Q-TRACE Part 9: System Performance & Resolution Scaling Benchmark")
    print("=" * 70)

    out_dir = PROJECT_ROOT / "results" / "part9" / "system"
    out_dir.mkdir(parents=True, exist_ok=True)

    resolutions = [
        ("256x256", 256, 256),
        ("512x512", 512, 512),
        ("1024x1024", 1024, 1024),
        ("1920x1080 (FHD)", 1920, 1080),
    ]

    ela_analyzer = ErrorLevelAnalyzer()
    noise_analyzer = NoiseAnalyzer()
    cmfd_analyzer = CopyMoveAnalyzer()

    temp_storage_dir = Path(tempfile.mkdtemp(prefix="qtrace_sys_bench_"))
    storage = StorageService(root_path=temp_storage_dir)

    perf_records = []

    print("\n[1/2] Benchmarking Pipeline Stages Across Resolutions...")

    for name, w, h in resolutions:
        print(f"  Testing Resolution: {name} ({w}x{h})...")
        img_bytes = generate_benchmark_image(w, h)
        file_size_kb = len(img_bytes) / 1024.0

        # Stage 1: File Storage Ingestion
        calc_sha = hashlib.sha256(img_bytes).hexdigest()
        t0 = time.perf_counter()
        stored_path, stored_filename = storage.store_original(img_bytes, calc_sha, f"bench_{w}x{h}.jpg")
        ingestion_ms = (time.perf_counter() - t0) * 1000.0

        # Stage 2: SHA-256 Cryptographic Verification
        t0 = time.perf_counter()
        verified_sha = compute_sha256_file(stored_path)
        assert verified_sha == calc_sha
        sha_ms = (time.perf_counter() - t0) * 1000.0

        # Stage 3: ELA Analysis
        t0 = time.perf_counter()
        ela_res = ela_analyzer.analyze(stored_path, img_bytes, {"quality": 95, "scale": 15}, storage, f"ela_{w}x{h}")
        ela_ms = (time.perf_counter() - t0) * 1000.0

        # Stage 4: Noise Analysis
        t0 = time.perf_counter()
        noise_res = noise_analyzer.analyze(stored_path, img_bytes, {}, storage, f"noise_{w}x{h}")
        noise_ms = (time.perf_counter() - t0) * 1000.0

        # Stage 5: CMFD Analysis
        t0 = time.perf_counter()
        cmfd_res = cmfd_analyzer.analyze(stored_path, img_bytes, {}, storage, f"cmfd_{w}x{h}")
        cmfd_ms = (time.perf_counter() - t0) * 1000.0

        # Stage 6: Consensus Fusion
        t0 = time.perf_counter()
        fusion_dict = {"ela": ela_res, "noise": noise_res, "cmfd": cmfd_res}
        fused_rois = fuse_candidate_regions(fusion_dict, iou_threshold=0.20)
        fusion_ms = (time.perf_counter() - t0) * 1000.0

        # Stage 7: Canvas Interactive Patch / SIFT Extraction
        t0 = time.perf_counter()
        img_cv = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        sift = cv2.SIFT_create(nfeatures=500)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        kps, descs = sift.detectAndCompute(gray, None)
        canvas_sift_ms = (time.perf_counter() - t0) * 1000.0

        total_forensic_pipeline_ms = ela_ms + noise_ms + cmfd_ms + fusion_ms

        perf_records.append({
            "resolution": name,
            "width": w,
            "height": h,
            "file_size_kb": round(file_size_kb, 2),
            "ingestion_ms": round(ingestion_ms, 2),
            "sha256_ms": round(sha_ms, 2),
            "ela_ms": round(ela_ms, 2),
            "noise_ms": round(noise_ms, 2),
            "cmfd_ms": round(cmfd_ms, 2),
            "consensus_ms": round(fusion_ms, 2),
            "total_forensic_ms": round(total_forensic_pipeline_ms, 2),
            "canvas_sift_ms": round(canvas_sift_ms, 2),
            "sift_keypoints_found": len(kps) if kps else 0,
        })

    # Stage 8: PDF Report Generation Benchmark
    print("\n[2/2] Benchmarking Multi-Page Cryptographic PDF Generation...")
    pdf_out_path = temp_storage_dir / "bench_dossier.pdf"
    
    # Accurate dossier snapshot data structure
    dossier_data = {
        "title": "Performance Evaluation Forensic Dossier",
        "case_number": "QC-2026-PERF-BENCH",
        "dossier_number": "DOS-2026-PERF-001",
        "case_title": "Automated Claims Performance Benchmark Case",
        "author": "Lead Forensic Examiner",
        "version": 1,
        "confidentiality_level": "RESTRICTED",
        "created_at": "2026-11-20T12:00:00Z",
        "investigation_scope": "Controlled system throughput test across resolutions and cryptographic integrity verification.",
        "executive_summary": "Photographic evidence was examined using multi-scale signal analysis and cryptographic integrity checks.",
        "examiner_conclusions": "Technical measurements documented herein provide objective decision support for the claim audit.",
        "recommendations": "Corroborate findings with physical vehicle inspection and surveyor work orders.",
        "limitations": "Image analysis cannot establish legal intent or identify the physical individual operating the camera.",
        "evidence_register": [
            {
                "id": "evid-bench-01",
                "original_filename": "vehicle_bumper_front.jpg",
                "stored_filename": "orig_vehicle_bumper_front.jpg",
                "file_size": 482100,
                "width": 1920,
                "height": 1080,
                "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "status": "VERIFIED_AUTHENTIC",
                "created_at": "2026-11-20T12:00:00Z",
                "mime_type": "image/jpeg",
            }
        ],
        "chain_of_custody_events": [
            {
                "timestamp": "2026-11-20T12:00:00Z",
                "action": "EVIDENCE_INGESTION_WORM",
                "performed_by": "System Ingestion Daemon",
                "evidence_id": "evid-bench-01",
                "verification_status": "VERIFIED_MATCH",
                "notes": "Cryptographic bitstream preserved with read-only WORM attribute.",
            }
        ],
        "forensic_methodology": [
            {
                "technique": "Error Level Analysis (ELA)",
                "category": "Compression Forensic",
                "version": "1.0.0",
                "description": "Multi-pass recompression residual analysis detecting localized compression differences.",
                "applicability": "JPEG images only",
            }
        ],
        "findings_categorized": {
            "facts": [{"title": "Bitstream Invariance", "description": "SHA-256 match confirmed against storage ledger."}],
            "observations": [{"title": "High Frequency Edge Residuals", "description": "Uniform gradient variance observed."}],
            "indicators": [{"title": "Compression Artifact Anomaly", "description": "Localized high-frequency compression residuals observed."}],
            "hypotheses": [{"title": "Secondary Resave Hypothesis", "description": "Indicative of secondary image compression."}],
        },
        "roi_evidence": [],
        "image_comparisons": [],
        "quantum_experiments": [
            {
                "analysis_id": "ana-quant-01",
                "architecture": "16-qubit Dedicated Register",
                "qubits": 16,
                "shots_used": 1024,
                "fidelity": 1.0,
                "difference_count": 0,
                "execution_time_ms": 31.43,
            }
        ],
        "examiner_notes": [
            {
                "id": "note-01",
                "author": "Examiner Miller",
                "content": "Initial baseline integrity and benchmark validation note.",
                "created_at": "2026-11-20T12:05:00Z",
            }
        ],
        "appendices": {
            "runtime_environment": {
                "version": "1.9.0",
                "python": "3.11.9",
                "opencv": "5.1.0",
                "reportlab": "5.1.0",
                "qiskit": "2.6.2",
                "database": "SQLite WAL",
            }
        },
        "completeness_disclosure": {
            "evidence_included": 1,
            "evidence_omitted": 0,
            "notes": "All benchmark evidentiary items processed successfully.",
        },
    }

    pdf_timings_ms = []
    for _ in range(5):
        t0 = time.perf_counter()
        pdf_gen = ForensicPDFGenerator(pdf_out_path)
        _ = pdf_gen.generate(dossier_data)
        pdf_timings_ms.append((time.perf_counter() - t0) * 1000.0)

    mean_pdf_ms = float(np.mean(pdf_timings_ms))
    pdf_size_kb = pdf_out_path.stat().st_size / 1024.0

    # Save CSV
    sys_csv = out_dir / "system_performance_benchmark.csv"
    with open(sys_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(perf_records[0].keys()))
        writer.writeheader()
        writer.writerows(perf_records)

    # Save JSON
    sys_json = out_dir / "system_performance_benchmark.json"
    summary_output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "resolution_benchmarks": perf_records,
        "pdf_generation_benchmark": {
            "mean_latency_ms": round(mean_pdf_ms, 2),
            "min_latency_ms": round(float(np.min(pdf_timings_ms)), 2),
            "max_latency_ms": round(float(np.max(pdf_timings_ms)), 2),
            "pdf_file_size_kb": round(pdf_size_kb, 2),
        }
    }
    with open(sys_json, "w", encoding="utf-8") as f:
        json.dump(summary_output, f, indent=2)

    print(f"\n[OK] System performance results saved to {out_dir}:")
    print(f"  - {sys_csv.name}")
    print(f"  - {sys_json.name}")
    print(f"  PDF generation: {round(mean_pdf_ms, 2)} ms ({round(pdf_size_kb, 2)} KB)")
    print("System performance benchmark complete.")


if __name__ == "__main__":
    main()
