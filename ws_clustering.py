import numpy as np
import ot
import matplotlib.pyplot as plt


def wasserstein_clustering(X, max_clusters=10, max_iter=100, tol=1e-3):
    """
    Clusters data using Wasserstein distance and the elbow method to determine the number of clusters.

    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
        Input data.
    max_clusters : int, optional (default=10)
        Maximum number of clusters to try.
    max_iter : int, optional (default=100)
        Maximum number of iterations for each cluster number.
    tol : float, optional (default=1e-3)
        Tolerance for convergence.

    Returns
    -------
    labels : array, shape (n_samples,)
        Cluster labels for each point.
    """
    wcss = []
    for n_clusters in range(1, max_clusters+1):
        # Initialize cluster centers randomly
        centers = np.random.rand(n_clusters, X.shape[1])

        for i in range(max_iter):
            # Compute the Wasserstein distances between each point and each center
            D = ot.dist(X, centers)

            # Assign each point to the nearest center
            labels = np.argmin(D, axis=1)

            # Update the cluster centers
            for j in range(n_clusters):
                centers[j] = np.mean(X[labels == j], axis=0)

            # Check for convergence
            if i > 0 and np.sum(labels == old_labels) == X.shape[0]:
                break

            old_labels = labels.copy()

        # Compute the within-cluster sum of squares (WCSS)
        wcss.append(np.sum((X - centers[labels])**2))

    # Choose the number of clusters based on the elbow point
    n_clusters = np.argmin(np.diff(wcss)) + 1

    # Cluster the data using the optimal number of clusters
    centers = np.random.rand(n_clusters, X.shape[1])
    for i in range(max_iter):
        D = ot.dist(X, centers)
        labels = np.argmin(D, axis=1)
        for j in range(n_clusters):
            centers[j] = np.mean(X[labels == j], axis=0)
        if i > 0 and np.sum(labels == old_labels) == X.shape[0]:
            break
        old_labels = labels.copy()

    return labels


if __name__ == "__main__":
    # Generate a sample dataset
    from sklearn.datasets import make_blobs

    X, y = make_blobs(n_samples=200, centers=4, random_state=42)

    # Cluster the data using Wasserstein distance and the elbow method
    labels = wasserstein_clustering(X)

    # Plot the clustering result and save it to a file
    plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis')
    plt.title('Wasserstein Clustering')
    plt.savefig('clustering_result.png')

    # Show the file path
    print('Clustering result saved to clustering_result.png')