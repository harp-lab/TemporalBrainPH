import h5py
import numpy as np
import gudhi
import gudhi.wasserstein
import os
import json
from time import time
import gc
from distance_calculation import generate_mds
from cluster_calculation import generate_kmeans_clusters_adhd

def get_barcodes_distance(dgm_1, dgm_2, distance_method='ws'):
    """Computes the Wasserstein or Bottleneck distance between two persistence diagrams."""
    if distance_method == 'ws':
        return gudhi.wasserstein.wasserstein_distance(dgm_1, dgm_2, order=1., internal_p=2.)
    elif distance_method == 'bn':
        return gudhi.bottleneck_distance(dgm_1, dgm_2)
    else:
        raise ValueError(f"Invalid distance method: {distance_method}")


def compute_dissimilarity_matrix_single_subject(subject_data, distance_method='ws'):
    """
    Computes the dissimilarity matrix for a subject.

    Args:
    - subject_data (numpy.ndarray): Shape (#timepoints, ROI, ROI)
    - distance_method (str): 'ws' for Wasserstein, 'bn' for Bottleneck

    Returns:
    - dissimilarity_matrix (numpy.ndarray): Shape (#timepoints, #timepoints)
    """
    num_timepoints, num_rois, _ = subject_data.shape  # Ensure time dimension is correct

    dissimilarity_matrix = np.zeros((num_timepoints, num_timepoints))
    barcodes = {}
    for i in range(num_timepoints):
        if i not in barcodes:
            adjacency_matrix_1 = subject_data[i, :, :]  # Extract (ROI, ROI) at time i
            rips_complex_1 = gudhi.RipsComplex(distance_matrix=adjacency_matrix_1)
            pd_1 = rips_complex_1.create_simplex_tree(max_dimension=1).persistence()[1:]
            barcodes_1 = np.array([pair[1] for pair in pd_1])
            barcodes[i] = barcodes_1
        else:
            barcodes_1 = barcodes[i]

        for j in range(i):
            if j not in barcodes:
                adjacency_matrix_2 = subject_data[j, :, :]  # Extract (ROI, ROI) at time j
                rips_complex_2 = gudhi.RipsComplex(distance_matrix=adjacency_matrix_2)
                pd_2 = rips_complex_2.create_simplex_tree(max_dimension=1).persistence()[1:]
                barcodes_2 = np.array([pair[1] for pair in pd_2])
                barcodes[j] = barcodes_2
            else:
                barcodes_2 = barcodes[j]

            distance = get_barcodes_distance(barcodes_1, barcodes_2, distance_method)
            distance = round(distance, 3)

            dissimilarity_matrix[i, j] = distance
            dissimilarity_matrix[j, i] = distance  # Symmetric matrix
    return dissimilarity_matrix


def normalize_subject_data(subject_data):
    """
    Normalizes fMRI temporal connectivity data.

    Args:
    - subject_data (numpy.ndarray): Shape (Timepoints, ROI, ROI)

    Returns:
    - normalized_data (numpy.ndarray): Shape (#timepoints, ROI, ROI)
    """
    num_timepoints, num_rois_1, num_rois_2 = subject_data.shape
    # print(f"Processing subject with shape: {subject_data.shape}")

    # Replace NaN values with 0
    subject_data = np.nan_to_num(subject_data)

    # Prepare an output array
    normalized_data = np.zeros((num_timepoints, num_rois_1, num_rois_2))

    for t in range(num_timepoints):
        time_data = subject_data[t, :, :]  # Extract matrix for time t

        # Compute correlation matrix
        corr_matrix = np.corrcoef(time_data.T)

        # Debugging: Check for incorrect values
        if np.isnan(corr_matrix).any():
            print(f"Warning: NaN detected in correlation matrix at time {t}")
            corr_matrix = np.nan_to_num(corr_matrix)  # Replace NaNs with 0

        if np.any(corr_matrix < -1) or np.any(corr_matrix > 1):
            print(f"Warning: Clipping correlation values at time {t}")
            corr_matrix = np.clip(corr_matrix, -1, 1)

        # Apply normalization formula correctly
        normalized_data[t] = np.sqrt(np.clip(1 - np.square(corr_matrix), 0, None))
    return normalized_data


