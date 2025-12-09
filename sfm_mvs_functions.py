import os
import subprocess
from pathlib import Path

# --- Configuration ---
COLMAP_EXECUTABLE = "colmap" # Assumes 'colmap' is in your system PATH

def run_command(command, stage_name):
    """
    Runs a COLMAP command and prints its output/errors.
    """
    print(f"\n--- Starting {stage_name} ---")
    try:
        # Run the command
        process = subprocess.run(
            command,
            check=True,
            shell=True,
            capture_output=True,
            text=True
        )
        print(f"--- {stage_name} Completed Successfully ---")
        # print("Output:\n", process.stdout) # Uncomment for detailed output
    except subprocess.CalledProcessError as e:
        print(f"!!! Error during {stage_name} !!!")
        print(f"Command: {e.cmd}")
        print("Stderr:\n", e.stderr)
        raise
    except FileNotFoundError:
        print(f"!!! Error: COLMAP executable not found. Check if '{COLMAP_EXECUTABLE}' is in your PATH. !!!")
        raise

# --- SFM Functions ---

def feature_extraction(database_path: Path, image_path: Path):
    """Extracts local features (e.g., SIFT) from images."""
    command = (
        f"{COLMAP_EXECUTABLE} feature_extractor "
        f"--database_path {database_path} "
        f"--image_path {image_path} "
        f"--ImageReader.camera_model SIMPLE_RADIAL " # A common, robust model
        f"--SiftExtraction.num_threads 8"
    )
    run_command(command, "Feature Extraction")

def feature_matching(database_path: Path):
    """Matches features between all image pairs."""
    command = (
        f"{COLMAP_EXECUTABLE} exhaustive_matcher "
        f"--database_path {database_path} "
        f"--SiftMatching.num_threads 8"
    )
    run_command(command, "Feature Matching")

def sparse_reconstruction(database_path: Path, image_path: Path, sparse_output_path: Path):
    """Performs the main Structure-from-Motion (SFM) triangulation."""
    # Ensure output path exists
    sparse_output_path.mkdir(exist_ok=True)
    
    command = (
        f"{COLMAP_EXECUTABLE} mapper "
        f"--database_path {database_path} "
        f"--image_path {image_path} "
        f"--output_path {sparse_output_path} "
        f"--Mapper.num_threads 8 "
        f"--Mapper.min_num_matches 15" # Robust setting
    )
    run_command(command, "Sparse Reconstruction (Mapper)")

# --- MVS Functions ---

def image_undistortion(image_path: Path, sparse_input_path: Path, dense_output_path: Path):
    """Prepares images and camera parameters for dense reconstruction."""
    # The sparse model is typically stored in a sub-folder named '0'
    model_path = sparse_input_path / "0" 
    
    command = (
        f"{COLMAP_EXECUTABLE} image_undistorter "
        f"--image_path {image_path} "
        f"--input_path {model_path} "
        f"--output_path {dense_output_path} "
        f"--output_type COLMAP" # Saves results in COLMAP format for MVS
    )
    run_command(command, "Image Undistortion")

def patch_match_stereo(dense_workspace_path: Path):
    """Computes depth maps for all images using PatchMatch Stereo."""
    stereo_output_path = dense_workspace_path / "stereo"
    stereo_output_path.mkdir(exist_ok=True)
    
    command = (
        f"{COLMAP_EXECUTABLE} patch_match_stereo "
        f"--workspace_path {dense_workspace_path} "
        f"--workspace_format COLMAP "
        f"--output_path {stereo_output_path} "
        f"--PatchMatchStereo.num_threads 8 "
        f"--PatchMatchStereo.max_image_size 2000" # Use full size for better results
        f"--PatchMatchStereo.gpu_index -1"
    )
    run_command(command, "PatchMatch Stereo (Depth Maps)")

def stereo_fusion(dense_workspace_path: Path, fused_output_file: Path):
    """Fuses the computed depth maps into a single dense point cloud."""
    stereo_input_path = dense_workspace_path / "stereo"
    
    command = (
        f"{COLMAP_EXECUTABLE} stereo_fusion "
        f"--workspace_path {dense_workspace_path} "
        f"--output_path {fused_output_file} "
        f"--input_path {stereo_input_path} "
        f"--StereoFusion.num_threads 8"
    )
    run_command(command, "Stereo Fusion (Dense Point Cloud)")

def poisson_mesher(input_ply_file: Path, output_ply_file: Path):
    """(Optional) Converts the dense point cloud into a triangular mesh."""
    command = (
        f"{COLMAP_EXECUTABLE} poisson_mesher "
        f"--input_path {input_ply_file} "
        f"--output_path {output_ply_file} "
        f"--PoissonMeshing.num_threads 8"
    )
    run_command(command, "Poisson Meshing (3D Model)")