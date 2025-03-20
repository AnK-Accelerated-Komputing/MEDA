import numpy as np
import open3d as o3d
import pandas as pd
import os
import math
from pathlib import Path
import trimesh


def load_and_sample_stl(filename, sample_points=1000):
    try:
        mesh = o3d.io.read_triangle_mesh(filename)
        mesh.compute_vertex_normals()
        return mesh.sample_points_uniformly(number_of_points=sample_points)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def preprocess_pcd(pcd, voxel_size):
    # Downsample and estimate normals
    pcd_down = pcd.voxel_down_sample(voxel_size)
    pcd_down.estimate_normals()
    # Compute FPFH features
    radius_feature = voxel_size * 5
    fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, fpfh

def global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    # The mutual_filter parameter is added as the 5th argument (here set to False)
    return o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, 
        target_down,
        source_fpfh,
        target_fpfh,
        False,  # mutual_filter
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3,  # ransac_n
        [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(distance_threshold)
        ],
        o3d.pipelines.registration.RANSACConvergenceCriteria(4000000, 500)
    )

def execute_fast_global_registration(source_down, target_down, source_fpfh,
                                     target_fpfh, voxel_size):
    distance_threshold = voxel_size * 0.5
    print(":: Apply fast global registration with distance threshold %.3f" \
            % distance_threshold)
    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=distance_threshold))
    return result

def load_stl_as_point_cloud(stl_path, num_points=1000):
    """
    Load an STL file and convert it to a point cloud with specified number of points.
    Returns None if the file doesn't exist or fails to load.
    """
    try:
        if not os.path.exists(stl_path):
            return None
        
        # Load STL using trimesh
        mesh = trimesh.load_mesh(stl_path)
        
        # Sample points from the mesh
        points = mesh.sample(num_points)
        
        # Create Open3D point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        return pcd
    except Exception as e:
        print(f"Error loading {stl_path}: {e}")
        return None

def normalize_point_cloud(pcd):
    """
    Normalize the point cloud to fit within a unit cube.
    """
    if pcd is None:
        return None
    
    # Get points as numpy array
    points = np.asarray(pcd.points)
    
    # Calculate min and max for each dimension
    min_vals = np.min(points, axis=0)
    max_vals = np.max(points, axis=0)
    
    # Calculate range for each dimension
    ranges = max_vals - min_vals
    max_range = np.max(ranges)
    
    # Scale points to fit in unit cube
    scaled_points = (points - min_vals) / max_range
    
    # Create new normalized point cloud
    normalized_pcd = o3d.geometry.PointCloud()
    normalized_pcd.points = o3d.utility.Vector3dVector(scaled_points)
    
    return normalized_pcd

def point_cloud_distance(pcd1, pcd2):
    """
    Calculate the point cloud distance between two point clouds.
    Returns sqrt(3) if either point cloud is None.
    """
    if pcd1 is None or pcd2 is None:
        return math.sqrt(3)
    
    # Calculate distances from pcd1 to pcd2
    distances = np.asarray(pcd1.compute_point_cloud_distance(pcd2))
    return np.mean(distances)

def hausdorff_distance(pcd1, pcd2):
    """
    Calculate the Hausdorff distance between two point clouds.
    Returns sqrt(3) if either point cloud is None.
    """
    if pcd1 is None or pcd2 is None:
        return math.sqrt(3)
    
    # Calculate distances from pcd1 to pcd2
    distances1 = np.asarray(pcd1.compute_point_cloud_distance(pcd2))
    
    # Calculate distances from pcd2 to pcd1
    distances2 = np.asarray(pcd2.compute_point_cloud_distance(pcd1))
    
    # Hausdorff distance is the maximum of the two
    return max(np.max(distances1), np.max(distances2))

def compute_bounding_box(pcd):
    """
    Compute the axis-aligned bounding box for a point cloud.
    Returns None if the point cloud is None.
    """
    if pcd is None:
        return None
    
    # Get the axis-aligned bounding box
    aabb = pcd.get_axis_aligned_bounding_box()
    min_bound = aabb.min_bound
    max_bound = aabb.max_bound
    
    return (min_bound, max_bound)

def intersection_over_ground_truth(pcd1, pcd2):
    """
    Calculate the Intersection over Ground Truth (IoGT) between two point clouds.
    Returns 0 if either point cloud is None.
    """
    if pcd1 is None or pcd2 is None:
        return 0.0
    
    # Get bounding boxes
    bbox1 = compute_bounding_box(pcd1)
    bbox2 = compute_bounding_box(pcd2)
    
    if bbox1 is None or bbox2 is None:
        return 0.0
    
    min_bound1, max_bound1 = bbox1
    min_bound2, max_bound2 = bbox2
    
    # Calculate intersection volume
    intersection_min = np.maximum(min_bound1, min_bound2)
    intersection_max = np.minimum(max_bound1, max_bound2)
    
    # Check if boxes overlap
    if np.any(intersection_min > intersection_max):
        return 0.0
    
    intersection_volume = np.prod(intersection_max - intersection_min)
    
    # Calculate ground truth volume
    gt_volume = np.prod(max_bound2 - min_bound2)
    
    if gt_volume == 0:
        return 0.0
    
    return intersection_volume / gt_volume

