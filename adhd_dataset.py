import h5py
import numpy as np
import gudhi
import gudhi.wasserstein
import os
import json
from time import time
import gc
import pandas as pd
import json
import copy
import csv
from scipy import stats
import matplotlib.pyplot as plt
from distance_calculation import generate_mds
from cluster_calculation import generate_kmeans_clusters_adhd

def shoelace_formula(vertices):
    """
    Calculate the area of a polygon using the shoelace formula.

    Args:
        vertices: A list of tuples, where each tuple represents the (x, y)
                  coordinates of a vertex.

    Returns:
        The area of the polygon.
    """
    n = len(vertices)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n  # Next vertex, wraps around to the first vertex
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    area = abs(area) / 2.0
    return area

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


def compute_dissimilarity_matrix_single_subject_nontda(subject_data):
    num_timepoints, num_rois, _ = subject_data.shape  # Ensure time dimension is correct

    dissimilarity_matrix = np.zeros((num_timepoints, num_timepoints))
    matrices = {}
    for i in range(num_timepoints):
        if i not in matrices:
            adjacency_matrix_1 = subject_data[i, :, :]  # Extract (ROI, ROI) at time i
            matrices[i] = adjacency_matrix_1
        else:
            adjacency_matrix_1 = matrices[i]

        for j in range(i):
            if j not in matrices:
                adjacency_matrix_2 = subject_data[j, :, :]  # Extract (ROI, ROI) at time j
                matrices[j] = adjacency_matrix_2
            else:
                adjacency_matrix_2 = matrices[j]
            distance = np.linalg.norm(adjacency_matrix_1 - adjacency_matrix_2)
            distance = round(distance, 3)
            dissimilarity_matrix[i - 1][j - 1] = distance
            dissimilarity_matrix[j - 1][i - 1] = distance
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


def compute_distance_matrix(filepath, distance_directory, distance_method='ws', pipeline="tda"):
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
            if pipeline == "tda":
                dissimilarity_matrix = compute_dissimilarity_matrix_single_subject(subject_data, distance_method)
            else:
                dissimilarity_matrix = compute_dissimilarity_matrix_single_subject_nontda(subject_data)
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
    print("=" * 20)
    print("\n\n")


def cluster_analysis(pipeline, output_file):
    # Define paths to cluster JSON files
    cluster_files = {
        "adhd1": f"adhd/{pipeline}/cluster/adhd1/clusters.json",
        "adhd2": f"adhd/{pipeline}/cluster/adhd2/clusters.json",
        "adhd3": f"adhd/{pipeline}/cluster/adhd3/clusters.json",
        "adhdcontrols": f"adhd/{pipeline}/cluster/adhdcontrols/clusters.json",
    }

    # Define paths to CSV files
    csv_files = {
        "adhd1": "adhd/site_map/ADHD_1_ADHD1.csv",
        "adhd2": "adhd/site_map/ADHD_2_ADHD2.csv",
        "adhd3": "adhd/site_map/ADHD_3_ADHD3.csv",
        "adhdcontrols": "adhd/site_map/ADHD_0_Controls.csv",
    }

    # Site Data (mapping SITE_ID to TR values)
    site_data = {
        1: {"SITE_NAME": "Peking", "TR": 2},
        3: {"SITE_NAME": "KKI", "TR": 2.5},
        4: {"SITE_NAME": "NeuroIMAGE", "TR": 2},
        5: {"SITE_NAME": "NYU", "TR": 2},
        6: {"SITE_NAME": "OHSU", "TR": 2.5},
        8: {"SITE_NAME": "WashU", "TR": 2.5},
    }

    # Define base directory for MDS data
    mds_base_path = f"adhd/{pipeline}/mds"

    # Final dictionary to store subject to TR mapping
    subject_tr_mapping = {}

    # Process each group
    for group, cluster_path in cluster_files.items():
        # Load cluster JSON file
        with open(cluster_path, 'r') as f:
            cluster_data = json.load(f)

        # Read the corresponding CSV file
        csv_path = csv_files[group]
        df = pd.read_csv(csv_path)

        # Ensure subject IDs are sequential in the CSV file
        df["Subject_Index"] = range(1, len(df) + 1)  # Sequential subject IDs

        # Extract relevant information
        subject_site_mapping = dict(zip(df["Subject_Index"], df["Site"]))
        # print(f"{group}: {subject_site_mapping}")

        # Assign TR values to subjects based on Site ID
        count_subject = 0
        for subject_id, cluster in cluster_data.items():
            subject_id = int(subject_id)  # Convert JSON keys to int for mapping
            if subject_id in subject_site_mapping:
                site_id = subject_site_mapping[subject_id]
                if site_id not in site_data.keys():
                    continue
                tr_value = site_data.get(site_id, {}).get("TR", None)  # Get TR value
                # Construct the MDS file path
                mds_file_path = os.path.join(mds_base_path, group, f"subject_{subject_id}.json")
                # Load MDS data if the file exists
                if os.path.exists(mds_file_path):
                    with open(mds_file_path, "r") as mds_file:
                        mds_data = json.load(mds_file)  # Assuming it's a list of [x, y] coordinates
                else:
                    mds_data = None  # No MDS data found for this subject

                subject_tr_mapping[f"{group}-{subject_id}"] = {"TR": tr_value, "Cluster": cluster,
                                                               "Subject_ID": subject_id,
                                                               "Group": group, "MDS": mds_data}
                count_subject += 1
        print(f"{group} has {count_subject} subjects with TR 2 or 2.5")

    # Output final mapping
    with open(output_file, "w") as f_out:
        json.dump(subject_tr_mapping, f_out)
    print(f"Generated subject, cluster, TR mapping: {output_file}")