def compute_distance_matrix(filepath, distance_directory, distance_method='ws'):
    """
    Reads fMRI DFC data from an HDF5 file, processes all subjects,
    computes normalized connectivity and dissimilarity matrices,
    and stores them as JSON.

    Args:
    - filepath (str): Path to the HDF5 file.
    - distance_directory (str): Directory to save distance matrices.
    - distance_method (str): Distance calculation method ('ws' or 'bn')

    Returns:
    - None (Saves dissimilarity matrices to JSON files)
    """
    if not os.path.exists(distance_directory):
        os.makedirs(distance_directory)
    total_time = 0
    with h5py.File(filepath, 'r') as f:
        dataset_keys = list(f.keys())  # Get dataset keys
        dataset_key = dataset_keys[1]  # Ensure correct dataset selection
        dataset = f[dataset_key]
        print(f"Started processing {dataset_key} containing {dataset.shape[1]} subjects.")
        for subject_idx in range(dataset.shape[1]):  # Iterate over subjects (13)
            start_time = time()
            # print(f"Processing Subject {subject_idx + 1}")
            # Dereference each subject
            subject_ref = dataset[0][subject_idx]  # Extract HDF5 reference
            subject_data = np.array(f[subject_ref])  # Convert reference to NumPy array
            # Transpose to correct shape (Timepoints, ROI, ROI)
            subject_data = np.transpose(subject_data, (2, 0, 1))
            subject_data = normalize_subject_data(subject_data)
            dissimilarity_matrix = compute_dissimilarity_matrix_single_subject(subject_data, distance_method)
            output_json = os.path.join(distance_directory, f"subject_{subject_idx + 1}.json")
            with open(output_json, "w") as f_out:
                json.dump(dissimilarity_matrix.tolist(), f_out)
            end_time = time()
            spent_time = end_time - start_time
            total_time += spent_time
            print(f"Saved dissimilarity matrix of {subject_idx + 1} to {output_json} in {spent_time:.4f} seconds")
            del subject_data
            del dissimilarity_matrix
            gc.collect()
    print(f"Distance matrices for {filepath} are generated in {total_time:.4f} seconds")
    print("="*20)
    print("\n\n")

