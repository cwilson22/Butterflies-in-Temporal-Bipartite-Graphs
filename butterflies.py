import csv
import itertools
from math import ceil
import random
import re
import pickle
import numpy
# from graph_tool.all import *
from collections import defaultdict
import cProfile


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


def enum_butterflies2(filepath, num_left_nodes):
    with open(filepath, 'rb') as fd:
        edges = pickle.load(fd)
    num_butterflies = 0
    for i in range(num_left_nodes):
        c = defaultdict(int)
        d = defaultdict(int)
        for e1 in edges[i]:
            for e2 in edges[e1[0]]:
                if e2[0] != i:
                    c[e2[0]] += 1
                    d[e1[0]*num_left_nodes + e2[0]] += 1
        for val in c.values():
            num_butterflies += val * (val - 1) / 2
        for val in d.values():
            num_butterflies -= val * (val - 1) / 2
    return num_butterflies / 2


def priority_gt(u, v, edges):
    if len(edges[u]) > len(edges[v]) or (len(edges[u]) == len(edges[v]) and u > v):
        return True
    return False


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


def list_butterflies2(filepath, num_left_nodes):
    with open(filepath, 'rb') as fd:
        edges = pickle.load(fd)
    butterflies = []

    for i in range(int(num_left_nodes)):
        paths = defaultdict(list)
        for e1 in edges[i]:
            for e2 in edges[e1[0]]:
                if i < e2[0]:
                    paths[e2[0]].append([e1, e2])

        for path_list in paths.values():
            for j, path1 in enumerate(path_list):
                for path2 in path_list[j:]:
                    if path1[0][0] != path2[0][0]:
                        butterflies.append(path1 + path2)

    return butterflies


#
# Classify a single butterfly based on temporal ordering of the edges.
#
def classify_butterfly(butterfly, delta_w=0, delta_c=0):
    if delta_c == 0 or abs(butterfly[1][2] - butterfly[0][2]) < delta_c and abs(butterfly[2][2] - butterfly[0][2]) < delta_c and abs(butterfly[3][2] - butterfly[1][2]) < delta_c and abs(butterfly[3][2] - butterfly[2][2]) < delta_c:
        butterfly.sort(key=lambda echo: echo[2])
        if delta_w == 0 or butterfly[3][2] - butterfly[0][2] < delta_w:
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


def classify_butterfly2(b, delta_c, delta_w=0):
    if not check_any_equal(b):
        c = sorted([(-1, b[0][0], b[0][1]), (b[1][0], b[0][0], b[1][1]), (-1, b[2][0], b[2][1]), (b[3][0], b[2][0], b[3][1])], key=lambda echo: echo[2])
        if abs(c[1][2] - c[0][2]) <= delta_c and abs(c[2][2] - c[1][2]) <= delta_c and abs(c[3][2] - c[2][2]) <= delta_c:
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


def classify_butterfly3(b, delta_w=0, delta_c=0, old=False):
    if not check_any_equal(b) or old:
        if abs(b[2][1] - b[0][1]) <= delta_c and abs(b[3][1] - b[1][1]) <= delta_c:
            if delta_w == 0 or max(b[0][1], b[1][1], b[2][1], b[3][1]) - min(b[0][1], b[1][1], b[2][1], b[3][1]) <= delta_w:
                if b[0][1] <= b[1][1]:
                    if b[0][1] <= b[2][1]:
                        if b[1][1] <= b[2][1]:  # a <= b <= c
                            if b[2][1] <= b[3][1]:
                                return 3
                            elif b[1][1] <= b[3][1]:
                                return 2
                            elif b[0][1] <= b[3][1]:
                                return 5
                            else:
                                return 4
                        else:  # a <= c <= b
                            if b[1][1] <= b[3][1]:
                                return 0
                            elif b[2][1] <= b[3][1]:
                                return 1
                            elif b[0][1] <= b[3][1]:
                                return 4
                            else:
                                return 5
                    else:  # c <= a <= b
                        if b[1][1] <= b[3][1]:
                            return 1
                        elif b[0][1] <= b[3][1]:
                            return 0
                        elif b[2][1] <= b[3][1]:
                            return 3
                        else:
                            return 2
                else:  # b <= a
                    if b[0][1] <= b[2][1]:  # b <= a <= c
                        if b[2][1] <= b[3][1]:
                            return 2
                        elif b[0][1] <= b[3][1]:
                            return 3
                        elif b[1][1] <= b[3][1]:
                            return 0
                        else:
                            return 1
                    else:
                        if b[1][1] <= b[2][1]:  # b <= c <= a
                            if b[0][1] <= b[3][1]:
                                return 5
                            elif b[2][1] <= b[3][1]:
                                return 4
                            elif b[1][1] <= b[3][1]:
                                return 1
                            else:
                                return 0
                        else:  # c <= b <= a
                            if b[0][1] <= b[3][1]:
                                return 4
                            elif b[1][1] <= b[3][1]:
                                return 5
                            elif b[2][1] <= b[3][1]:
                                return 2
                            else:
                                return 3
    return -1


