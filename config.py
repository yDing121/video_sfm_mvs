# config.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PipelineConfig:
    project_root: Path
    images_dir: Path
    database_path: Path
    sparse_dir: Path
    openmvs_bin_dir: Optional[Path] = None  # folder containing InterfaceCOLMAP, DensifyPointCloud, ...

    @classmethod
    def from_project_root(cls, root: str | Path, openmvs_bin_dir: str | Path | None = None) -> "PipelineConfig":
        root = Path(root).resolve()
        bin_dir = Path(openmvs_bin_dir).resolve() if openmvs_bin_dir else None
        return cls(
            project_root=root,
            images_dir=root / "images",
            database_path=root / "database.db",
            sparse_dir=root / "sparse",
            openmvs_bin_dir=bin_dir,
        )
