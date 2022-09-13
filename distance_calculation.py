import json
import gudhi
import gudhi.wasserstein
import numpy as np
from utils import get_dataset, timer
from mds_calculation import get_mds
import os
import argparse


def get_barcodes_distance(dgm_1, dgm_2, distance_method='ws'):
    if distance_method == 'ws':
        return gudhi.wasserstein.wasserstein_distance(dgm_1, dgm_2,
                                                      order=1., internal_p=2.)
    elif distance_method == 'bn':
        return gudhi.bottleneck_distance(dgm_1, dgm_2)


@timer
def get_mds_matrix(subject_id, json_directory):
    data_path = f'{json_directory}/subject_{subject_id}.json'
    dissimilarity_matrix = np.array(json.loads(open(data_path, "r").read()))
    mds_matrix = get_mds(dissimilarity_matrix)
    return json.dumps(mds_matrix.tolist())


@timer
def get_distance_matrix(data_dir, subject_number, timeslots,
                        normalize_file_prefix, distance_method='ws'):
    dissimilarity_matrix = np.array([[0.0 for j in range(timeslots)] for i in
                                     range(timeslots)])
    barcodes = {}
    for i in range(1, timeslots + 1):
        time_1 = f"time_{i}"
        if time_1 not in barcodes:
            filepath_1 = f'{data_dir}/{normalize_file_prefix}{subject_number}_time_{i}.txt'
            adjacency_matrix_1 = get_dataset(filename=filepath_1, fmri=True)
            rips_complex_1 = gudhi.RipsComplex(
                distance_matrix=adjacency_matrix_1)
            pd_1 = rips_complex_1.create_simplex_tree(
                max_dimension=1).persistence()[1:]
            barcodes_1 = np.array([pair[1] for pair in pd_1])
            barcodes[time_1] = barcodes_1
        else:
            barcodes_1 = barcodes[time_1]
        for j in range(1, i):
            time_2 = f"time_{j}"
            if time_2 not in barcodes:
                filepath_2 = f'{data_dir}/{normalize_file_prefix}{subject_number}_time_{j}.txt'
                adjacency_matrix_2 = get_dataset(filename=filepath_2,
                                                 fmri=True)
                rips_complex_2 = gudhi.RipsComplex(
                    distance_matrix=adjacency_matrix_2)
                pd_2 = rips_complex_2.create_simplex_tree(
                    max_dimension=1).persistence()[1:]
                barcodes_2 = np.array([pair[1] for pair in pd_2])
                barcodes[time_2] = barcodes_2
            else:
                barcodes_2 = barcodes[time_2]
            distance = get_barcodes_distance(barcodes_1,
                                             barcodes_2,
                                             distance_method=distance_method)
            distance = round(distance, 3)
            dissimilarity_matrix[i - 1][j - 1] = distance
            dissimilarity_matrix[j - 1][i - 1] = distance
    return dissimilarity_matrix


@timer
def generate_distance_matrix(data_dir, distance_directory,
                             total_subjects, total_timeslots,
                             normalize_file_prefix, start_subject=None,
                             end_subject=None, distance_method='ws'):
    if not os.path.exists(distance_directory):
        os.makedirs(distance_directory)
    if start_subject == None:
        start_subject = 1
        end_subject = total_subjects
    for subject_number in range(start_subject, end_subject + 1):
        print(f"Generating distance matrix for Subject {subject_number}")
        generated_json = f'{distance_directory}/subject_{subject_number}.json'
        dissimilarity_matrix = get_distance_matrix(data_dir,
                                                   subject_number,
                                                   total_timeslots,
                                                   normalize_file_prefix,
                                                   distance_method)
        with open(generated_json, "w") as f:
            json.dump(dissimilarity_matrix.tolist(), f)
            print(
                f"{distance_method} distance JSON created for Subject {subject_number}")
    print("Done generating the {distance_method} distance matrix JSON files")


@timer
def generate_mds(mds_directory, json_directory, total_subjects,
                 start_subject=None,
                 end_subject=None, distance_method='ws'
                 ):
    if not os.path.exists(mds_directory):
        os.makedirs(mds_directory)
    if start_subject == None:
        start_subject = 1
        end_subject = total_subjects
    for subject_number in range(start_subject, end_subject + 1):
        generated_mds = f'{mds_directory}/subject_{subject_number}.json'
        mds_matrix = get_mds_matrix(subject_number, json_directory)
        with open(generated_mds, "w") as f:
            json.dump(mds_matrix, f)
            print(f"MDS JSON created for Subject {subject_number}")
    print("Done generating the MDS JSON files")


def get_user_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', '-d',
                        help='Enter one of the DFC dataset (645, 1400, 2500)')
    parser.add_argument('--method', '-m',
                        help='Enter one of the distance method (ws, bn)')
    parser.add_argument('--start', '-s',
                        help='Enter start subject (1, 316)')
    parser.add_argument('--end', '-e',
                        help='Enter end subject (1, 316)')
    parser.add_argument('--distance', '-p',
                        help='To calculate distance matrix (y or n)')
    parser.add_argument('--mds', '-q',
                        help='To calculate MDS (y or n)')

    args = parser.parse_args()
    if args.data:
        main(int(args.data), args.method, start_subject=int(args.start),
             end_subject=int(args.end),
             distance_calculation=args.distance,
             mds_calculation=args.mds)
        return
    parser.print_help()


@timer
def main(dataset, method, start_subject=1, end_subject=316,
         distance_calculation='y', mds_calculation='y'):
    if dataset == 2500:
        # DFC 2500
        data_directory = "../dfc_2500_normal"
        # data_directory = "fmri_data"
        distance_matrix_directory = "../dfc_2500_subjects_distance_matrix_" + method
        mds_directory = "../dfc_2500_subjects_mds_" + method
        normalize_file_prefix = 'normalize_dfc_2500_subject_'
        total_subjects = 316
        total_timeslots = 86
    elif dataset == 1400:
        # DFC 1400
        data_directory = "../dfc_1400_normal"
        distance_matrix_directory = "../dfc_1400_subjects_distance_matrix_" + method
        mds_directory = "../dfc_1400_subjects_mds_" + method
        normalize_file_prefix = 'normalize_dfc_1400_subject_'
        total_subjects = 316
        total_timeslots = 336
    elif dataset == 645:
        # DFC 645
        data_directory = "../dfc_645_normal"
        distance_matrix_directory = "../dfc_645_subjects_distance_matrix_" + method
        mds_directory = "../dfc_645_subjects_mds_" + method
        normalize_file_prefix = 'normalize_dfc_645_subject_'
        total_subjects = 316
        total_timeslots = 754
    if distance_calculation == 'y':
        generate_distance_matrix(data_directory, distance_matrix_directory,
                                 total_subjects, total_timeslots,
                                 normalize_file_prefix, start_subject,
                                 end_subject,
                                 distance_method=method)
    if mds_calculation == 'y':
        generate_mds(mds_directory, distance_matrix_directory, total_subjects,
                     1, total_subjects, distance_method=method)


if __name__ == "__main__":
    get_user_input()
