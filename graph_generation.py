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


def round_values(datasets, decimal_point=1):
    return [[round(i, decimal_point) for i in ar] for ar in datasets]


def draw_line_chart(datasets, dataset_titles,
                    x_label=None,
                    y_label=None,
                    title=None, figure_path=None, limit_y=None,
                    show_text_label=True,
                    log_scale=False):
    datasets = round_values(datasets)
    fig, ax = plt.subplots(figsize=(8, 4))
    x = list(range(len(datasets[0])))
    for i in range(len(datasets)):
        ax.plot(x,
                datasets[i], label=dataset_titles[i], marker='o',
                markersize=5)
        if show_text_label:
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

    if log_scale:
        plt.yscale("log")
        plt.gca().yaxis.set_major_formatter(ScalarFormatter())
    ax.set_xticks(x)
    fig.tight_layout(pad=-3.0)
    if figure_path == None:
        figure_path = 'drawing/line.png'
    fig.savefig(figure_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved in {figure_path}")


def show_pairwise_2500_1400():
    distance_2500_1400 = [
        54.43, 14.873, 5.696, 5.38, 6.329, 2.532, 0.949, 2.532, 1.899, 1.582,
        1.266, 0.316, 0.949, 1.266
    ]
    distance_2500_1400_title = "Distance 2500ms and 1400ms (TDA)"
    distance_2500_1400_nontda = [
        3.165, 9.81, 10.759, 9.81, 12.025, 11.709, 10.127, 5.696, 7.595, 5.063,
        5.063, 5.696, 2.848, 0.633
    ]
    distance_2500_1400_nontda_title = "Distance 2500ms and 1400ms (nonTDA)"
    x_label = "Cluster difference"
    y_label = "Percentage of total subjects"
    draw_line_chart([distance_2500_1400, distance_2500_1400_nontda],
                    [distance_2500_1400_title,
                     distance_2500_1400_nontda_title],
                    x_label, y_label,
                    figure_path="drawing/pairwise_2500_1400.png")


def show_pairwise_1400_645():
    distance_1400_645 = [
        55.696, 19.304, 3.797, 3.481, 2.848, 2.848, 2.532, 1.899, 0.949, 2.215,
        0.949, 1.582, 0.949, 0.949
    ]
    distance_1400_645_title = "Distance 1400ms and 645ms (TDA)"
    distance_1400_645_nontda = [12.342, 14.873, 12.975, 8.228, 11.076, 9.810,
                                7.595, 5.380, 7.911, 3.797, 2.215, 1.582,
                                1.266, 0.949]
    distance_1400_645_nontda_title = "Distance 1400ms and 645ms (nonTDA)"
    x_label = "Cluster difference"
    y_label = "Percentage of total subjects"
    draw_line_chart([distance_1400_645, distance_1400_645_nontda],
                    [distance_1400_645_title, distance_1400_645_nontda_title],
                    x_label, y_label,
                    figure_path="drawing/pairwise_1400_645.png",
                    log_scale=False)


def show_pairwise_645_2500():
    distance_645_2500 = [
        50.633, 20.570, 6.013, 2.532, 5.380, 3.165, 1.582, 2.848, 1.582, 0.949,
        1.266, 0.949, 1.899, 0.633
    ]
    distance_645_2500_title = "Distance 645ms and 2500ms (TDA)"
    distance_645_2500_nontda = [4.114, 7.278, 10.759, 10.127, 8.544, 5.696,
                                9.177, 6.962, 6.962, 6.329, 8.544, 6.962,
                                6.329, 2.215]
    distance_645_2500_nontda_title = "Distance 645ms and 2500ms (nonTDA)"

    x_label = "Cluster difference"
    y_label = "Percentage of total subjects"
    draw_line_chart([distance_645_2500, distance_645_2500_nontda],
                    [distance_645_2500_title, distance_645_2500_nontda_title],
                    x_label, y_label,
                    figure_path="drawing/pairwise_645_2500.png")


def show_tda_pairwise():
    distance_2500_1400 = [
        54.43, 14.873, 5.696, 5.38, 6.329, 2.532, 0.949, 2.532, 1.899, 1.582,
        1.266, 0.316, 0.949, 1.266
    ]
    distance_2500_1400_title = "Distance 2500ms and 1400ms"
    distance_1400_645 = [
        55.696, 19.304, 3.797, 3.481, 2.848, 2.848, 2.532, 1.899, 0.949, 2.215,
        0.949, 1.582, 0.949, 0.949
    ]
    distance_1400_645_title = "Distance 1400ms and 645ms"
    distance_645_2500 = [
        50.633, 20.570, 6.013, 2.532, 5.380, 3.165, 1.582, 2.848, 1.582, 0.949,
        1.266, 0.949, 1.899, 0.633
    ]
    distance_645_2500_title = "Distance 645ms and 2500ms"

    x_label = "Cluster difference"
    y_label = "Percentage of total subjects"
    draw_line_chart([distance_2500_1400, distance_1400_645, distance_645_2500],
                    [distance_2500_1400_title, distance_1400_645_title,
                     distance_645_2500_title],
                    x_label, y_label,
                    figure_path="drawing/tda_pairwise.png",
                    show_text_label=False)


def show_nontda_pairwise():
    distance_2500_1400_nontda = [
        3.165, 9.81, 10.759, 9.81, 12.025, 11.709, 10.127, 5.696, 7.595, 5.063,
        5.063, 5.696, 2.848, 0.633
    ]
    distance_2500_1400_nontda_title = "Distance 2500ms and 1400ms"
    distance_1400_645_nontda = [12.342, 14.873, 12.975, 8.228, 11.076, 9.810,
                                7.595, 5.380, 7.911, 3.797, 2.215, 1.582,
                                1.266, 0.949]
    distance_1400_645_nontda_title = "Distance 1400ms and 645ms"
    distance_645_2500_nontda = [4.114, 7.278, 10.759, 10.127, 8.544, 5.696,
                                9.177, 6.962, 6.962, 6.329, 8.544, 6.962,
                                6.329, 2.215]
    distance_645_2500_nontda_title = "Distance 645ms and 2500ms"
    x_label = "Cluster difference"
    y_label = "Percentage of total subjects"
    draw_line_chart([distance_2500_1400_nontda, distance_1400_645_nontda,
                     distance_645_2500_nontda],
                    [distance_2500_1400_nontda_title,
                     distance_1400_645_nontda_title,
                     distance_645_2500_nontda_title],
                    x_label, y_label,
                    figure_path="drawing/nontda_pairwise.png",
                    show_text_label=False)


def show_tda_nontda():
    first_dataset = [37.34, 22.15, 5.7, 5.38, 6.96, 4.11, 2.53, 3.48, 2.53,
                     2.53, 1.9, 1.58, 1.9, 1.9]
    first_dataset_title = "TDA"
    second_dataset = [.32, 1.27, 2.85, 4.75, 7.28, 11.08, 9.81, 8.86, 10.76,
                      10.13, 10.44, 10.13, 9.18, 3.16]
    second_dataset_title = "nonTDA"
    x_label = "Cluster difference"
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
    show_nontda_pairwise()
    show_pairwise_2500_1400()
    show_pairwise_645_2500()
    # show_pairwise_1400_645()