def classify_butterfly4(b, delta_c):
    if not check_any_equal(b):
        t1 = b[0][1]
        t2 = b[1][1]
        t3 = b[2][1]
        b.sort(key=lambda echo: echo[1])
        if abs(b[0][1] - b[1][1]) <= delta_c and abs(b[1][1] - b[2][1]) <= delta_c and abs(b[2][1] - b[3][1]) <= delta_c:
            if t1 == b[0][1]:
                if t2 == b[1][1]:
                    if t3 == b[2][1]:
                        return 3
                    else:
                        return 2
                elif t3 == b[1][1]:
                    if t2 == b[2][1]:
                        return 0
                    else:
                        return 1
                elif t2 == b[2][1]:
                    return 5
                else:
                    return 4
            elif t1 == b[1][1]:
                if t2 == b[0][1]:
                    if t3 == b[2][1]:
                        return 2
                    else:
                        return 3
                elif t3 == b[0][1]:
                    if t2 == b[2][1]:
                        return 1
                    else:
                        return 0
                elif t2 == b[2][1]:
                    return 4
                else:
                    return 5
            elif t1 == b[2][1]:
                if t2 == b[0][1]:
                    if t3 == b[1][1]:
                        return 5
                    else:
                        return 0
                elif t3 == b[0][1]:
                    if t2 == b[1][1]:
                        return 4
                    else:
                        return 3
                elif t2 == b[1][1]:
                    return 1
                else:
                    return 2
            else:
                if t2 == b[0][1]:
                    if t3 == b[1][1]:
                        return 4
                    else:
                        return 1
                elif t3 == b[0][1]:
                    if t2 == b[1][1]:
                        return 5
                    else:
                        return 2
                elif t2 == b[1][1]:
                    return 0
                else:
                    return 3
    return -1


def classify_butterfly5(b, delta_c):
    if (max(b[0][1], b[1][1], b[2][1], b[3][1]) - min(b[0][1], b[1][1], b[2][1], b[3][1]))/3 <= delta_c:
        if not check_any_equal(b):
            if b[0][1] <= b[1][1]:
                if b[0][1] <= b[2][1]:
                    if b[1][1] <= b[2][1]:  # a <= b <= c
                        if b[2][1] <= b[3][1]:
                            return 3
                        elif b[1][1] <= b[3][1]:
                            return 2
                        elif b[0][1] <= b[3][1]:
                            return 5
                        else:
                            return 4
                    else:  # a <= c <= b
                        if b[1][1] <= b[3][1]:
                            return 0
                        elif b[2][1] <= b[3][1]:
                            return 1
                        elif b[0][1] <= b[3][1]:
                            return 4
                        else:
                            return 5
                else:  # c <= a <= b
                    if b[1][1] <= b[3][1]:
                        return 1
                    elif b[0][1] <= b[3][1]:
                        return 0
                    elif b[2][1] <= b[3][1]:
                        return 3
                    else:
                        return 2
            else:  # b <= a
                if b[0][1] <= b[2][1]:  # b <= a <= c
                    if b[2][1] <= b[3][1]:
                        return 2
                    elif b[0][1] <= b[3][1]:
                        return 3
                    elif b[1][1] <= b[3][1]:
                        return 0
                    else:
                        return 1
                else:
                    if b[1][1] <= b[2][1]:  # b <= c <= a
                        if b[0][1] <= b[3][1]:
                            return 5
                        elif b[2][1] <= b[3][1]:
                            return 4
                        elif b[1][1] <= b[3][1]:
                            return 1
                        else:
                            return 0
                    else:  # c <= b <= a
                        if b[0][1] <= b[3][1]:
                            return 4
                        elif b[1][1] <= b[3][1]:
                            return 5
                        elif b[2][1] <= b[3][1]:
                            return 2
                        else:
                            return 3
    return -1