def plot_group_histogram(pipeline, groups, group_names, title, group_type):
    plt.figure(figsize=(10, 6))
    all_values = np.concatenate([groups[name] for name in group_names])
    bins = np.arange(1, 17, 1)


    # Determine the width of each bin based on the number of groups
    total_width = 0.8  # total width taken by bars in one bin space
    width = total_width / len(group_names)

    for idx, group_name in enumerate(group_names):
        values = groups[group_name]
        counts, bin_edges = np.histogram(values, bins=bins)
        percentages = counts / counts.sum() * 100
        # bin_centers = bin_edges[:-1] + 0.5

        # Offset for side-by-side arrangement
        offset = (idx - (len(group_names) - 1) / 2) * width
        plt.bar(bin_edges[:-1] + offset, percentages, width=width, alpha=0.7, label=group_name, edgecolor='black')

    plt.xlabel("# of Clusters")
    plt.ylabel("Percentage (%)")
    plt.title(title)
    x_ticks = np.arange(1, 17, 1)
    # print(x_ticks)
    plt.xticks(x_ticks, [f"{int(x):d}" for x in x_ticks])
    plt.legend()
    plt.grid(axis="y", alpha=0.75)
    plt.tight_layout()
    image_name = f"adhd/{pipeline}/{pipeline}_{group_type}.png"
    image_name = image_name.replace(" ", "")
    plt.savefig(image_name, dpi=250)
    plt.close()
    print(f"Generated {image_name}")