def run_icp(source, target, trans_init, threshold):
    """
    Apply the Iterative Closest Point algorithm to align source to target.
    Returns aligned source and transformation matrix.
    Returns source and identity matrix if either point cloud is None.
    """
    if source is None or target is None:
        # Return identity transformation if either point cloud is None
        return source, np.identity(4)
    
    # Make deep copies to avoid modifying the original point clouds
    source_copy = o3d.geometry.PointCloud(source)
    target_copy = o3d.geometry.PointCloud(target)
    
    # Initial alignment using point-to-point ICP
    icp_result = o3d.pipelines.registration.registration_icp(
        source, target, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
    
    # Apply transformation to the source point cloud
    source_copy.transform(icp_result.transformation)
    
    return source_copy, icp_result.transformation

def calculate_iqr(data):
    """
    Calculate the Inter-Quartile Range (IQR) and quartiles for a given dataset.
    
    Returns:
        tuple: (Q1, median, Q3, IQR)
    """
    q1 = np.percentile(data, 25)
    median = np.percentile(data, 50)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    return q1, median, q3, iqr

def evaluate_stl_files(generated_dir, ground_truth_dir, output_csv, summary_csv):
    """
    Evaluate all generated STL files against their ground truth counterparts.
    """
    results = []
    
    # Get all ground truth files and extract base file names
    gt_files = list(Path(ground_truth_dir).glob("*_ground_truth.stl"))
    base_file_names = [f.stem.replace("_ground_truth", "") for f in gt_files]
    
    print(f"Found {len(base_file_names)} ground truth files")
    
    # Ensure we evaluate exactly 200 files (or however many are specified)
    total_files = 200
    processed_count = 0
    
    for base_name in base_file_names:
        if processed_count >= total_files:
            break
            
        gen_path = os.path.join(generated_dir, f"{base_name}.stl")
        gt_path = os.path.join(ground_truth_dir, f"{base_name}_ground_truth.stl")
        
        processed_count += 1
        print(f"Processing {base_name} ({processed_count}/{total_files})")
        
        # Load point clouds
        gen_pcd = load_and_sample_stl(gen_path)
        gt_pcd = load_and_sample_stl(gt_path)
        
        # Default values for failed compilations
        pc_dist = math.sqrt(3)
        haus_dist = math.sqrt(3)
        iogt = 0.0
        compilation_success = False
        
        # Preprocess: downsample and compute features
        
        voxel_size = 0.05
        if gen_pcd is not None and gt_pcd is not None:
            source_down, source_fpfh = preprocess_pcd(gen_pcd, voxel_size)
            target_down, target_fpfh = preprocess_pcd(gt_pcd, voxel_size)

            # Global registration using RANSAC to get an initial alignment
            ransac_result = global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size)
        # Refine alignment with ICP so that the blue box overlaps the orange perfectly
        threshold = voxel_size * 0.5
        
        if gen_pcd is not None and gt_pcd is not None:
            compilation_success = True
            # Apply ICP for alignment
            aligned_gen_pcd, _ = run_icp(gen_pcd, gt_pcd,ransac_result.transformation,threshold)
            # Normalize point clouds

            gen_pcd_norm = normalize_point_cloud(aligned_gen_pcd)
            gt_pcd_norm = normalize_point_cloud(gt_pcd)
            
            
            
            # Calculate metrics
            pc_dist = point_cloud_distance(gen_pcd_norm, gt_pcd_norm)
            haus_dist = hausdorff_distance(gen_pcd_norm, gt_pcd_norm)
            iogt = intersection_over_ground_truth(gen_pcd_norm, gt_pcd_norm)
        
        # Store results
        results.append({
            'file_name': base_name,
            'compilation_success': compilation_success,
            'point_cloud_distance': pc_dist,
            'hausdorff_distance': haus_dist,
            'iogt': iogt
        })
    
    # If we didn't get 200 files, pad with failed compilations
    while len(results) < total_files:
        missing_index = len(results) + 1
        results.append({
            'file_name': f"missing_{missing_index}",
            'compilation_success': False,
            'point_cloud_distance': math.sqrt(3),
            'hausdorff_distance': math.sqrt(3),
            'iogt': 0.0
        })
    
    # Convert results to DataFrame and save
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    
    # Print summary statistics
    print("\nEvaluation Summary:")
    print(f"Total files: {len(results)}")
    print(f"Successfully compiled: {df['compilation_success'].sum()}")
    print(f"Failed to compile: {len(results) - df['compilation_success'].sum()}")
    
    # Calculate statistics for successfully compiled files and save to summary CSV
    success_df = df[df['compilation_success']]
    
    # Initialize summary data dictionary
    summary_data = {
        'metric': [],
        'mean': [],
        'median': [],
        'q1': [],
        'q3': [],
        'iqr': [],
        'min': [],
        'max': []
    }
    
    # Add basic counts
    summary_data['metric'].append('total_files')
    summary_data['mean'].append(len(results))
    summary_data['median'].append(len(results))
    summary_data['q1'].append(None)
    summary_data['q3'].append(None)
    summary_data['iqr'].append(None)
    summary_data['min'].append(None)
    summary_data['max'].append(None)
    
    summary_data['metric'].append('successfully_compiled')
    summary_data['mean'].append(int(df['compilation_success'].sum()))
    summary_data['median'].append(int(df['compilation_success'].sum()))
    summary_data['q1'].append(None)
    summary_data['q3'].append(None)
    summary_data['iqr'].append(None)
    summary_data['min'].append(None)
    summary_data['max'].append(None)
    
    summary_data['metric'].append('compilation_success_rate')
    success_rate = df['compilation_success'].sum() / len(results)
    summary_data['mean'].append(round(success_rate, 4))
    summary_data['median'].append(None)
    summary_data['q1'].append(None)
    summary_data['q3'].append(None)
    summary_data['iqr'].append(None)
    summary_data['min'].append(None)
    summary_data['max'].append(None)
    
    if not success_df.empty:
        # Calculate and add statistics for each metric
        for metric in ['point_cloud_distance', 'hausdorff_distance', 'iogt']:
            data = success_df[metric]
            
            # Calculate statistics
            mean_val = data.mean()
            q1, median_val, q3, iqr_val = calculate_iqr(data)
            min_val = data.min()
            max_val = data.max()
            
            # Add to summary data
            summary_data['metric'].append(metric)
            summary_data['mean'].append(round(mean_val, 4))
            summary_data['median'].append(round(median_val, 4))
            summary_data['q1'].append(round(q1, 4))
            summary_data['q3'].append(round(q3, 4))
            summary_data['iqr'].append(round(iqr_val, 4))
            summary_data['min'].append(round(min_val, 4))
            summary_data['max'].append(round(max_val, 4))
        
        # Print detailed statistics
        print("\nMetrics for successfully compiled files:")
        
        # Mean statistics (original)
        print("\nMean Statistics:")
        print(f"Average Point Cloud Distance: {success_df['point_cloud_distance'].mean():.4f}")
        print(f"Average Hausdorff Distance: {success_df['hausdorff_distance'].mean():.4f}")
        print(f"Average IoGT: {success_df['iogt'].mean():.4f}")
        
        # Median and IQR statistics (new)
        print("\nMedian Statistics (with IQR):")
        
        # Point Cloud Distance
        pc_q1, pc_median, pc_q3, pc_iqr = calculate_iqr(success_df['point_cloud_distance'])
        print(f"Median Point Cloud Distance: {pc_median:.4f} (IQR: {pc_iqr:.4f}, Q1: {pc_q1:.4f}, Q3: {pc_q3:.4f})")
        
        # Hausdorff Distance
        haus_q1, haus_median, haus_q3, haus_iqr = calculate_iqr(success_df['hausdorff_distance'])
        print(f"Median Hausdorff Distance: {haus_median:.4f} (IQR: {haus_iqr:.4f}, Q1: {haus_q1:.4f}, Q3: {haus_q3:.4f})")
        
        # IoGT
        iogt_q1, iogt_median, iogt_q3, iogt_iqr = calculate_iqr(success_df['iogt'])
        print(f"Median IoGT: {iogt_median:.4f} (IQR: {iogt_iqr:.4f}, Q1: {iogt_q1:.4f}, Q3: {iogt_q3:.4f})")
    
    # Save summary data to CSV
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(summary_csv, index=False)
    print(f"Summary statistics saved to {summary_csv}")
    
    return df

def main():
    """
    Main function to run the evaluation.
    """
    # Set the directories and output files with the correct names
    generated_dir = "Generated"
    ground_truth_dir = "Ground_truth"
    output_csv = "final_results_final.csv"
    summary_csv = "final_summary_final.csv"
    
    # Create directories if they don't exist
    os.makedirs(generated_dir, exist_ok=True)
    os.makedirs(ground_truth_dir, exist_ok=True)
    
    print(f"Starting evaluation of STL files...")
    print(f"Generated directory: {generated_dir}")
    print(f"Ground truth directory: {ground_truth_dir}")
    
    df = evaluate_stl_files(generated_dir, ground_truth_dir, output_csv, summary_csv)
    print(f"Evaluation complete. Results saved to {output_csv}")
    print(f"Summary statistics saved to {summary_csv}")
    
    return df

if __name__ == "__main__":
    main()