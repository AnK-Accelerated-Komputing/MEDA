import math
import os
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d
import pandas as pd
import plotly.graph_objects as go
# import tqdm
# from mpl_toolkits.mplot3d import Axes3D
# from mpl_toolkits.mplot3d.art3d import Poly3DCollection
# from skimage.metrics import mean_squared_error, structural_similarity
from sklearn.neighbors import NearestNeighbors
from stl import mesh


def stl_to_point_cloud(filename):
    try:
        point_cloud = o3d.io.read_triangle_mesh(filename)
        point_cloud = point_cloud.sample_points_poisson_disk(1000)
        return point_cloud
    except Exception as e:
        print(f"Failed to load {filename}: {e}")
        return None


def pc_normalize(pc):
    l = pc.shape[0]
    centroid = np.mean(pc, axis=0)
    pc = pc - centroid
    m = np.max(np.sqrt(np.sum(pc**2, axis=1)))
    pc = pc / m
    return pc

# Credit for https://github.com/OmarJItani/Iterative-Closest-Point-Algorithm


def best_fit_transform(A, B):
    """
    Calculates the best-fit transform that maps points A onto points B.
    Input:
        A: Nxm numpy array of source points
        B: Nxm numpy array of destination points
    Output:
        T: (m+1)x(m+1) homogeneous transformation matrix
    """

    # Check if A and B have same dimensions
    assert A.shape == B.shape

    # Get number of dimensions
    m = A.shape[1]

    # Translate points to their centroids
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    AA = A - centroid_A
    BB = B - centroid_B

    # Rotation matrix
    H = np.dot(AA.T, BB)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)

    # Special reflection case
    if np.linalg.det(R) < 0:
        Vt[m-1, :] *= -1
        R = np.dot(Vt.T, U.T)

    # Translation
    t = centroid_B.reshape(-1, 1) - np.dot(R, centroid_A.reshape(-1, 1))

    # Homogeneous transformation
    T = np.eye(m+1)
    T[:m, :m] = R
    T[:m, -1] = t.ravel()

    return T


def nearest_neighbor(src, dst):
    '''
    Find the nearest (Euclidean) neighbor in dst for each point in src
    Input:
        src: Nxm array of points
        dst: Nxm array of points
    Output:
        distances: Euclidean distances of the nearest neighbor
        indices: dst indices of the nearest neighbor
    '''

    assert src.shape == dst.shape

    neigh = NearestNeighbors(n_neighbors=1)  # n_neighbors=1
    neigh.fit(dst)
    distances, indices = neigh.kneighbors(src, return_distance=True)
    return distances.ravel(), indices.ravel()


def iterative_closest_point(A, B, max_iterations=20, tolerance=0.001):  # tolerance=0.001
    '''
    The Iterative Closest Point method: finds best-fit transform that maps points A on to points B
    Input:
        A: Nxm numpy array of source points
        B: Nxm numpy array of destination points
        max_iterations: exit algorithm after max_iterations
        tolerance: convergence criteria
    Output:
        T: final homogeneous transformation that maps A on to B
        finalA: Aligned points A; Source points A after getting mapped to destination points B
        final_error: Sum of euclidean distances (errors) of the nearest neighbors
        i: number of iterations to converge
    '''

    assert A.shape == B.shape

    # get number of dimensions
    m = A.shape[1]

    # make points homogeneous, copy them to maintain the originals
    src = np.ones((m+1, A.shape[0]))
    dst = np.ones((m+1, B.shape[0]))
    src[:m, :] = np.copy(A.T)
    dst[:m, :] = np.copy(B.T)

    prev_error = 0

    for i in range(max_iterations):  # tqdm.tqdm(range(max_iterations)):
        # find the nearest neighbors between the current source and destination points
        distances, indices = nearest_neighbor(src[:m, :].T, dst[:m, :].T)

        # compute the transformation between the current source and nearest destination points
        T = best_fit_transform(src[:m, :].T, dst[:m, indices].T)

        # update the current source
        src = np.dot(T, src)

        # check error (stop if error is less than specified tolerance)
        mean_error = np.mean(distances)
        if np.abs(prev_error - mean_error) < tolerance:
            break
        prev_error = mean_error

    # calculate final transformation, error, and mapped source points
    T = best_fit_transform(A, src[:m, :].T)
    final_error = prev_error

    # get final A
    rot = T[0:-1, 0:-1]
    t = T[:-1, -1]
    finalA = np.dot(rot, A.T).T + t

    return T, finalA, final_error, i


