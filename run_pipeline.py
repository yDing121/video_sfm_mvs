import os
from pathlib import Path
from sfm_mvs_functions import (
    feature_extraction, feature_matching, sparse_reconstruction,
    image_undistortion, patch_match_stereo, stereo_fusion, poisson_mesher
)

def setup_paths():
    """Defines and creates all necessary directories."""
    # Assuming this script is run from the 'colmap_pipeline' folder
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"

    # Define paths
    image_dir = data_dir / "images"
    database_file = data_dir / "database" / "database.db"
    sparse_dir = data_dir / "sparse"
    dense_dir = data_dir / "dense"

    # Ensure all directories exist
    data_dir.mkdir(exist_ok=True)
    image_dir.mkdir(exist_ok=True)
    database_file.parent.mkdir(exist_ok=True)
    sparse_dir.mkdir(exist_ok=True)
    dense_dir.mkdir(exist_ok=True)

    print(f"--- Project Directory Setup Complete (Path: {data_dir}) ---")
    
    return image_dir, database_file, sparse_dir, dense_dir

def main():
    """Runs the full SFM and MVS pipeline."""
    try:
        # 1. Setup paths
        image_path, database_path, sparse_output_path, dense_output_path = setup_paths()
        
        # Check if images are present
        if not any(image_path.iterdir()):
            print("\n!!! ERROR: The 'data/images' folder is empty. Place your images there and run again. !!!")
            return

        print("\n================ STARTING SFM PIPELINE ================")
        
        # 2. SFM Pipeline (Sparse Reconstruction)
        feature_extraction(database_path, image_path)
        feature_matching(database_path)
        sparse_reconstruction(database_path, image_path, sparse_output_path)
        
        print("\n================ SFM COMPLETE. STARTING MVS PIPELINE ================")

        # 3. MVS Pipeline (Dense Reconstruction)
        fused_ply_file = dense_output_path / "fused.ply"
        mesh_ply_file = dense_output_path / "model.ply"
        
        image_undistortion(image_path, sparse_output_path, dense_output_path)
        patch_match_stereo(dense_output_path)
        stereo_fusion(dense_output_path, fused_ply_file)
        poisson_mesher(fused_ply_file, mesh_ply_file)

        print("\n================ PIPELINE FINISHED SUCCESSFULLY ================")
        print(f"Final Dense Point Cloud (PLY): {fused_ply_file}")
        print(f"Final 3D Mesh (PLY): {mesh_ply_file}")

    except Exception as e:
        print(f"\n!!! Pipeline failed due to an error: {e} !!!")

if __name__ == "__main__":
    main()