# run_pipeline.py
from __future__ import annotations
import argparse

from config import PipelineConfig
from sfm_pipeline import run_sfm
from mvs_pipeline import run_mvs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Video SfM/MVS pipeline (keyframes already extracted).")
    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        # required=True,
        help="Path to project root (must contain images/).",
    )
    parser.add_argument(
        "--openmvs-bin",
        type=str,
        default="/snap/bin",
        help="Directory containing OpenMVS binaries (InterfaceCOLMAP, DensifyPointCloud, ...). "
             "If omitted, assumes they are on PATH.",
    )
    parser.add_argument(
        "--skip-mvs",
        action="store_true",
        help="Run only SfM (COLMAP/pycolmap), skip OpenMVS step.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = PipelineConfig.from_project_root(
        root=args.project_root,
        openmvs_bin_dir=args.openmvs_bin or None,
    )

    print("=== Stage 1: SfM (pycolmap) ===")
    run_sfm(cfg)

    if not args.skip_mvs:
        print("=== Stage 2: MVS (OpenMVS) ===")
        run_mvs(cfg)
    else:
        print("[Runner] Skipping MVS as requested.")


if __name__ == "__main__":
    main()
