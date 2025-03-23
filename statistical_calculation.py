import json
import argparse
import csv
import matplotlib.pyplot as plt


def draw_line_chart(x, y, y_limit_bottom=None, y_limit_top=None,
                    x_limit_left=None, x_limit_right=None,
                    x_axis_label=None,
                    y_axis_label=None, legend=None, title=None,
                    output_filename=None):
    if legend:
        plt.plot(x, y, label=legend)
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0)
    if x_axis_label:
        plt.xlabel(x_axis_label)
    if y_axis_label:
        plt.ylabel(y_axis_label)
    if title:
        plt.title(title)
    if y_limit_bottom != None and y_limit_top != None:
        plt.ylim([y_limit_bottom, y_limit_top])
    elif y_limit_bottom != None and y_limit_top == None:
        plt.ylim(bottom=y_limit_bottom)
    elif y_limit_top != None and y_limit_bottom == None:
        plt.ylim(top=y_limit_top)
    if x_limit_left != None and x_limit_right != None:
        plt.xlim([x_limit_left, x_limit_right])
    elif x_limit_left != None and x_limit_right == None:
        plt.xlim(left=x_limit_left)
    elif x_limit_right != None and x_limit_left == None:
        plt.xlim(right=x_limit_right)
    plt.gcf().set_size_inches(8, 4)
    plt.tight_layout()
    output_filename = f'output/{output_filename}'
    plt.savefig(output_filename, bbox_inches='tight', dpi=600)
    print(f"Chart exported to: {output_filename}")


def draw_scatter_chart(x, y, y_limit_bottom=None, y_limit_top=None,
                       x_limit_left=None, x_limit_right=None,
                       x_axis_label=None,
                       y_axis_label=None, legend=None, title=None,
                       output_filename=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if legend:
        dfc_2500 = [row[0] for row in y]
        dfc_1400 = [row[1] for row in y]
        dfc_645 = [row[2] for row in y]
        ax.scatter(x, dfc_2500, label=legend[0])
        ax.scatter(x, dfc_1400, label=legend[1])
        ax.scatter(x, dfc_645, label=legend[2])
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0)
    if x_axis_label:
        plt.xlabel(x_axis_label)
    if y_axis_label:
        plt.ylabel(y_axis_label)
    if title:
        plt.title(title)
    if y_limit_bottom != None and y_limit_top != None:
        plt.ylim([y_limit_bottom, y_limit_top])
    elif y_limit_bottom != None and y_limit_top == None:
        plt.ylim(bottom=y_limit_bottom)
    elif y_limit_top != None and y_limit_bottom == None:
        plt.ylim(top=y_limit_top)
    if x_limit_left != None and x_limit_right != None:
        plt.xlim([x_limit_left, x_limit_right])
    elif x_limit_left != None and x_limit_right == None:
        plt.xlim(left=x_limit_left)
    elif x_limit_right != None and x_limit_left == None:
        plt.xlim(right=x_limit_right)
    plt.gcf().set_size_inches(8, 4)
    plt.tight_layout()
    output_filename = f'output/{output_filename}'
    plt.savefig(output_filename, bbox_inches='tight', dpi=600)
    print(f"Chart exported to: {output_filename}")


def get_user_input():
    parser = argparse.ArgumentParser()
    data_help_text = "Enter one of the clustering result JSON file path"
    data_help_text += "(output/clusters_kmeans/clusters.json , " \
                      "output/clusters_kmeans_non_tda/clusters.json)"
    parser.add_argument('--data', '-d',
                        help=data_help_text)
    args = parser.parse_args()
    if args.data:
        main(args.data)
        return
    parser.print_help()


def main(data):
    subject_numbers = [i for i in range(1, 317)]
    with open(data) as fp:
        clusters = json.load(fp)
        clusters_2500 = [clusters[subject][0] for subject in clusters]
        clusters_1400 = [clusters[subject][1] for subject in clusters]
        clusters_645 = [clusters[subject][2] for subject in clusters]
        header = ["2500ms", "1400ms", "645ms"]
        rows = [[clusters_2500[i], clusters_1400[i], clusters_645[i]]
                for i in range(len(clusters_2500))]
        output_filename_line = "TDA_clusters_line.png"
        output_filename_scatter = "TDA_clusters_scatter.png"
        if "non_tda" in data:
            output_filename_line = "Non_TDA_clusters_line.png"
            output_filename_scatter = "Non_TDA_clusters_scatter.png"

        draw_line_chart(subject_numbers, rows,
                        x_axis_label="Subject ID",
                        y_axis_label="Number of clusters",
                        x_limit_left=0, x_limit_right=316, y_limit_bottom=0,
                        legend=header, output_filename=output_filename_line)

        draw_scatter_chart(subject_numbers, rows,
                           x_axis_label="Subject ID",
                           y_axis_label="Number of clusters",
                           x_limit_left=0, x_limit_right=316, y_limit_bottom=0,
                           legend=header,
                           output_filename=output_filename_scatter)

        # with open("clusters.csv", "w") as csv_file:
        #     csv_writer = csv.writer(csv_file)
        #     csv_writer.writerow(header)
        #     csv_writer.writerows(rows)


if __name__ == "__main__":
    get_user_input()

# Run:
# python statistical_calculation.py -d output/clusters_kmeans/clusters.json
# python statistical_calculation.py -d output/clusters_kmeans_non_tda/clusters.json