# sfm_pipeline.py
from __future__ import annotations
import subprocess
from pathlib import Path

import pycolmap  # pip install pycolmap

from config import PipelineConfig


def run_sfm(config: PipelineConfig) -> None:
    project_root = config.project_root
    images_dir = config.images_dir
    database_path = config.database_path
    sparse_dir = config.sparse_dir

    project_root.mkdir(parents=True, exist_ok=True)
    sparse_dir.mkdir(parents=True, exist_ok=True)

    if not images_dir.is_dir():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")

    if database_path.exists():
        print(f"[SfM] Removing existing database: {database_path}")
        database_path.unlink()

    print(f"[SfM] Extracting features from images in {images_dir}")
    pycolmap.extract_features(
        database_path=str(database_path),
        image_path=str(images_dir),
        camera_mode=pycolmap.CameraMode.SINGLE,  # single moving camera (video)
        camera_model="PINHOLE",                  # required by InterfaceCOLMAP/OpenMVS tutorials
    )

    print("[SfM] Matching features sequentially (video-style)")
    pycolmap.match_sequential(
        database_path=str(database_path),
    )

    print(f"[SfM] Running incremental mapping, output -> {sparse_dir}")
    recons = pycolmap.incremental_mapping(
        database_path=str(database_path),
        image_path=str(images_dir),
        output_path=str(sparse_dir),
    )

    print(f"[SfM] Number of reconstructions: {len(recons)}")

    # incremental_mapping writes dirs sparse/0, sparse/1, ...
    submodels = [p for p in sparse_dir.iterdir() if p.is_dir()]
    if not submodels:
        raise RuntimeError(f"[SfM] No sparse reconstructions found in {sparse_dir}")

    # pick first model (you can change this heuristic if needed)
    main_model_dir = sorted(submodels)[0]
    print(f"[SfM] Using main sparse model: {main_model_dir}")

    # Convert to TXT format so OpenMVS' InterfaceCOLMAP can read it
    # Equivalent to:
    #   colmap model_converter \
    #     --input_path sparse/0 \
    #     --output_path sparse \
    #     --output_type TXT
    print("[SfM] Converting COLMAP model (binary -> TXT) via colmap model_converter")
    cmd = [
        "colmap", "model_converter",
        "--input_path", str(main_model_dir),
        "--output_path", str(sparse_dir),
        "--output_type", "TXT",
    ]
    subprocess.run(cmd, check=True)
    print("[SfM] model_converter finished; cameras.txt, images.txt, points3D.txt should be in sparse/")
