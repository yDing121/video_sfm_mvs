# mvs_pipeline.py
from __future__ import annotations
import platform
import subprocess
from pathlib import Path

from config import PipelineConfig


def _exe_name(base: str) -> str:
    """Add .exe on Windows."""
    if platform.system().lower().startswith("win"):
        return base + ".exe"
    return base


def _bin(config: PipelineConfig, base: str) -> str:
    """Resolve OpenMVS binary path (either from bin dir or from PATH)."""
    exe = _exe_name(base)
    if config.openmvs_bin_dir is not None:
        return str((config.openmvs_bin_dir / exe).resolve())
    return exe  # rely on PATH


def run_mvs(config: PipelineConfig) -> None:
    root = config.project_root
    sparse_dir = config.sparse_dir
    images_dir = config.images_dir

    if not (sparse_dir / "cameras.txt").is_file():
        raise FileNotFoundError(f"[MVS] Expected cameras.txt in {sparse_dir}; run SfM first.")
    if not images_dir.is_dir():
        raise FileNotFoundError(f"[MVS] Images dir not found: {images_dir}")

    scene_colmap = root / "scene_colmap.mvs"
    scene_dense = root / "scene_dense.mvs"
    scene_mesh = root / "scene_mesh.mvs"
    scene_mesh_refined = root / "scene_mesh_refined.mvs"
    scene_obj = root / "scene.obj"

    # 1) COLMAP -> OpenMVS interface
    print("[MVS] Running InterfaceCOLMAP")
    cmd = [
        _bin(config, "InterfaceCOLMAP"),
        "--working-folder", str(root),
        "--input-file", str(root),
        "--output-file", str(scene_colmap),
    ]
    subprocess.run(cmd, check=True)

    # 2) Dense point cloud
    print("[MVS] Running DensifyPointCloud")
    cmd = [
        _bin(config, "DensifyPointCloud"),
        "--input-file", str(scene_colmap),
        "--working-folder", str(root),
        "--output-file", str(scene_dense),
        "--archive-type", "-1",
    ]
    subprocess.run(cmd, check=True)

    # 3) Mesh reconstruction
    print("[MVS] Running ReconstructMesh")
    cmd = [
        _bin(config, "ReconstructMesh"),
        "--input-file", str(scene_dense),
        "--working-folder", str(root),
        "--output-file", str(scene_mesh),
    ]
    subprocess.run(cmd, check=True)

    # 4) Mesh refinement (optional but nice)
    print("[MVS] Running RefineMesh")
    cmd = [
        _bin(config, "RefineMesh"),
        "--resolution-level", "1",
        "--input-file", str(scene_mesh),
        "--working-folder", str(root),
        "--output-file", str(scene_mesh_refined),
    ]
    subprocess.run(cmd, check=True)

    # 5) Texture mesh (outputs OBJ)
    print("[MVS] Running TextureMesh")
    cmd = [
        _bin(config, "TextureMesh"),
        "--export-type", "obj",
        "--output-file", str(scene_obj),
        "--working-folder", str(root),
        "--input-file", str(scene_mesh_refined),
    ]
    subprocess.run(cmd, check=True)

    print(f"[MVS] Finished. Textured mesh: {scene_obj}")

