import json
import csv
import gudhi
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter


def draw_barcode_and_matrix(data, matrix):
    plt.rcdefaults()
    fig, ax = plt.subplots(1, 2)
    max_xaxis = sorted([i[1] for i in data], reverse=True)[0]
    y_pos = [i for i in range(len(data))]
    values = [pair[1] for pair in data]
    ax[0].barh(y_pos, values, align='center', height=0.6)
    ax[0].invert_yaxis()
    ax[0].set_xlabel('Delta')
    ax[0].set_title('Persistent barcodes (0 dimensional)')
    ax[0].set_xlim([0, max_xaxis])
    ax[0].bar_label(ax[0].containers[0])
    ax[0].get_yaxis().set_visible(False)
    ax[1].set_title('Adjacency matrix')
    matrix = [["{:.2f}".format(j) for j in ar] for ar in matrix]
    t = ax[1].table(cellText=matrix,
                    cellLoc='center',
                    rowLoc='center',
                    colLoc='center',
                    loc='center')
    t.scale(1, 4)
    ax[1].axis('off')
    plt.gcf().set_size_inches(8, 2.5)
    plt.tight_layout()
    output_filename = f'output/barcode_demo/barcode_matrix_title.png'
    plt.savefig(output_filename, bbox_inches='tight', dpi=600)
    print(f"Chart exported to: {output_filename}")


def draw_matrix_only(matrix):
    plt.rcdefaults()
    fig, ax = plt.subplots()
    matrix = [["{:.2f}".format(j) for j in ar] for ar in matrix]
    t = ax.table(cellText=matrix,
                 cellLoc='center',
                 rowLoc='center',
                 colLoc='center',
                 loc='center')
    t.scale(1, 3)
    ax.axis('off')
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    plt.gcf().set_size_inches(6, 2)
    plt.tight_layout()
    output_filename = f'output/barcode_demo/matrix.png'
    plt.savefig(output_filename, bbox_inches='tight', dpi=600)
    print(f"Chart exported to: {output_filename}")


def draw_barcode_only(data):
    plt.rcdefaults()
    fig, ax = plt.subplots()
    max_xaxis = sorted([i[1] for i in data], reverse=True)[0]
    y_pos = [i for i in range(len(data))]
    values = [pair[1] for pair in data]
    ax.barh(y_pos, values, height=0.3, align='center')
    ax.invert_yaxis()
    ax.set_xlabel('Delta')
    # ax.set_title('Persistent barcodes (0 dimensional)')
    ax.set_xlim([0, max_xaxis])
    ax.bar_label(ax.containers[0])
    ax.get_yaxis().set_visible(False)
    plt.tight_layout()
    plt.gcf().set_size_inches(6, 2)
    plt.tight_layout()
    output_filename = f'output/barcode_demo/barcode.png'
    plt.savefig(output_filename, bbox_inches='tight', dpi=600)
    print(f"Chart exported to: {output_filename}")


def draw_line_chart(datasets, dataset_titles,
                    x_label=None,
                    y_label=None,
                    title=None, figure_path=None, limit_y=None):
    fig, ax = plt.subplots(figsize=(8, 4))
    x = list(range(len(datasets[0])))
    for i in range(len(datasets)):
        ax.plot(x,
                datasets[i], label=dataset_titles[i], marker='o',
                markersize=5)
        for j in range(len(x)):
            plt.text(x[j], datasets[i][j] + 0.4, str(datasets[i][j]) + "%",
                     ha='center', va='bottom')
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    if title:
        ax.set_title(title)
    if limit_y:
        ax.set_ylim(0, 100)
    ax.legend()

    # plt.yscale("log")
    # plt.gca().yaxis.set_major_formatter(ScalarFormatter())
    ax.set_xticks(x)
    fig.tight_layout(pad=-3.0)
    if figure_path == None:
        figure_path = 'drawing/line.png'
    fig.savefig(figure_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved in {figure_path}")


def show_tda_nontda():
    first_dataset = [37.34, 22.15, 5.7, 5.38, 6.96, 4.11, 2.53, 3.48, 2.53, 2.53, 1.9, 1.58, 1.9, 1.9]
    first_dataset_title = "TDA"
    second_dataset = [.32, 1.27, 2.85, 4.75, 7.28, 11.08, 9.81, 8.86, 10.76, 10.13, 10.44, 10.13, 9.18, 3.16]
    second_dataset_title = "nonTDA"
    x_label = "Number of clusters"
    y_label = "Percentage of total subjects"
    title = "TDA and nonTDA distance comparison"
    draw_line_chart([first_dataset, second_dataset],
                    [first_dataset_title, second_dataset_title, ],
                    x_label, y_label,
                    figure_path="drawing/tda_nontda.png")


if __name__ == "__main__":
    # with open('output/barcode_demo/demo.csv', newline='') as f:
    #     reader = csv.reader(f)
    #     data = []
    #     for row in reader:
    #         record = []
    #         for val in row:
    #             record.append(float(val.strip()))
    #         data.append(record)
    # max_distance = max(map(max, data))
    # rips_complex = gudhi.RipsComplex(distance_matrix=data,
    #                                  max_edge_length=max_distance)
    # simplex_tree = rips_complex.create_simplex_tree(max_dimension=1)
    # pd = simplex_tree.persistence()[1:]
    # barcodes = [pair[1] for pair in pd]
    # barcodes.append([0, max_distance])
    # barcodes = sorted(barcodes, key=lambda x: -x[1])
    # draw_barcode_and_matrix(barcodes, data)
    # draw_matrix_only(data)

    # draw_barcode_only(barcodes)

    # diag = simplex_tree.persistence()
    # gudhi.plot_persistence_barcode(diag)
    # plt.show()

    show_tda_nontda()