def perform_t_test(pipeline, json_file_path):
    output_file_path = f"adhd/{pipeline}/{pipeline}_cohorts.json"
    output_csv_file_path = f"adhd/{pipeline}/{pipeline}_cohorts.csv"
    with open(json_file_path, 'r') as f:
        subject_data = json.load(f)

    # Separate subjects into cohorts based on TR values
    cohort_1_subjects = {key: data for key, data in subject_data.items() if data["TR"] == 2}
    cohort_2_subjects = {key: data for key, data in subject_data.items() if data["TR"] == 2.5}

    # Separate subjects into control and ADHD based on "Group" value
    cohort_1_control = {key: data for key, data in cohort_1_subjects.items() if data["Group"] == "adhdcontrols"}
    cohort_1_adhd = {key: data for key, data in cohort_1_subjects.items() if data["Group"] != "adhdcontrols"}

    cohort_2_control = {key: data for key, data in cohort_2_subjects.items() if data["Group"] == "adhdcontrols"}
    cohort_2_adhd = {key: data for key, data in cohort_2_subjects.items() if data["Group"] != "adhdcontrols"}

    # Convert to numpy arrays
    cohort_1_control_clusters = np.array([data["Cluster"] for key, data in cohort_1_control.items()])
    cohort_1_adhd_clusters = np.array([data["Cluster"] for key, data in cohort_1_adhd.items()])
    cohort_2_control_clusters = np.array([data["Cluster"] for key, data in cohort_2_control.items()])
    cohort_2_adhd_clusters = np.array([data["Cluster"] for key, data in cohort_2_adhd.items()])

    # Compute mean and standard error
    updated_data = {
        "cohort1-control": {
            "mean": round(float(np.mean(cohort_1_control_clusters)), 4),
            "std_error": round(float(stats.sem(cohort_1_control_clusters)), 4),
            "data": cohort_1_control_clusters.tolist()
        },
        "cohort1-adhd": {
            "mean": round(float(np.mean(cohort_1_adhd_clusters)), 4),
            "std_error": round(float(stats.sem(cohort_1_adhd_clusters)), 4),
            "data": cohort_1_adhd_clusters.tolist()
        },
        "cohort2-control": {
            "mean": round(float(np.mean(cohort_2_control_clusters)), 4),
            "std_error": round(float(stats.sem(cohort_2_control_clusters)), 4),
            "data": cohort_2_control_clusters.tolist()
        },
        "cohort2-adhd": {
            "mean": round(float(np.mean(cohort_2_adhd_clusters)), 4),
            "std_error": round(float(stats.sem(cohort_2_adhd_clusters)), 4),
            "data": cohort_2_adhd_clusters.tolist()
        }
    }
    updated_data_no_data_dynamic = copy.deepcopy(updated_data)

    # # Remove "data" key from each sub-dictionary
    # for key in updated_data_no_data_dynamic:
    #     updated_data_no_data_dynamic[key].pop("data", None)
    #
    # print(updated_data_no_data_dynamic)
    #
    # # Save as JSON file
    # with open(output_file_path, "w") as json_file:
    #     json.dump(updated_data, json_file)
    # print(f"Generated: {output_file_path}")
    #
    # # Write to CSV file
    #
    # with open(output_csv_file_path, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #
    #     # Write header
    #     writer.writerow(updated_data.keys())
    #
    #     # Get max length of data lists
    #     max_length = max(len(v["data"]) for v in updated_data.values())
    #
    #     # Write data row-wise
    #     for i in range(max_length):
    #         row = [
    #             updated_data[key]["data"][i] if i < len(updated_data[key]["data"]) else ""
    #             for key in updated_data
    #         ]
    #         writer.writerow(row)
    # print(f"Generated: {output_csv_file_path}")


    # Plot histograms
    groups = {
        "Control (TR=2)": cohort_1_control_clusters,
        "ADHD (TR=2)": cohort_1_adhd_clusters,
        "Control (TR=2.5)": cohort_2_control_clusters,
        "ADHD (TR=2.5)": cohort_2_adhd_clusters,
    }

    # print(groups)

    # Plotting figures as requested
    plot_group_histogram(pipeline, groups, ['Control (TR=2)', 'Control (TR=2)'],
                         f"Histogram of Control groups ({pipeline.upper()})", "Control")
    plot_group_histogram(pipeline, groups, ['ADHD (TR=2)', 'ADHD (TR=2.5)'],
                         f"Histogram of ADHD groups ({pipeline.upper()})", "ADHD")
    # # Perform t-tests
    # t_values_c1, p_values_c1 = stats.ttest_ind(cohort_1_control_clusters, cohort_1_adhd_clusters, equal_var=False)
    # t_values_c2, p_values_c2 = stats.ttest_ind(cohort_2_control_clusters, cohort_2_adhd_clusters, equal_var=False)
    #
    # # Calculate differences between control and ADHD for each cohort
    # t_values_X1, p_values_X1 = stats.ttest_ind(cohort_1_control_clusters, cohort_2_control_clusters, equal_var=False)
    # t_values_X2, p_values_X2 = stats.ttest_ind(cohort_1_adhd_clusters, cohort_2_adhd_clusters, equal_var=False)
    #
    # # Print results
    # print(f"Pipeline: {pipeline}")
    # print(f"Cohort 1 => control: {cohort_1_control_clusters.shape[0]} subjects, "
    #       f"ADHD: {cohort_1_adhd_clusters.shape[0]} subjects")
    # print(f"Cohort 2 => control: {cohort_2_control_clusters.shape[0]} subjects, "
    #       f"ADHD: {cohort_2_adhd_clusters.shape[0]} subjects")
    #
    # print("Cohort 1 (TR=2s):")
    # print(f"t-statistic (between control and adhd): {t_values_c1:.3f}")
    # print(f"p-value (between control and adhd): {p_values_c1:.3f}")
    #
    # print("Cohort 2 (TR=2.5s):")
    # print(f"t-statistic (between control and adhd): {t_values_c2:.3f}")
    # print(f"p-value (between control and adhd): {p_values_c2:.3f}")
    #
    # print(f"t-statistic (between control of cohorts): {t_values_X1:.3f}")
    # print(f"p-value (between control of cohorts): {p_values_X1:.3f}")
    #
    # print(f"t-statistic (between adhd of cohorts): {t_values_X2:.3f}")
    # print(f"p-value (between adhd of cohorts): {p_values_X2:.3f}")

    # print("Cohort 1 results:", "t-value:", t_values_c1)
    # print("Cohort 2 results:", "t-value:", t_values_c2)
    # print("X1 vs X2 comparison:", "t-value:", t_values_X1_X2, "p-value:", p_values_X1_X2)