def classify_butterfly6(b, delta_c):
    c = [(b[0][0], b[0][1]), (b[1][0], b[1][1]), (b[2][0], b[2][1]), (b[3][0], b[3][1])]
    b.sort(key=lambda echo: echo[1])
    if abs(b[0][1] - b[1][1]) <= delta_c and abs(b[1][1] - b[2][1]) <= delta_c and abs(b[2][1] - b[3][1]) <= delta_c:
        if c[0][1] == c[1][1]:
            if c[0][1] == c[2][1]:
                if c[0][1] == c[3][1]:
                    return 20
                else:
                    if c[0][1] < c[3][1]:
                        return 19
                    else:
                        return 18
            elif c[0][1] == c[3][1]:
                if c[0][1] < c[2][1]:
                    return 19
                else:
                    return 18
            elif c[2][1] == c[3][1]:
                return 16
            else:
                if c[0][1] < c[2][1]:
                    if c[0][1] < c[3][1]:
                        return 9
                    else:
                        return 10
                else:
                    if c[0][1] < c[3][1]:
                        return 10
                    else:
                        return 11
        elif c[0][1] == c[2][1]:
            if c[0][1] == c[3][1]:
                if c[0][1] < c[1][1]:
                    return 19
                else:
                    return 18
            elif c[1][1] == c[3][1]:
                return 15
            else:
                if c[0][1] < c[1][1]:
                    if c[0][1] < c[3][1]:
                        return 6
                    else:
                        return 7
                else:
                    if c[0][1] < c[3][1]:
                        return 7
                    else:
                        return 8
        elif c[0][1] == c[3][1]:
            if c[1][1] == c[2][1]:
                return 17
            else:
                if c[0][1] < c[1][1]:
                    if c[0][1] < c[2][1]:
                        return 12
                    else:
                        return 13
                else:
                    if c[0][1] < c[2][1]:
                        return 13
                    else:
                        return 14
        elif c[1][1] == c[2][1]:
            if c[1][1] == c[3][1]:
                if c[0][1] < c[1][1]:
                    return 18
                else:
                    return 19
            else:
                if c[1][1] < c[0][1]:
                    if c[1][1] < c[3][1]:
                        return 12
                    else:
                        return 13
                else:
                    if c[1][1] < c[3][1]:
                        return 13
                    else:
                        return 14
        elif c[1][1] == c[3][1]:
            if c[1][1] < c[0][1]:
                if c[1][1] < c[2][1]:
                    return 6
                else:
                    return 7
            else:
                if c[1][1] < c[2][1]:
                    return 7
                else:
                    return 8
        elif c[2][1] == c[3][1]:
            if c[2][1] < c[0][1]:
                if c[2][1] < c[1][1]:
                    return 9
                else:
                    return 10
            else:
                if c[2][1] < c[1][1]:
                    return 10
                else:
                    return 11
        else:
            if c[0][1] < c[1][1]:
                if c[0][1] < c[2][1]:
                    if c[1][1] < c[2][1]:
                        if c[2][1] < c[3][1]:
                            return 3
                        elif c[1][1] < c[3][1]:
                            return 2
                        elif c[0][1] < c[3][1]:
                            return 5
                        else:
                            return 4
                    else:
                        if c[1][1] < c[3][1]:
                            return 0
                        elif c[2][1] < c[3][1]:
                            return 1
                        elif c[0][1] < c[3][1]:
                            return 4
                        else:
                            return 5
                else:
                    if c[1][1] < c[3][1]:
                        return 1
                    elif c[0][1] < c[3][1]:
                        return 0
                    elif c[2][1] < c[3][1]:
                        return 3
                    else:
                        return 2
            else:
                if c[0][1] < c[2][1]:
                    if c[2][1] < c[3][1]:
                        return 2
                    elif c[0][1] < c[3][1]:
                        return 3
                    elif c[1][1] < c[3][1]:
                        return 0
                    else:
                        return 1
                else:
                    if c[1][1] < c[2][1]:
                        if c[0][1] < c[3][1]:
                            return 5
                        elif c[2][1] < c[3][1]:
                            return 4
                        elif c[1][1] < c[3][1]:
                            return 1
                        else:
                            return 0
                    else:
                        if c[0][1] < c[3][1]:
                            return 4
                        elif c[1][1] < c[3][1]:
                            return 5
                        elif c[2][1] < c[3][1]:
                            return 2
                        else:
                            return 3
    return -1