def intersection_over_GT2(GT, test, threshold=-0.6):  # -0.6
    # Convert to binary images based on a threshold
    # print(GT)
    GT_binary = (GT > threshold).astype(np.uint8)
    test_binary = (test > threshold).astype(np.uint8)
    # print(f"GT_binary:\n{GT_binary}")
    # print(f"test_binary:\n{test_binary}")
    # Compute the intersection of GT and test images
    intersection = np.logical_and(GT_binary, test_binary).astype(np.uint8)

    # Calculate the ratio of the intersection over GT's foreground
    if np.count_nonzero(GT_binary) == 0:
        return 0  # Handle division by zero if GT has no foreground pixels
    return np.count_nonzero(intersection) / np.count_nonzero(GT_binary)


def intersection_over_GT(GT, test):
    # Ensure both images are single-channel by converting them to grayscale if they are not
    if len(GT.shape) == 3:
        GT = cv2.cvtColor(GT, cv2.COLOR_BGR2GRAY)
    if len(test.shape) == 3:
        test = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)

    # intersection = cv2.bitwise_and(GT, test)
    intersection = np.logical_and(GT, test).astype(np.uint8)

    return cv2.countNonZero(intersection) / cv2.countNonZero(GT)


def point_cloud_distance(pc1, pc2):
    """
    Calculates the average minimum distance from each point in pc1 to the closest point in pc2.

    Parameters:
    - pc1: numpy array of shape (N, 3) representing the first point cloud.
    - pc2: numpy array of shape (M, 3) representing the second point cloud.

    Returns:
    - avg_distance: The average of the minimum distances from points in pc1 to points in pc2.
    """
    # Expand dimensions for broadcasting to calculate distances between each pair of points
    pc1_expanded = np.expand_dims(pc1, axis=1)  # Shape (N, 1, 3)
    pc2_expanded = np.expand_dims(pc2, axis=0)  # Shape (1, M, 3)

    # Calculate squared distances between each pair of points
    distances = np.sqrt(np.sum((pc1_expanded - pc2_expanded) ** 2, axis=2))

    # Find the minimum distance for each point in pc1 to any point in pc2
    min_distances = np.min(distances, axis=1)

    # Calculate the average of these minimum distances
    avg_distance = np.mean(min_distances)

    return avg_distance


def voxel_grid2(point_cloud, grid_size):
    # Normalizing coordinates to the grid size
    min_vals = np.min(point_cloud, axis=0)
    max_vals = np.max(point_cloud, axis=0)
    # Adjust max_vals slightly to ensure points on the upper boundary are included
    max_vals += 1e-9
    scales = (grid_size - 1) / (max_vals - min_vals)
    voxels = np.floor((point_cloud - min_vals) * scales).astype(int)
    # Ensure all voxel indices are within the grid size
    voxels = np.clip(voxels, 0, grid_size - 1)
    return set(map(tuple, voxels))


def hausdorff_distance(pc1, pc2):
    """
    Calculates the Hausdorff distance between two point clouds.

    Parameters:
    - pc1: numpy array of shape (N, 3), representing the first point cloud.
    - pc2: numpy array of shape (M, 3), representing the second point cloud.

    Returns:
    - hausdorff_dist: The Hausdorff distance between the two point clouds.
    """
    # Expand dimensions for broadcasting to calculate distances between each pair of points
    pc1_expanded = np.expand_dims(pc1, axis=1)  # Shape (N, 1, 3)
    pc2_expanded = np.expand_dims(pc2, axis=0)  # Shape (1, M, 3)

    # Calculate squared distances between each pair of points
    distances = np.sqrt(np.sum((pc1_expanded - pc2_expanded) ** 2, axis=2))

    # Find the minimum distance for each point in pc1 to any point in pc2
    min_distances_1_to_2 = np.min(distances, axis=1)

    # Find the minimum distance for each point in pc2 to any point in pc1
    min_distances_2_to_1 = np.min(distances, axis=0)

    # The Hausdorff distance is the maximum of these minimum distances
    hausdorff_dist = max(np.max(min_distances_1_to_2),
                         np.max(min_distances_2_to_1))

    return hausdorff_dist