def distance_generation(datasets, groups, pipeline, distance_directory, distance_method):
    for group in groups:
        compute_distance_matrix(datasets[group]["filepath"], distance_directory[group], distance_method, pipeline)


def mds_generation(datasets, groups, distance_directory, mds_directory):
    for group in groups:
        start_time = time()
        print(
            f"Started processing {distance_directory[group]} containing {datasets[group]['total_subjects']} subjects.")
        generate_mds(mds_directory[group], distance_directory[group], datasets[group]['total_subjects'])
        end_time = time()
        spent_time = end_time - start_time
        print(f"Generated MDS on {mds_directory[group]} in {spent_time:.4f} seconds\n")


def cluster_generation(datasets, groups, mds_directory, cluster_directory):
    for group in groups:
        start_time = time()
        print(f"Started clustering {mds_directory[group]} containing {datasets[group]['total_subjects']} subjects.")
        clusters = generate_kmeans_clusters_adhd(cluster_directory[group], mds_directory[group],
                                                 datasets[group]['total_subjects'], group)
        end_time = time()
        spent_time = end_time - start_time
        print(f"Clusters: {clusters}")
        print(f"Generated clusters on {cluster_directory[group]} in {spent_time:.4f} seconds\n")


def get_mds_data(pipeline, json_file_path):
    output_file_path = f"adhd/{pipeline}/{pipeline}_cohorts.json"
    with open(json_file_path, 'r') as f:
        subject_data = json.load(f)

    # Separate subjects into cohorts based on TR values
    cohort_1_subjects = {key: data for key, data in subject_data.items() if data["TR"] == 2}
    cohort_2_subjects = {key: data for key, data in subject_data.items() if data["TR"] == 2.5}

    # Separate subjects into control and ADHD based on "Group" value
    cohort_1_control = {key: data for key, data in cohort_1_subjects.items() if data["Group"] == "adhdcontrols"}
    cohort_1_adhd = {key: data for key, data in cohort_1_subjects.items() if data["Group"] != "adhdcontrols"}

    cohort_2_control = {key: data for key, data in cohort_2_subjects.items() if data["Group"] == "adhdcontrols"}
    cohort_2_adhd = {key: data for key, data in cohort_2_subjects.items() if data["Group"] != "adhdcontrols"}


    # Convert to numpy arrays
    cohort_1_control_mdss = [np.array(json.loads(data["MDS"])) for key, data in cohort_1_control.items()]
    cohort_1_adhd_mdss = [np.array(json.loads(data["MDS"])) for key, data in cohort_1_adhd.items()]
    cohort_2_control_mdss = [np.array(json.loads(data["MDS"])) for key, data in cohort_2_control.items()]
    cohort_2_adhd_mdss = [np.array(json.loads(data["MDS"])) for key, data in cohort_2_adhd.items()]

    cohort_1_control_areas = [shoelace_formula(mds) for mds in cohort_1_control_mdss]
    cohort_1_adhd_areas = [shoelace_formula(mds) for mds in cohort_1_adhd_mdss]
    cohort_2_control_areas = [shoelace_formula(mds) for mds in cohort_2_control_mdss]
    cohort_2_adhd_areas = [shoelace_formula(mds) for mds in cohort_2_adhd_mdss]

    # Perform t-tests
    t_values_c1, p_values_c1 = stats.ttest_ind(cohort_1_control_areas, cohort_1_adhd_areas, equal_var=False)
    t_values_c2, p_values_c2 = stats.ttest_ind(cohort_2_control_areas, cohort_2_adhd_areas, equal_var=False)

    # Calculate differences between control and ADHD for each cohort
    t_values_X1, p_values_X1 = stats.ttest_ind(cohort_1_control_areas, cohort_2_control_areas, equal_var=False)
    t_values_X2, p_values_X2 = stats.ttest_ind(cohort_1_adhd_areas, cohort_2_adhd_areas, equal_var=False)

    print(f"Pipeline: {pipeline}")
    print(f"Cohort 1 (Control - ADHD): ({t_values_c1:.4f}, {p_values_c1:.4f})")
    print(f"Cohort 2 (Control - ADHD): ({t_values_c2:.4f}, {p_values_c2:.4f})")

    print(f"Control (Cohort 1 - Cohort 2): ({t_values_X1:.4f}, {p_values_X1:.4f})")
    print(f"ADHD (Cohort 1 - Cohort 2): ({t_values_X2:.4f}, {p_values_X2:.4f})")

    # print(len(cohort_1_control_mdss), len(cohort_1_adhd_mdss))
    # print(len(cohort_2_control_mdss), len(cohort_2_adhd_mdss))

    # cohort_1_control_mdss_avg = [np.mean(ar, axis=0) for ar in cohort_1_control_mdss]
    # cohort_1_adhd_mdss_avg = [np.mean(ar, axis=0) for ar in cohort_1_adhd_mdss]
    # cohort_2_control_mdss_avg = [np.mean(ar, axis=0) for ar in cohort_2_control_mdss]
    # cohort_2_adhd_mdss_avg = [np.mean(ar, axis=0) for ar in cohort_2_adhd_mdss]

    # print(len(cohort_1_control_mdss_avg), cohort_1_control_mdss_avg[0])