def check_any_equal(b):
    if b[0][1] == b[1][1] or b[0][1] == b[2][1] or b[0][1] == b[3][1] or b[1][1] == b[2][1] or b[1][1] == b[3][1] or b[2][1] == b[3][1]:
        return True
    return False


def custom_bisect(edge_list, time):
    lo = 0
    hi = len(edge_list)
    while lo < hi:
        mid = (lo + hi) // 2
        if edge_list[mid][1] < time:
            lo = mid + 1
        else:
            hi = mid
    return lo


#
# Classifies all butterflies in a given graph without generating a complete list of butterflies, for space efficiency.
#
# Returns: The count for each of the six types of formation order.
#          The seventh entry is the butterflies which were discarded based on delta_w or delta_c.
#
def classify_without_listing(filepath, num_left_nodes, delta_w=0, delta_c=0):
    g = load_graph(filepath)
    class_counts = [0, 0, 0, 0, 0, 0, 0]

    for i in range(num_left_nodes):
        paths = defaultdict(list)
        for e1 in g.get_all_edges(i, [g.ep.timestamps]):
            for e2 in g.get_all_edges(e1[1], [g.ep.timestamps]):
                if i < e2[1]:
                    paths[e2[1]].append([e1, numpy.array([e2[1], e2[0], e2[2]])])

        for path_list in paths.values():
            for j, path1 in enumerate(path_list):
                for path2 in path_list[j:]:
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
def classify_without_listing_sorted(filepath, num_left_nodes, delta_w=0, delta_c=0, reverse=False, old=False):
    if delta_c < 1:
        return "dc too low!"

    with open(filepath, 'rb') as fd:
        edges = pickle.load(fd)

    # class_counts = [0]*22
    class_counts = [0]*7

    for i in range(num_left_nodes):
        paths = defaultdict(list)
        for e1 in edges[i]:
            j = custom_bisect(edges[e1[0]], e1[1] - 3*delta_c)
            while j < len(edges[e1[0]]) and abs(edges[e1[0]][j][1] - e1[1]) <= 3*delta_c:
                if i < edges[e1[0]][j][0]:
                    paths[edges[e1[0]][j][0]].append([e1, edges[e1[0]][j]])
                j += 1

        for path_list in paths.values():
            for k, path1 in enumerate(path_list):
                for path2 in path_list[k:]:
                    if path1[0][0] != path2[0][0]:
                        class_counts[classify_butterfly4(path1 + path2, delta_c)] += 1

    if reverse:
        # return [class_counts[3], class_counts[2], class_counts[1], class_counts[0], class_counts[5], class_counts[4], class_counts[9], class_counts[10], class_counts[11], class_counts[6], class_counts[7], class_counts[8], class_counts[12], class_counts[13], class_counts[14], class_counts[16], class_counts[15], class_counts[17], class_counts[18], class_counts[19], class_counts[20]]
        return [class_counts[3], class_counts[2], class_counts[1], class_counts[0], class_counts[5], class_counts[4]]
    else:
        return class_counts[:-1]


