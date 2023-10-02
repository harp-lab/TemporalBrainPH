import json
import math
import os
import csv
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from utils import timer, get_dataset


def get_labels_highest_score(dataset):
    max_score = -math.inf
    labels = None
    number_of_clusters = 9
    for i in range(2, 16):
        cluster = KMeans(n_clusters=i, random_state=10)
        cluster_labels = cluster.fit_predict(dataset)
        score = silhouette_score(dataset, cluster_labels)
        if score > max_score:
            number_of_clusters = i
            max_score = score
            labels = cluster_labels
    return number_of_clusters, labels


def get_cluster_info(dfc_normalize_path,
                     dfc_timeslots,
                     subject_number, dfc_number):
    dataset = []
    file_prefix = f"normalize_dfc_{dfc_number}_subject_"
    for i in range(1, dfc_timeslots + 1):
        filename = f'{dfc_normalize_path}/{file_prefix}{subject_number}_time_{i}.txt'
        dataset.append(get_dataset(filename=filename,
                                   fmri=True))
    three_dim_data = np.array(dataset)
    two_dim_data = three_dim_data.reshape(-1,
                                          three_dim_data.shape[1] *
                                          three_dim_data.shape[2])
    n_clusters, labels = get_labels_highest_score(two_dim_data)
    return n_clusters


def generate_kmeans_clusters(start_subject, end_subject,
                             dfc_2500_normalize_path,
                             dfc_2500_timeslots,
                             dfc_1400_normalize_path,
                             dfc_1400_timeslots,
                             dfc_645_normalize_path,
                             dfc_645_timeslots,
                             output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    cluster_info = {}
    for subject_number in range(start_subject, end_subject + 1):
        print(f"Generating cluster for Subject: {subject_number}")
        n_clusters_2500 = get_cluster_info(
            dfc_2500_normalize_path, dfc_2500_timeslots,
            subject_number, 2500)
        n_clusters_1400 = get_cluster_info(
            dfc_1400_normalize_path, dfc_1400_timeslots,
            subject_number, 1400)
        n_clusters_645 = get_cluster_info(
            dfc_645_normalize_path, dfc_645_timeslots,
            subject_number, 645)
        cluster_info[subject_number] = [
            n_clusters_2500, n_clusters_1400, n_clusters_645
        ]
        print(f"Generated cluster for Subject: {subject_number}\n")
    with open(f"{output_directory}/clusters.json", "w") as json_file:
        json.dump(cluster_info, json_file)
    print(
        f"Done. Generated clusters: subject {start_subject} - {end_subject}\n")
    return cluster_info


def show_clustering_results(cluster_summary,
                            clustering_algorithm="kmeans",
                            comments=None, file_path=None, csv_file_path=None):
    if file_path:
        cluster_summary = json.load(open(file_path))
    total_matches = 0
    total_subjects = 0
    matches = []
    distances = {}
    for subject in cluster_summary:
        dfc_2500, dfc_1400, dfc_645 = cluster_summary[subject]
        a, b, c = sorted([dfc_2500, dfc_1400, dfc_645])
        distance = abs(b - a) + abs(c - b)
        distances[distance] = distances.get(distance, 0) + 1
        if dfc_2500 == dfc_1400 and dfc_1400 == dfc_645:
            total_matches += 1
            matches.append(subject)
        total_subjects += 1
    match_percentage = (total_matches / total_subjects) * 100
    print(f"Clustering Method: {clustering_algorithm}")
    if comments:
        print(comments)
    print(f"Total subjects: {total_subjects}")
    distances = sorted(distances.items(), key=lambda x: x[0])
    print("Match percentages:")
    for pair in distances:
        percentage = (pair[1] / total_subjects) * 100
        print(
            f"Distance: {pair[0]:3d}, number of subjects: {pair[1]:3d}, percentage: {percentage:.2f}%")
    if csv_file_path:
        with open(csv_file_path, 'w', newline='') as csvfile:
            column_names = ['Subject', 'DFC 2500', 'DFC 1400', 'DFC 645']
            csv_data = []
            for subject in cluster_summary:
                subject_data = {}
                subject_data[column_names[0]] = subject
                for i in range(1, len(column_names)):
                    subject_data[column_names[i]] = cluster_summary[subject][
                        i - 1]
                csv_data.append(subject_data)
            writer = csv.DictWriter(csvfile, fieldnames=column_names)
            writer.writeheader()
            writer.writerows(csv_data)
    return total_subjects, total_matches, match_percentage


@timer
def main():
    output_dir = "../clusters_kmeans_without_mds"
    start_subject_number = 1
    end_subject_number = 316
    dfc_2500_normalize = "../dfc_2500_normal_original"
    dfc_2500_timeslots = 86
    dfc_1400_normalize = "../dfc_1400_normal_original"
    dfc_1400_timeslots = 336
    dfc_645_normalize = "../dfc_645_normal_original"
    dfc_645_timeslots = 754
    cluster_summary = generate_kmeans_clusters(start_subject_number,
                                               end_subject_number,
                                               dfc_2500_normalize,
                                               dfc_2500_timeslots,
                                               dfc_1400_normalize,
                                               dfc_1400_timeslots,
                                               dfc_645_normalize,
                                               dfc_645_timeslots,
                                               output_dir)
    note = "Best cluster selection using Silhouette Score in 2-15 range"
    # show_clustering_results(None,
    #                         clustering_algorithm="KMeans",
    #                         comments=note,
    #                         file_path=output_dir + "/clusters.json",
    #                         csv_file_path="clusters.csv")


if __name__ == "__main__":
    main()
