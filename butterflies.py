import sys
import numpy
from graph_tool.all import *
from collections import defaultdict


# def enum_butterflies(path, num_left_nodes):
#     g = load_graph(path + ".xml.gz")
#     num_butterflies = 0
#     for i in range(num_left_nodes):
#         c = defaultdict(int)
#         d = defaultdict(lambda: defaultdict(int))
#         m = defaultdict(int)
#         for neighbor1 in g.get_all_neighbors(g.vertex(i)):
#             m[neighbor1] += 1
#             for neighbor2 in g.get_all_neighbors(g.vertex(neighbor1)):
#                 if neighbor2 != i:
#                     c[neighbor2] += 1
#                     if m[neighbor1] == 1:
#                         d[neighbor2][neighbor1] += 1
#         for k, v in c.items():
#             num_butterflies += v * (v-1) / 2
#             for m_key, d_val in d[k].items():
#                 num_butterflies -= d_val * m[m_key] * (d_val * m[m_key] - 1) / 2
#     return num_butterflies / 2


def enum_butterflies(path, num_left_nodes):
    g = load_graph(path + ".xml.gz")
    num_butterflies = 0
    for i in range(num_left_nodes):
        c = defaultdict(int)
        d = defaultdict(lambda: defaultdict(int))
        for neighbor1 in g.get_all_neighbors(g.vertex(i)):
            for neighbor2 in g.get_all_neighbors(g.vertex(neighbor1)):
                if neighbor2 != i:
                    c[neighbor2] += 1
                    d[neighbor2][neighbor1] += 1
        for k, v in c.items():
            num_butterflies += v * (v-1) / 2
            for d_val in d[k].values():
                num_butterflies -= d_val * (d_val - 1) / 2
    return num_butterflies / 2


def list_butterflies(path, num_left_nodes):
    g = load_graph(path + ".xml.gz")
    butterflies = []

    print("Finding all the butterflies...")
    for i in range(int(num_left_nodes)):
        paths = []
        for e1 in g.get_all_edges(i, [g.ep.timestamps]):
            for e2 in g.get_all_edges(e1[1], [g.ep.timestamps]):
                if i < e2[1]:
                    paths.append([e1, numpy.array([e2[1], e2[0], e2[2]])])

        for j, path1 in enumerate(paths):
            for path2 in paths[j+1:]:
                if path1[1][0] == path2[1][0] and path1[0][1] != path2[0][1]:
                    butterflies.append(path1 + path2)

    return butterflies


def classify_butterflies(butterfly_list, delta_w=0, delta_c=0):
    classes = [[], [], [], [], [], []]
    class_counts = [0, 0, 0, 0, 0, 0]
    for butterfly in butterfly_list:
        temp = sorted(butterfly, key=lambda echo: echo[2])
        if delta_w == 0 or temp[3][2] - temp[0][2] < delta_w:
            if delta_c == 0 or (temp[1][2] - temp[0][2] < delta_c and temp[2][2] - temp[1][2] < delta_c and temp[3][2] - temp[2][2] < delta_c):
                if temp[0][0] == temp[1][0] and temp[0][1] == temp[2][1]:
                    classes[0].append(temp)
                    class_counts[0] += 1
                elif temp[0][0] == temp[1][0] and temp[0][1] == temp[3][1]:
                    classes[1].append(temp)
                    class_counts[1] += 1
                elif temp[0][0] == temp[3][0] and temp[0][1] == temp[1][1]:
                    classes[2].append(temp)
                    class_counts[2] += 1
                elif temp[0][0] == temp[2][0] and temp[0][1] == temp[1][1]:
                    classes[3].append(temp)
                    class_counts[3] += 1
                elif temp[0][0] == temp[2][0] and temp[0][1] == temp[3][1]:
                    classes[4].append(temp)
                    class_counts[4] += 1
                elif temp[0][0] == temp[3][0] and temp[0][1] == temp[2][1]:
                    classes[5].append(temp)
                    class_counts[5] += 1
    return class_counts, classes


def classify_butterfly(butterfly, delta_w=0, delta_c=0):
    temp = sorted(butterfly, key=lambda echo: echo[2])
    if delta_w == 0 or temp[3][2] - temp[0][2] < delta_w:
        if delta_c == 0 or (temp[1][2] - temp[0][2] < delta_c and temp[2][2] - temp[1][2] < delta_c and temp[3][2] - temp[2][2] < delta_c):
            if temp[0][0] == temp[1][0] and temp[0][1] == temp[2][1]:
                return 1
            elif temp[0][0] == temp[1][0] and temp[0][1] == temp[3][1]:
                return 2
            elif temp[0][0] == temp[3][0] and temp[0][1] == temp[1][1]:
                return 3
            elif temp[0][0] == temp[2][0] and temp[0][1] == temp[1][1]:
                return 4
            elif temp[0][0] == temp[2][0] and temp[0][1] == temp[3][1]:
                return 5
            elif temp[0][0] == temp[3][0] and temp[0][1] == temp[2][1]:
                return 6


def classify_without_listing(path, num_left_nodes, delta_w=0, delta_c=0):
    g = load_graph(path + ".xml.gz")
    class_counts = [0, 0, 0, 0, 0, 0]

    for i in range(int(num_left_nodes)):
        paths = []
        for e1 in g.get_all_edges(i, [g.ep.timestamps]):
            for e2 in g.get_all_edges(e1[1], [g.ep.timestamps]):
                if i < e2[1]:
                    paths.append([e1, numpy.array([e2[1], e2[0], e2[2]])])

        for j, path1 in enumerate(paths):
            for path2 in paths[j + 1:]:
                if path1[1][0] == path2[1][0] and path1[0][1] != path2[0][1]:
                    class_counts[classify_butterfly(path1 + path2, delta_w, delta_c)-1] += 1

    return class_counts


# if __name__ == '__main__':
#     if len(sys.argv) != 3 or type(sys.argv[1]) != str:
#         print("Error: Input should be the filepath for the graph followed by the size of the left node set.")
#         print(len(sys.argv))
#         sys.exit()
#     print("Extracting graph...")
#     butterfly_listing = list_butterflies(sys.argv[1], sys.argv[2])
#     print("Classifying...")
#     counts, groups = classify_butterflies(butterfly_listing)
#     print(f"Done! Here's the results for the {len(butterfly_listing)} butterflies found:")
#     print("\nCount for each type of butterfly formation")
#     print("------------------------------------------")
#     print(f"Type 1: {counts[0]}\tType 2: {counts[1]}\tType 3: {counts[2]}\tType 4: {counts[3]}\tType 5: {counts[4]}\tType 6: {counts[5]}\t")
#     # print("\nAnd the list of butterflies by type is:")
#     # print("--------------")
#     # print(f"Type 1: {butterflies[0]}")
#     # print(f"Type 2: {butterflies[1]}")
#     # print(f"Type 3: {butterflies[2]}")
#     # print(f"Type 4: {butterflies[3]}")
#     # print(f"Type 5: {butterflies[4]}")
#     # print(f"Type 6: {butterflies[5]}")