def classify_without_listing_sorted_mod(filepath, num_left_nodes, delta_c, reverse=False, ref_given=False):
    if delta_c < 1:
        return "dc too low!"

    if ref_given:
        edges = filepath
    else:
        with open(filepath, 'rb') as fd:
            edges = pickle.load(fd)

    class_counts = [0]*7

    for i in range(num_left_nodes):
        paths = defaultdict(list)
        for e1 in edges[i]:
            j = custom_bisect(edges[e1[0]], e1[1] - 3*delta_c)
            while j < len(edges[e1[0]]) and abs(edges[e1[0]][j][1] - e1[1]) <= 3*delta_c:
                if i < edges[e1[0]][j][0]:
                    paths[edges[e1[0]][j][0]].append([e1, edges[e1[0]][j]])
                j += 1

        for path_list in paths.values():
            path_list.sort(key=lambda echo: echo[0][1])
            for k, path1 in enumerate(path_list):
                j = k + 1
                while j < len(path_list) and path_list[j][0][1] - path1[0][1] <= 3*delta_c:
                    if path1[0][0] != path_list[j][0][0]:
                        class_counts[classify_butterfly4(path1 + path_list[j], delta_c)] += 1
                    j += 1

    if reverse:
        return [class_counts[3], class_counts[2], class_counts[1], class_counts[0], class_counts[5], class_counts[4]]
    else:
        return class_counts[:6]


def classify_list_by_type(filepath, num_left_nodes, delta_c, reverse=False, ref_given=False):
    if delta_c < 1:
        return "dc too low!"

    if ref_given:
        edges = filepath
    else:
        with open(filepath, 'rb') as fd:
            edges = pickle.load(fd)

    butterflies = [[] for x in range(6)]

    for i in range(num_left_nodes):
        paths = defaultdict(list)
        for e1 in edges[i]:
            j = custom_bisect(edges[e1[0]], e1[1] - 3*delta_c)
            while j < len(edges[e1[0]]) and abs(edges[e1[0]][j][1] - e1[1]) <= 3*delta_c:
                if i < edges[e1[0]][j][0]:
                    paths[edges[e1[0]][j][0]].append([e1, edges[e1[0]][j]])
                j += 1

        for path_list in paths.values():
            path_list.sort(key=lambda echo: echo[0][1])
            for k, path1 in enumerate(path_list):
                j = k + 1
                while j < len(path_list) and path_list[j][0][1] - path1[0][1] <= 3*delta_c:
                    if path1[0][0] != path_list[j][0][0]:
                        x = classify_butterfly4(path1 + path_list[j], delta_c)
                        if x >= 0:
                            butterflies[x].append((i, path1+path_list[j]))
                    j += 1

    if reverse:
        return butterflies
    else:
        return butterflies


def classify_all_equality_types(filepath, num_left_nodes, delta_c, reverse=False, ref_given=False):
    if delta_c < 1:
        return "dc too low!"

    if ref_given:
        edges = filepath
    else:
        with open(filepath, 'rb') as fd:
            edges = pickle.load(fd)

    class_counts = [0]*22

    for i in range(num_left_nodes):
        paths = defaultdict(list)
        for e1 in edges[i]:
            j = custom_bisect(edges[e1[0]], e1[1] - 3*delta_c)
            while j < len(edges[e1[0]]) and abs(edges[e1[0]][j][1] - e1[1]) <= 3*delta_c:
                if i < edges[e1[0]][j][0]:
                    paths[edges[e1[0]][j][0]].append([e1, edges[e1[0]][j]])
                j += 1

        for path_list in paths.values():
            path_list.sort(key=lambda echo: echo[0][1])
            for k, path1 in enumerate(path_list):
                j = k + 1
                while j < len(path_list) and path_list[j][0][1] - path1[0][1] <= 3*delta_c:
                    if path1[0][0] != path_list[j][0][0]:
                        class_counts[classify_butterfly6(path1 + path_list[j], delta_c)] += 1
                    j += 1

    if reverse:
        return [class_counts[3], class_counts[2], class_counts[1], class_counts[0], class_counts[5], class_counts[4], class_counts[9], class_counts[10], class_counts[11], class_counts[6], class_counts[7], class_counts[8], class_counts[12], class_counts[13], class_counts[14], class_counts[16], class_counts[15], class_counts[17], class_counts[18], class_counts[19], class_counts[20]]
    else:
        return class_counts[:-1]


