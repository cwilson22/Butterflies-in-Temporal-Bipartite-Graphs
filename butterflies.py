import bisect
import pickle
import numpy
from graph_tool.all import *
from collections import defaultdict


#
# Returns the number of butterflies in a given graph. Runs efficiently in O(sum((d_u)^2)).
#
def enum_butterflies(filepath, num_left_nodes):
    g = load_graph(filepath)
    num_butterflies = 0
    for i in range(num_left_nodes):
        c = defaultdict(int)
        d = defaultdict(int)
        for neighbor1 in g.get_all_neighbors(g.vertex(i)):
            for neighbor2 in g.get_all_neighbors(g.vertex(neighbor1)):
                if neighbor2 != i:
                    c[neighbor2] += 1
                    d[str(neighbor1) + str(neighbor2)] += 1
        for val in c.values():
            num_butterflies += val * (val - 1) / 2
        for val in d.values():
            num_butterflies -= val * (val - 1) / 2
    return num_butterflies / 2


#
# Given a bipartite graph, lists all the butterflies present in the graph.
#
def list_butterflies(filepath, num_left_nodes):
    g = load_graph(filepath)
    butterflies = []

    for i in range(int(num_left_nodes)):
        paths = defaultdict(list)
        for e1 in g.get_all_edges(i, [g.ep.timestamps]):
            for e2 in g.get_all_edges(e1[1], [g.ep.timestamps]):
                if i < e2[1]:
                    paths[e2[1]].append([e1, numpy.array([e2[1], e2[0], e2[2]])])

        for path_list in paths.values():
            for j, path1 in enumerate(path_list):
                for path2 in path_list[j+1:]:
                    if path1[0][1] != path2[0][1]:
                        butterflies.append(path1 + path2)

    return butterflies


#
# Classify a collection of butterflies based on temporal ordering of their edges.
#
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


#
# Classify a single butterfly based on temporal ordering of the edges.
#
def classify_butterfly(butterfly, delta_w=0, delta_c=0):
    butterfly.sort(key=lambda echo: echo[2])
    if delta_w == 0 or butterfly[3][2] - butterfly[0][2] < delta_w:
        if delta_c == 0 or (butterfly[1][2] - butterfly[0][2] < delta_c and butterfly[2][2] - butterfly[1][2] < delta_c and butterfly[3][2] - butterfly[2][2] < delta_c):
            if butterfly[0][0] == butterfly[1][0] and butterfly[0][1] == butterfly[2][1]:
                return 0
            elif butterfly[0][0] == butterfly[1][0] and butterfly[0][1] == butterfly[3][1]:
                return 1
            elif butterfly[0][0] == butterfly[3][0] and butterfly[0][1] == butterfly[1][1]:
                return 2
            elif butterfly[0][0] == butterfly[2][0] and butterfly[0][1] == butterfly[1][1]:
                return 3
            elif butterfly[0][0] == butterfly[2][0] and butterfly[0][1] == butterfly[3][1]:
                return 4
            elif butterfly[0][0] == butterfly[3][0] and butterfly[0][1] == butterfly[2][1]:
                return 5
    return -1


def classify_butterfly2(b, delta_w=0, delta_c=0):
    if max(b[0][1], b[1][1], b[2][1], b[3][1]) - min(b[0][1], b[1][1], b[2][1], b[3][1]) < delta_w:
        if abs(b[0][1] - b[2][1]) < delta_c and abs(b[1][1] - b[1][1]) < delta_c:
            c = sorted([(-1, b[0][0], b[0][1]), (b[1][0], b[0][0], b[1][1]), (-1, b[2][0], b[2][1]), (b[3][0], b[2][0], b[3][1])], key=lambda echo: echo[2])
            if c[0][0] == c[1][0] and c[0][1] == c[2][1]:
                return 0
            elif c[0][0] == c[1][0] and c[0][1] == c[3][1]:
                return 1
            elif c[0][0] == c[3][0] and c[0][1] == c[1][1]:
                return 2
            elif c[0][0] == c[2][0] and c[0][1] == c[1][1]:
                return 3
            elif c[0][0] == c[2][0] and c[0][1] == c[3][1]:
                return 4
            elif c[0][0] == c[3][0] and c[0][1] == c[2][1]:
                return 5
    return -1


#
# Classifies all butterflies in a given graph without generating a complete list of butterflies, for space efficiency.
#
# Returns: The count for each of the six types of formation order.
#          The seventh entry is the butterflies which were discarded based on delta_w or delta_c.
#
def classify_without_listing(filepath, num_left_nodes, delta_w=0, delta_c=0):
    g = load_graph(filepath)
    class_counts = [0, 0, 0, 0, 0, 0, 0]

    for i in range(int(num_left_nodes)):
        paths = defaultdict(list)
        for e1 in g.get_all_edges(i, [g.ep.timestamps]):
            for e2 in g.get_all_edges(e1[1], [g.ep.timestamps]):
                if i < e2[1]:
                    paths[e2[1]].append([e1, numpy.array([e2[1], e2[0], e2[2]])])

        for path_list in paths.values():
            for j, path1 in enumerate(path_list):
                for path2 in path_list[j + 1:]:
                    if path1[0][1] != path2[0][1]:
                        class_counts[classify_butterfly(path1 + path2, delta_w, delta_c)] += 1

    return class_counts


#
# Classifies all butterflies in a given graph without generating a complete list of butterflies, for space efficiency.
#
# Note that the adjacency lists of the given graph must be sorted for this method to work.
#
# Returns: The count for each of the six types of formation order.
#          The seventh entry is the butterflies which were discarded based on delta_w or delta_c.
#
def classify_without_listing_sorted(filepath, num_left_nodes, delta_w=0, delta_c=0):
    with open(filepath, 'rb') as fd:
        edges = pickle.load(fd)

    if delta_c > delta_w:
        delta_w = delta_c
    elif delta_c < delta_w / 3:
        delta_c = delta_w / 3
    class_counts = [0, 0, 0, 0, 0, 0, 0]

    for i in range(num_left_nodes):
        paths = defaultdict(list)
        for e1 in edges[i]:
            j = bisect.bisect_left([a[1] for a in edges[e1[0]]], e1[1] - delta_c)
            while j < len(edges[e1[0]]) and abs(edges[e1[0]][j][1] - e1[1]) < delta_c:
                if i < edges[e1[0]][j][0]:
                    paths[edges[e1[0]][j][0]].append([e1, edges[e1[0]][j]])
                j += 1
            # for e2 in edges[e1[0]]:
            #     if i < e2[0] and abs(e2[1] - e1[1]) < delta_c:
            #         paths[e2[0]].append([e1, e2])

        for path_list in paths.values():
            for j, path1 in enumerate(path_list):
                for path2 in path_list[j:]:
                    if path1[0][0] != path2[0][0]:
                        if max(path1[0][1], path1[1][1], path2[0][1], path2[1][1]) - min(path1[0][1], path1[1][1], path2[0][1], path2[1][1]) < delta_w and abs(path1[0][1] - path2[0][1]) < delta_c and abs(path1[1][1] - path2[1][1]) < delta_c:
                            class_counts[classify_butterfly2(path1 + path2, delta_w, delta_c)] += 1

    return class_counts[:6]

