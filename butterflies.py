import sys
import numpy
from graph_tool.all import *
from collections import defaultdict


def enum_butterflies(path, num_left_nodes):
    g = load_graph(path + ".xml.gz")
    num_butterflies = 0
    for i in range(num_left_nodes):
        c = defaultdict(int)
        d = defaultdict(lambda: defaultdict(int))
        m = defaultdict(int)
        for neighbor1 in g.get_all_neighbors(g.vertex(i)):
            m[neighbor1] += 1
            for neighbor2 in g.get_all_neighbors(g.vertex(neighbor1)):
                if neighbor2 != i:
                    c[neighbor2] += 1
                    if m[neighbor1] == 1:
                        d[neighbor2][neighbor1] += 1
        for k, v in c.items():
            num_butterflies += v * (v-1) / 2
            for m_key, d_val in d[k].items():
                num_butterflies -= d_val * m[m_key] * (d_val * m[m_key] - 1) / 2
    return num_butterflies / 2


# def list_butterflies(path, num_left_nodes):
#     g = load_graph(path + ".xml.gz")
#     butterflies = []
#     # num_butterflies = 0
#     for i in range(num_left_nodes):
#         c = defaultdict(int)
#         d = defaultdict(lambda: defaultdict(int))
#         m = defaultdict(int)
#         paths = []
#         for e1 in g.get_all_edges(g.vertex(i)):
#             m[e1[1]] += 1
#             for e2 in g.get_all_edges(g.vertex(e1[1])):
#                 if e2[1] != i:
#                     c[e2] += 1
#                     if m[e1] == 1:
#                         d[e2][e1] += 1
#                     paths.append([i, e2, e1])
#         # for k, v in c.items():
#         #     num_butterflies += v * (v-1) / 2
#         #     for m_key, d_val in d[k].items():
#         #         num_butterflies -= d_val * m[m_key] * (d_val * m[m_key] - 1) / 2
#         # print(i, num_butterflies, c, m, d)
#         for j, path1 in enumerate(paths):
#             for path2 in paths[j+1:]:
#                 if path1[1] == path2[1] and path1[2] != path2[2]:
#                     butterflies.append(path1 + [path2[2]])
#     return butterflies


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


def classify_butterflies(butterfly_list):
    classes = [[], [], [], [], [], []]
    class_counts = [0, 0, 0, 0, 0, 0]
    for butterfly in butterfly_list:
        temp = sorted(butterfly, key=lambda echo: echo[2])
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


def classify_butterfly(butterfly):
    temp = sorted(butterfly, key=lambda echo: echo[2])
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


# def list_butterflies(path, num_left_nodes):
#     g = load_graph(path + ".xml.gz")
#     butterflies = []
#     num_butterflies = 0
#     for i in range(num_left_nodes):
#         c = {}
#         d = {}
#         m = {}
#         paths = []
#         for neighbor1 in g.get_all_neighbors(g.vertex(i)):
#             if neighbor1 in m.keys():
#                 m[neighbor1] += 1
#             else:
#                 m[neighbor1] = 1
#             for neighbor2 in g.get_all_neighbors(g.vertex(neighbor1)):
#                 if neighbor2 != i:
#                     if neighbor2 in c.keys():
#                         c[neighbor2] += 1
#                     else:
#                         c[neighbor2] = 1
#                     if m[neighbor1] == 1:
#                         if neighbor2 not in d.keys():
#                             d[neighbor2] = {}
#                         if neighbor1 in d[neighbor2].keys():
#                             d[neighbor2][neighbor1] += 1
#                         else:
#                             d[neighbor2][neighbor1] = 1
#                         paths.append([i, neighbor2, neighbor1])
#         for k, v in c.items():
#             num_butterflies += v * (v - 1) / 2
#             for m_key, m_val in d[k].items():
#                 num_butterflies -= m_val * m[m_key] * (m_val * m[m_key] - 1) / 2
#         print(i, num_butterflies, c, m, d)
#         for j, path1 in enumerate(paths):
#             for path2 in paths[j+1:]:
#                 if path1[1] == path2[1]:
#                     butterflies.append(path1 + [path2[2]])
#         print(i, c, butterflies)
#     return num_butterflies / 2


# print(classify_butterflies(list_butterflies("../edit-rmwikibooks/out.edit-rmwikibooks", 21)))

if __name__ == '__main__':
    if len(sys.argv) != 3 or type(sys.argv[1]) != str:
        print("Error: Input should be the filepath for the graph followed by the size of the left node set.")
        print(len(sys.argv))
        sys.exit()
    print("Extracting graph...")
    butterfly_list = list_butterflies(sys.argv[1], sys.argv[2])
    print("Classifying...")
    counts, butterflies = classify_butterflies(butterfly_list)
    print(f"Done! Here's the results for the {len(butterfly_list)} butterflies found:")
    print("\nCount for each type of butterfly formation")
    print("------------------------------------------")
    print(f"Type 1: {counts[0]}\tType 2: {counts[1]}\tType 3: {counts[2]}\tType 4: {counts[3]}\tType 5: {counts[4]}\tType 6: {counts[5]}\t")
    # print("\nAnd the list of butterflies by type is:")
    # print("--------------")
    # print(f"Type 1: {butterflies[0]}")
    # print(f"Type 2: {butterflies[1]}")
    # print(f"Type 3: {butterflies[2]}")
    # print(f"Type 4: {butterflies[3]}")
    # print(f"Type 5: {butterflies[4]}")
    # print(f"Type 6: {butterflies[5]}")