def classify_all_4event(filepath, delta_c, delta_w):
    with open(filepath, 'rb') as fd:
        edges = pickle.load(fd)

    counts = [0]*12
    for i, edge in enumerate(edges):
        j = i + 1
        while j < len(edges) and edges[j][2] - edges[i][2] <= delta_w:
            p1 = shared_node(edges[i], edges[j])
            if p1 >= 0:
                k = j + 1
                while k < len(edges) and (edges[k][2] - edges[j][2] <= delta_c or edges[k][2] - edges[i][2] <= delta_w):
                    p2 = shared_node(edges[i], edges[k])
                    p3 = shared_node(edges[j], edges[k])
                    if p2 >= 0 or p3 >= 0:
                        m = k + 1
                        while m < len(edges) and (edges[m][2] - edges[k][2] <= delta_c or edges[m][2] - edges[i][2] <= delta_w):
                            p4 = shared_node(edges[i], edges[m])
                            p5 = shared_node(edges[j], edges[m])
                            p6 = shared_node(edges[k], edges[m])
                            if p4 >= 0 or p5 >= 0 or p6 >= 0:
                                counts[classify_4event_shape((p1, p2, p3, p4, p5, p6))] += 1
                            m += 1
                    k += 1
            j += 1

    return counts


def classify_all_4event_t_reversed(filepath, delta_c, delta_w):
    with open(filepath, 'rb') as fd:
        edges2 = pickle.load(fd)
    edges = []
    for i in range(len(edges2)):
        edges.append((edges2[len(edges2)-i-1][0], edges2[len(edges2)-i-1][1], edges2[i][2]))

    counts = [0]*12
    for i, edge in enumerate(edges):
        j = i + 1
        while j < len(edges) and edges[j][2] - edges[i][2] <= delta_w:
            p1 = shared_node(edges[i], edges[j])
            if p1 >= 0:
                k = j + 1
                while k < len(edges) and (edges[k][2] - edges[j][2] <= delta_c or edges[k][2] - edges[i][2] <= delta_w):
                    p2 = shared_node(edges[i], edges[k])
                    p3 = shared_node(edges[j], edges[k])
                    if p2 >= 0 or p3 >= 0:
                        m = k + 1
                        while m < len(edges) and (edges[m][2] - edges[k][2] <= delta_c or edges[m][2] - edges[i][2] <= delta_w):
                            p4 = shared_node(edges[i], edges[m])
                            p5 = shared_node(edges[j], edges[m])
                            p6 = shared_node(edges[k], edges[m])
                            if p4 >= 0 or p5 >= 0 or p6 >= 0:
                                counts[classify_4event_shape((p1, p2, p3, p4, p5, p6))] += 1
                            m += 1
                    k += 1
            j += 1

    return counts


def shared_node(e1, e2):
    if e1[0] == e2[0]:
        if e1[1] == e2[1]:
            return 2
        return 0
    if e1[1] == e2[1]:
        return 1
    return -1


def classify_4event_shape(p_list):
    same_2_ct = p_list.count(2)
    left_ct = p_list.count(0)
    right_ct = p_list.count(1)
    same_1_ct = left_ct + right_ct

    if same_2_ct == 6:
        return 0
    if same_2_ct == 3:
        return 1
    if same_2_ct == 2:
        return 2
    if same_2_ct == 1:
        if same_1_ct == 5:
            return 3
        if same_1_ct == 4:
            return 4
        if same_1_ct == 3:
            return 5
    if same_2_ct == 0:
        if same_1_ct == 6:
            return 6
        if same_1_ct == 5:
            return 7
        if same_1_ct == 4:
            if (left_ct == 1 or right_ct == 1) and (left_ct == 3 or right_ct == 3):
                return 8
            if left_ct == 2 and right_ct == 2:
                return 9
        if same_1_ct == 3:
            return 10
    return -1


def classify_nodes(filepath, num_nodes, num_left_nodes, left=True, delta_c=0, reverse=False):
    with open(filepath, 'rb') as fd:
        edges = pickle.load(fd)

    type1_counts = defaultdict(int)
    type2_counts = defaultdict(int)
    type3_counts = defaultdict(int)
    type4_counts = defaultdict(int)
    type5_counts = defaultdict(int)
    type6_counts = defaultdict(int)

    if left:
        for i in range(num_left_nodes):
            x = per_node_classify(edges, i, delta_c, reverse=reverse)
            type1_counts[x[0]] += 1
            type2_counts[x[1]] += 1
            type3_counts[x[2]] += 1
            type4_counts[x[3]] += 1
            type5_counts[x[4]] += 1
            type6_counts[x[5]] += 1
    else:
        for i in range(num_left_nodes, num_nodes):
            x = per_node_classify(edges, i, delta_c, reverse=reverse)
            type1_counts[x[0]] += 1
            type2_counts[x[1]] += 1
            type3_counts[x[2]] += 1
            type4_counts[x[3]] += 1
            type5_counts[x[4]] += 1
            type6_counts[x[5]] += 1

    return type1_counts, type2_counts, type3_counts, type4_counts, type5_counts, type6_counts