def run_pipeline(datasets, pipeline, distance_method):
    groups = ["adhd2", "adhd1", "adhd3", "adhdcontrols"]
    cluster_tr = f"adhd/{pipeline}/cluster_tr.json"
    distance_directory = {}
    mds_directory = {}
    cluster_directory = {}
    for group in groups:
        distance_directory[group] = f"adhd/{pipeline}/distance_matrix/{group}/"
        mds_directory[group] = f"adhd/{pipeline}/mds/{group}/"
        cluster_directory[group] = f"adhd/{pipeline}/cluster/{group}/"

    # distance_generation(datasets, groups, pipeline, distance_directory, distance_method)
    # mds_generation(datasets, groups, distance_directory, mds_directory)
    # cluster_generation(datasets, groups, mds_directory, cluster_directory)

    # Generate cluster info and tr json
    # cluster_analysis(pipeline, cluster_tr)

    # perform_t_test(pipeline, cluster_tr)
    get_mds_data(pipeline, cluster_tr)


if __name__ == "__main__":
    datasets = {
        "adhd2": {
            "total_subjects": 13,
            "filepath": "/media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_adhd2.mat"
        },
        "adhd1": {
            "total_subjects": 208,
            "filepath": "/media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_adhd1.mat"
        },
        "adhd3": {
            "total_subjects": 136,
            "filepath": "/media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_adhd3.mat"
        },
        "adhdcontrols": {
            "total_subjects": 573,
            "filepath": "/media/shovon/Multimedia/dfc/adhd/data/DFC_adhd_filt_controls.mat"
        }
    }

    run_pipeline(datasets, "tda", "ws")
    run_pipeline(datasets, "traditional", "ws")
