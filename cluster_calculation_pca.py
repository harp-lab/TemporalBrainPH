import json
import math
import os
import csv
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from utils import timer, get_dataset


def get_highest_score(dataset):
    max_score = -math.inf
    number_of_clusters = 9
    for i in range(2, 16):
        cluster = KMeans(n_clusters=i, random_state=10)
        cluster_labels = cluster.fit_predict(dataset)
        score = silhouette_score(dataset, cluster_labels)
        if score > max_score:
            number_of_clusters = i
            max_score = score
    return number_of_clusters

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
                     subject_number, dfc_number, is_pca=False):
    dataset = []
    file_prefix = f"normalize_dfc_{dfc_number}_subject_"
    for i in range(1, dfc_timeslots + 1):
        filename = f'{dfc_normalize_path}/{file_prefix}{subject_number}_time_{i}.txt'
        dataset.append(get_dataset(filename=filename,
                                   fmri=True))
    three_dim_data = np.array(dataset)
    if is_pca:
        # Flatten to 2D
        data2d = three_dim_data.reshape(three_dim_data.shape[0], -1)
        # PCA with 2 components
        pca = PCA(n_components=2)
        pca.fit(data2d)
        two_dim_data = pca.transform(data2d)
    else:
        two_dim_data = three_dim_data.reshape(-1, three_dim_data.shape[1] *
                                              three_dim_data.shape[2])
    n_clusters, labels = get_labels_highest_score(two_dim_data)
    unique_labels = np.unique(labels)
    return n_clusters, labels, unique_labels, two_dim_data

def show_clusters(labels, unique_labels, dataset, title, index):
    ax = plt.subplot(1, 3, index)
    for i in unique_labels:
        x = dataset[labels == i, 0]
        y = dataset[labels == i, 1]
        label = f"cluster {i + 1}"
        if i == -1:
            label = "noise"
        ax.scatter(x, y, label=label, s=5)
        ax.legend()
    ax.set_title(title)
    plt.tight_layout()

def generate_kmeans_clusters(start_subject, end_subject,
                             dfc_2500_normalize_path,
                             dfc_2500_timeslots,
                             dfc_1400_normalize_path,
                             dfc_1400_timeslots,
                             dfc_645_normalize_path,
                             dfc_645_timeslots,
                             output_directory, is_pca=False):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    cluster_info = {}
    for subject_number in range(start_subject, end_subject + 1):
        print(f"Generating cluster for Subject: {subject_number}")
        n_clusters_2500, labels_2500, unique_labels_2500, dataset_2500 = get_cluster_info(
            dfc_2500_normalize_path, dfc_2500_timeslots,
            subject_number, 2500, is_pca=is_pca)
        n_clusters_1400, labels_1400, unique_labels_1400, dataset_1400 = get_cluster_info(
            dfc_1400_normalize_path, dfc_1400_timeslots,
            subject_number, 1400, is_pca=is_pca)
        n_clusters_645, labels_645, unique_labels_645, dataset_645 = get_cluster_info(
            dfc_645_normalize_path, dfc_645_timeslots,
            subject_number, 645, is_pca=is_pca)
        cluster_info[subject_number] = [
            n_clusters_2500, n_clusters_1400, n_clusters_645
        ]
        title = f'DFC2500: {n_clusters_2500} clusters'
        show_clusters(labels_2500, unique_labels_2500, dataset_2500, title, 1)
        title = f'DFC1400: {n_clusters_1400} clusters'
        show_clusters(labels_1400, unique_labels_1400, dataset_1400, title, 2)
        title = f'DFC645: {n_clusters_645} clusters'
        show_clusters(labels_645, unique_labels_645, dataset_645, title, 3)
        image_name = f"{output_directory}/subject_{subject_number}.png"
        plt.suptitle(f"Clustering for Subject {subject_number}")
        plt.gcf().set_size_inches(10, 4)
        plt.tight_layout()
        plt.savefig(image_name, dpi=250)
        plt.close()

        print(
            f"Generated cluster for Subject: {subject_number} {cluster_info[subject_number]}\n")
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


def show_pairwise_analysis(file_path):
    cluster_summary = json.load(open(file_path))
    dfc_2500_1400 = {}
    dfc_1400_645 = {}
    dfc_645_2500 = {}
    total_subjects = 0
    for subject in cluster_summary:
        dfc_2500, dfc_1400, dfc_645 = cluster_summary[subject]
        d_2500_1400 = abs(dfc_2500 - dfc_1400)
        d_1400_645 = abs(dfc_1400 - dfc_645)
        d_645_2500 = abs(dfc_645 - dfc_2500)
        dfc_2500_1400[d_2500_1400] = dfc_2500_1400.get(d_2500_1400, 0) + 1
        dfc_1400_645[d_1400_645] = dfc_1400_645.get(d_1400_645, 0) + 1
        dfc_645_2500[d_645_2500] = dfc_645_2500.get(d_645_2500, 0) + 1
        total_subjects += 1
    dfc_2500_1400 = sorted(dfc_2500_1400.items(), key=lambda x: x[0])
    dfc_1400_645 = sorted(dfc_1400_645.items(), key=lambda x: x[0])
    dfc_645_2500 = sorted(dfc_645_2500.items(), key=lambda x: x[0])
    # print(len(dfc_2500_1400), len(dfc_1400_645), len(dfc_645_2500))

    for i in range(
            max([len(dfc_2500_1400), len(dfc_1400_645), len(dfc_645_2500)])):
        dfc_2500_1400_subjects = 0
        dfc_1400_645_subjects = 0
        dfc_645_2500_subjects = 0
        if i < len(dfc_2500_1400):
            dfc_2500_1400_subjects = dfc_2500_1400[i][1]
        if i < len(dfc_1400_645):
            dfc_1400_645_subjects = dfc_1400_645[i][1]
        if i < len(dfc_645_2500):
            dfc_645_2500_subjects = dfc_645_2500[i][1]
        print(i, end=" & ")
        print(dfc_2500_1400_subjects, end=" & ")
        print(f"{(dfc_2500_1400_subjects / total_subjects) * 100:.3f}\\%",
              end=" & ")
        print(dfc_1400_645_subjects, end=" & ")
        print(f"{(dfc_1400_645_subjects / total_subjects) * 100:.3f}\\%",
              end=" & ")
        print(dfc_645_2500_subjects, end=" & ")
        print(f"{(dfc_645_2500_subjects / total_subjects) * 100:.3f}\\%",
              end=" \\\\ \hline \n")

def generate_three_cohorts_clusters_cheaha():
    output_dir = "../clusters_kmeans_pca"
    start_subject_number = 32
    end_subject_number = 32
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
                                               output_dir, is_pca=True)

@timer
def main():
    # The following code is to generate the clustering result in cheaha
    generate_three_cohorts_clusters_cheaha()

    # The following code is to show the clustering result
    # output_dir = "output/Old_formula_generated/clusters_kmeans_direct_clustering"
    # note = "Best cluster selection using Silhouette Score in 2-15 range"
    # show_clustering_results(None,
    #                         clustering_algorithm="KMeans",
    #                         comments=note,
    #                         file_path=output_dir + "/clusters.json",
    #                         csv_file_path="clusters_direct_clustering.csv")

    # The following code is to generate the pairwise clustering analysis
    # show_pairwise_analysis(
    #     file_path="output/Old_formula_generated/clusters_kmeans_without_mds_pca/clusters.json")


if __name__ == "__main__":
    main()