def per_node_classify(edges, node_id, delta_c, reverse=False):
    counts = [0, 0, 0, 0, 0, 0, 0]
    if delta_c == 0:
        return counts
    paths = defaultdict(list)

    for e1 in edges[node_id]:
        j = custom_bisect(edges[e1[0]], e1[1] - delta_c)
        while j < len(edges[e1[0]]) and abs(edges[e1[0]][j][1] - e1[1]) <= delta_c:
            if node_id != edges[e1[0]][j][0]:
                paths[edges[e1[0]][j][0]].append([e1, edges[e1[0]][j]])
            j += 1

    for path_list in paths.values():
        for k, path1 in enumerate(path_list):
            for path2 in path_list[k:]:
                if path1[0][0] != path2[0][0]:
                    counts[classify_butterfly4(path1 + path2, delta_c=delta_c)] += 1

    if reverse:
        return [counts[3], counts[2], counts[1], counts[0], counts[5], counts[4]]
    else:
        return counts


def classify_time_windowed(filepath, timestep, delta_c, reverse=False):
    with open(filepath, 'rb') as fd:
        edges = pickle.load(fd)

    counts = [0]*7
    c = ceil(3 * delta_c / timestep)
    paths_holder = defaultdict(list)
    times_visited = defaultdict(list)

    for time, section in edges.items():
        for node, edge_list in section[0].items():
            times_visited[node].append(time)
            new_paths = defaultdict(list)
            for e1 in edge_list:
                for i in range(-c, c+1):
                    if time+i in edges and e1[0] in edges[time+i][1]:
                        for e2 in edges[time+i][1][e1[0]]:
                            if e2[0] > node:
                                new_paths[e2[0]].append([e1, e2])

            # update previous path dictionaries so only last c are stored
            while time - times_visited[node][0] > c:
                paths_holder[node].pop(0)
                times_visited[node].pop(0)

            for k, wedge_list in new_paths.items():
                for path_dict in paths_holder[node]:
                    if k in path_dict:
                        for wedge1 in wedge_list:
                            for wedge2 in path_dict[k]:
                                if wedge1[0][0] != wedge2[0][0]:
                                    # x = classify_butterfly4(wedge1+wedge2, delta_c)
                                    # counts[x] += 1
                                    # if x == 4:
                                    #     print(node, wedge1+wedge2)
                                    counts[classify_butterfly4(wedge1 + wedge2, delta_c)] += 1
                for i, wedge1 in enumerate(wedge_list):
                    for wedge2 in wedge_list[i:]:
                        if wedge1[0][0] != wedge2[0][0]:
                            counts[classify_butterfly4(wedge1 + wedge2, delta_c)] += 1

            paths_holder[node].append(new_paths)

    if reverse:
        return [counts[3], counts[2], counts[1], counts[0], counts[5], counts[4]]
    else:
        return counts[:-1]


def compute_interarrival_times(filepath, delimiter='\t'):
    edges = []
    with open(filepath) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        for row in rd:
            if row[0].isnumeric():
                edges.append(float(row[3]))
    edges.sort()
    print(f"min: {edges[0]}")
    print(f"max: {edges[-1]}")
    print(f"max-min = {edges[-1] - edges[0]}")

    distances = defaultdict(int)
    for i in range(1, len(edges)):
        distances[edges[i] - edges[i-1]] += 1

    return distances, len(edges)


def compute_median_interarrival_time(filepath, delimiter='\t'):
    d, num_events = compute_interarrival_times(filepath, delimiter)
    total = 0
    ind = 0
    while total < num_events / 2:
        total += d[ind]
        print(ind, d[ind], total)
        ind += 1


