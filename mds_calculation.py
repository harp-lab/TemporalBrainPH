from sklearn.manifold import MDS
import matplotlib.pyplot as plt


def get_mds(dissimilarity_matrix, is_euclidean=None):
    if is_euclidean:
        embedding = MDS(n_components=2, random_state=6)
    else:
        embedding = MDS(n_components=2, dissimilarity="precomputed",
                        random_state=6)
    return embedding.fit_transform(dissimilarity_matrix)


def plot_mds(mds_matrix, subject_number):
    plt.rcdefaults()
    x = mds_matrix[:, 0]
    y = mds_matrix[:, 1]
    plt.scatter(x, y)
    annotations = [str(i + 1) for i in range(len(x))]
    for i, label in enumerate(annotations):
        plt.annotate(label, (x[i] - 0.1, y[i] + 0.1), fontsize=7)
    plt.axis('equal')
    plt.title(f"Time slot MDS for Subject {subject_number}")
    plt.show()