def iou(y_true, y_pred):

    intersection = np.logical_and(y_true, y_pred)
    union = np.logical_or(y_true, y_pred)
    iou_score = np.sum(intersection) / np.sum(union)
    print(iou_score)
    return iou_score


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
        gt_path = os.path.join(
            ground_truth_dir, f"{base_name}_ground_truth.stl")

        processed_count += 1
        print(f"Processing {base_name} ({processed_count}/{total_files})")

        # Load point clouds
        gen_pcd = stl_to_point_cloud(gen_path)
        gt_pcd = stl_to_point_cloud(gt_path)

        # Default values for failed compilations
        pc_dist = math.sqrt(3)
        haus_dist = math.sqrt(3)
        iogt = 0.0
        compilation_success = False

        if gen_pcd is not None and gt_pcd is not None:
            compilation_success = True
            # Apply ICP for alignment
            destination_points = np.asarray(gen_pcd.points)
            source_points = np.asarray(gt_pcd.points)

            destination_points = pc_normalize(destination_points)
            source_points = pc_normalize(source_points)
            T, finalA, final_error, i = iterative_closest_point(
                source_points, destination_points, 2000)
            iogt = intersection_over_GT2(destination_points, finalA)
            pc_dist = point_cloud_distance(destination_points, finalA)
            haus_dist = hausdorff_distance(destination_points, finalA)

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
    print(
        f"Failed to compile: {len(results) - df['compilation_success'].sum()}")

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
        print(
            f"Average Point Cloud Distance: {success_df['point_cloud_distance'].mean():.4f}")
        print(
            f"Average Hausdorff Distance: {success_df['hausdorff_distance'].mean():.4f}")
        print(f"Average IoGT: {success_df['iogt'].mean():.4f}")

        # Median and IQR statistics (new)
        print("\nMedian Statistics (with IQR):")

        # Point Cloud Distance
        pc_q1, pc_median, pc_q3, pc_iqr = calculate_iqr(
            success_df['point_cloud_distance'])
        print(
            f"Median Point Cloud Distance: {pc_median:.4f} (IQR: {pc_iqr:.4f}, Q1: {pc_q1:.4f}, Q3: {pc_q3:.4f})")

        # Hausdorff Distance
        haus_q1, haus_median, haus_q3, haus_iqr = calculate_iqr(
            success_df['hausdorff_distance'])
        print(
            f"Median Hausdorff Distance: {haus_median:.4f} (IQR: {haus_iqr:.4f}, Q1: {haus_q1:.4f}, Q3: {haus_q3:.4f})")

        # IoGT
        iogt_q1, iogt_median, iogt_q3, iogt_iqr = calculate_iqr(
            success_df['iogt'])
        print(
            f"Median IoGT: {iogt_median:.4f} (IQR: {iogt_iqr:.4f}, Q1: {iogt_q1:.4f}, Q3: {iogt_q3:.4f})")

    # Save summary data to CSV
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(summary_csv, index=False)
    print(f"Summary statistics saved to {summary_csv}")


def main():
    """
    Main function to run the evaluation.
    """
    # Set the directories and output files with the correct names
    # generated_dir = "/home/niel77/CADsimtest/ablation_study/Executor"
    # ground_truth_dir = "/home/niel77/CADsimtest/Ground_truth"
    # output_csv = "cadcodeverify_summary_executor.csv"
    # summary_csv = "cadcodeverify_summary_executor.csv"

    # generated_dir = "/home/niel77/CADsimtest/ablation_study/Reviewer_first_refinement"
    # ground_truth_dir = "/home/niel77/CADsimtest/Ground_truth"
    # output_csv = "cadcodeverify_results_reviewer_first.csv"
    # summary_csv = "cadcodeverify_summary_reviewer_first.csv"

    # generated_dir = "/home/niel77/CADsimtest/ablation_study/Reviewer_second_refinement"
    # ground_truth_dir = "/home/niel77/CADsimtest/Ground_truth"
    # output_csv = "cadcodeverify_results_reviewer_second.csv"
    # summary_csv = "cadcodeverify_summary_reviewer_second.csv"

    generated_dir = "/home/niel77/CADsimtest/ablation_study/Final"
    ground_truth_dir = "/home/niel77/CADsimtest/Ground_truth"
    output_csv = "cadcodeverify_results_final.csv"
    summary_csv = "cadcodeverify_summary_final.csv"

    # Create directories if they don't exist
    os.makedirs(generated_dir, exist_ok=True)
    os.makedirs(ground_truth_dir, exist_ok=True)

    print(f"Starting evaluation of STL files...")
    print(f"Generated directory: {generated_dir}")
    print(f"Ground truth directory: {ground_truth_dir}")

    evaluate_stl_files(generated_dir, ground_truth_dir,
                       output_csv, summary_csv)
    print(f"Evaluation complete. Results saved to {output_csv}")
    print(f"Summary statistics saved to {summary_csv}")


if __name__ == "__main__":
    main()