def analyze_per_node_butterflies(filepath, num_left_nodes, delta_c):
    with open(filepath, 'rb') as fd:
        edges = pickle.load(fd)

    compiled = []
    for node in range(num_left_nodes):
        others = [0]*num_left_nodes

        paths = defaultdict(list)
        for e1 in edges[node]:
            j = custom_bisect(edges[e1[0]], e1[1] - 3*delta_c)
            while j < len(edges[e1[0]]) and abs(edges[e1[0]][j][1] - e1[1]) <= 3*delta_c:
                if node != edges[e1[0]][j][0]:
                    paths[edges[e1[0]][j][0]].append([e1, edges[e1[0]][j]])
                j += 1

        for ap, path_list in paths.items():
            path_list.sort(key=lambda echo: echo[0][1])
            for k, path1 in enumerate(path_list):
                j = k + 1
                while j < len(path_list) and path_list[j][0][1] - path1[0][1] <= 3*delta_c:
                    if path1[0][0] != path_list[j][0][0]:
                        if classify_butterfly6(path1 + path_list[j], delta_c) >= 0:
                            others[ap] += 1
                    j += 1
        compiled.append(others)
    # keys = []
    # with open('../Data/covid-tweets/keywords.csv') as f:
    #     red = csv.reader(f)
    #     for row in red:
    #         keys.append(row[1])
    keys = ['PAY-CHECK', 'MOVE-FUNDS', 'QUICK-PAYMENT', 'DEPOSIT-CASH', 'MAKE-PAYMENT', 'WITHDRAWAL', 'EXCHANGE', 'DEPOSIT-CHECK']
    to_remove = []
    for i, row in enumerate(compiled):
        if sum(row) == 0:
            to_remove.append(i)
    for i in range(len(compiled)-1, -1, -1):
        if i in to_remove:
            del compiled[i]
            del keys[i]
        else:
            for j in reversed(to_remove):
                del compiled[i][j]
    for i, rd in enumerate(compiled):
        print(keys[i], rd)


def list_butterfly_ordering(bt):
    out = [0]*4
    bts = sorted([t[1] for t in bt])
    for i in range(4):
        out[i] = bts.index(bt[i][1])
    return out


def subtypes(order, ix1, ix2):
    if order[ix1] == 0:
        return 2**(order[ix2] - 1) - 1
    elif order[ix2] == 0:
        return 2**(order[ix1] - 1) - 1
    return 2**(order[ix1] - 1) + 2**(order[ix2] - 1) - 1


def analyze_good_versus_bad(filepath, num_left_nodes, delta_c, idx_of_gb):
    butterflies = classify_list_by_type(filepath, num_left_nodes, delta_c)
    for b_list in butterflies:
        gb_counts = [0]*28
        for b in b_list:
            ct = sum([bt[idx_of_gb] for bt in b[1]])
            if ct == 0:
                gb_counts[0] += 1
            elif ct == 1:
                x = [bt[idx_of_gb] for bt in b[1]].index(1)
                y = list_butterfly_ordering(b[1])
                gb_counts[y[x] + 1] += 1
            elif ct == 2:
                y = list_butterfly_ordering(b[1])
                if b[1][0][idx_of_gb] == 1 and b[1][2][idx_of_gb] == 1:
                    gb_counts[subtypes(y, 0, 2) + 5] += 1
                elif b[1][1][idx_of_gb] == 1 and b[1][3][idx_of_gb] == 1:
                    gb_counts[subtypes(y, 1, 3) + 5] += 1
                elif b[1][0][idx_of_gb] == 1 and b[1][1][idx_of_gb] == 1:
                    gb_counts[subtypes(y, 0, 1) + 11] += 1
                elif b[1][2][idx_of_gb] == 1 and b[1][3][idx_of_gb] == 1:
                    gb_counts[subtypes(y, 2, 3) + 11] += 1
                elif b[1][0][idx_of_gb] == 1 and b[1][3][idx_of_gb] == 1:
                    gb_counts[subtypes(y, 0, 3) + 17] += 1
                else:
                    gb_counts[subtypes(y, 1, 2) + 17] += 1
            elif ct == 3:
                x = [bt[idx_of_gb] for bt in b[1]].index(0)
                y = list_butterfly_ordering(b[1])
                gb_counts[y[x] + 23] += 1
            else:
                gb_counts[27] += 1
        print(sum(gb_counts), sum(gb_counts[1:5]), sum(gb_counts[5:23]), sum(gb_counts[23:27]), gb_counts)