if __name__ == "__main__":
    total_subjects_adhd2 = 13
    filepath_adhd2 = "/media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_adhd2.mat"
    distance_directory_adhd2 = "adhd/distance_matrix/adhd2/"
    mds_directory_adhd2 = "adhd/mds/adhd2"
    cluster_directory_adhd2 = "adhd/cluster/adhd2"
    # compute_distance_matrix(filepath_adhd2, distance_directory_adhd2, distance_method='ws')

    total_subjects_adhd1 = 208
    filepath_adhd1 = "/media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_adhd1.mat"
    distance_directory_adhd1 = "adhd/distance_matrix/adhd1/"
    mds_directory_adhd1 = "adhd/mds/adhd1"
    cluster_directory_adhd1 = "adhd/cluster/adhd1"
    # compute_distance_matrix(filepath_adhd1, distance_directory_adhd1, distance_method='ws')

    total_subjects_adhd3 = 136
    filepath_adhd3 = "/media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_adhd3.mat"
    distance_directory_adhd3 = "adhd/distance_matrix/adhd3/"
    mds_directory_adhd3 = "adhd/mds/adhd3"
    cluster_directory_adhd3 = "adhd/cluster/adhd3"
    # compute_distance_matrix(filepath_adhd3, distance_directory_adhd3, distance_method='ws')

    total_subjects_adhdcontrols = 573
    filepath_adhdcontrols = "/media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_controls.mat"
    distance_directory_adhdcontrols = "adhd/distance_matrix/adhdcontrols/"
    mds_directory_adhdcontrols = "adhd/mds/adhdcontrols"
    cluster_directory_adhdcontrols = "adhd/cluster/adhdcontrols"
    # compute_distance_matrix(filepath_adhdcontrols, distance_directory_adhdcontrols, distance_method='ws')

    # start_time = time()
    # print(f"Started processing {distance_directory_adhd2} containing {total_subjects_adhd2} subjects.")
    # generate_mds(mds_directory_adhd2, distance_directory_adhd2, total_subjects_adhd2)
    # end_time = time()
    # spent_time = end_time - start_time
    # print(f"Generated MDS on {mds_directory_adhd2} in {spent_time:.4f} seconds\n")

    # start_time = time()
    # print(f"Started processing {distance_directory_adhd1} containing {total_subjects_adhd1} subjects.")
    # generate_mds(mds_directory_adhd1, distance_directory_adhd1, total_subjects_adhd1)
    # end_time = time()
    # spent_time = end_time - start_time
    # print(f"Generated MDS on {mds_directory_adhd1} in {spent_time:.4f} seconds\n")
    #
    # start_time = time()
    # print(f"Started processing {distance_directory_adhd3} containing {total_subjects_adhd3} subjects.")
    # generate_mds(mds_directory_adhd3, distance_directory_adhd3, total_subjects_adhd3)
    # end_time = time()
    # spent_time = end_time - start_time
    # print(f"Generated MDS on {mds_directory_adhd3} in {spent_time:.4f} seconds\n")
    #
    # start_time = time()
    # print(f"Started processing {distance_directory_adhdcontrols} containing {total_subjects_adhdcontrols} subjects.")
    # generate_mds(mds_directory_adhdcontrols, distance_directory_adhdcontrols, total_subjects_adhdcontrols)
    # end_time = time()
    # spent_time = end_time - start_time
    # print(f"Generated MDS on {mds_directory_adhdcontrols} in {spent_time:.4f} seconds\n")


    start_time = time()
    print(f"Started clustering {mds_directory_adhd2} containing {total_subjects_adhd2} subjects.")
    adhd2_clusters = generate_kmeans_clusters_adhd(cluster_directory_adhd2, mds_directory_adhd2,
                                                   total_subjects_adhd2, "ADHD 2")
    end_time = time()
    spent_time = end_time - start_time
    print(f"Clusters: {adhd2_clusters}")
    print(f"Generated clusters on {cluster_directory_adhd2} in {spent_time:.4f} seconds\n")

    start_time = time()
    print(f"Started clustering {mds_directory_adhd1} containing {total_subjects_adhd1} subjects.")
    adhd1_clusters = generate_kmeans_clusters_adhd(cluster_directory_adhd1, mds_directory_adhd1,
                                                   total_subjects_adhd1, "ADHD 1")
    end_time = time()
    spent_time = end_time - start_time
    print(f"Clusters: {adhd1_clusters}")
    print(f"Generated clusters on {cluster_directory_adhd1} in {spent_time:.4f} seconds\n")

    start_time = time()
    print(f"Started clustering {mds_directory_adhd3} containing {total_subjects_adhd3} subjects.")
    adhd3_clusters = generate_kmeans_clusters_adhd(cluster_directory_adhd3, mds_directory_adhd3,
                                                   total_subjects_adhd3, "ADHD 3")
    end_time = time()
    spent_time = end_time - start_time
    print(f"Clusters: {adhd3_clusters}")
    print(f"Generated clusters on {cluster_directory_adhd3} in {spent_time:.4f} seconds\n")

    start_time = time()
    print(f"Started clustering {mds_directory_adhdcontrols} containing {total_subjects_adhdcontrols} subjects.")
    adhdcontrols_clusters = generate_kmeans_clusters_adhd(cluster_directory_adhdcontrols,
                                                          mds_directory_adhdcontrols,
                                                          total_subjects_adhdcontrols, "ADHD Controls")
    end_time = time()
    spent_time = end_time - start_time
    print(f"Clusters: {adhdcontrols_clusters}")
    print(f"Generated clusters on {cluster_directory_adhdcontrols} in {spent_time:.4f} seconds\n")
