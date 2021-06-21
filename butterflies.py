import csv
import random
import re
import pickle
import numpy
from graph_tool.all import *
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
                    d[str(e1[0]) + ":" + str(e2[0])] += 1
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


def classify_butterfly2(b, delta_w=0, delta_c=0):
    if abs(b[2][1] - b[0][1]) < delta_c and abs(b[3][1] - b[1][1]) <= delta_c:
        if delta_w == 0 or max(b[0][1], b[1][1], b[2][1], b[3][1]) - min(b[0][1], b[1][1], b[2][1], b[3][1]) <= delta_w:
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

    # if delta_c > delta_w:
    #     delta_w = delta_c
    # elif delta_c < delta_w / 3:
    #     delta_c = delta_w / 3
    class_counts = [0, 0, 0, 0, 0, 0, 0]

    for i in range(num_left_nodes):
        paths = defaultdict(list)
        for e1 in edges[i]:
            # j = bisect_left([a[1] for a in edges[e1[0]]], e1[1] - delta_c)
            j = custom_bisect(edges[e1[0]], e1[1] - delta_c)
            while j < len(edges[e1[0]]) and abs(edges[e1[0]][j][1] - e1[1]) <= delta_c:
                if i < edges[e1[0]][j][0]:
                    paths[edges[e1[0]][j][0]].append([e1, edges[e1[0]][j]])
                j += 1
            # for e2 in edges[e1[0]]:
            #     if i < e2[0] and abs(e2[1] - e1[1]) <= delta_c:
            #         paths[e2[0]].append([e1, e2])

        for path_list in paths.values():
            for k, path1 in enumerate(path_list):
                for path2 in path_list[k:]:
                    if path1[0][0] != path2[0][0]:
                        # x = classify_butterfly3(path1 + path2, delta_w, delta_c)
                        # if x >= 0:
                        #     butterflies.append(path1 + path2)
                        # class_counts[x] += 1
                        class_counts[classify_butterfly3(path1 + path2, delta_w=delta_w, delta_c=delta_c, old=old)] += 1

    if reverse:
        return [class_counts[3], class_counts[2], class_counts[1], class_counts[0], class_counts[5], class_counts[4]]
    else:
        return class_counts[:6]


def classify_nodes(filepath, num_nodes, num_left_nodes, left=True, delta_c=0):
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
            x = per_node_classify(edges, i, delta_c)
            type1_counts[x[0]] += 1
            type2_counts[x[1]] += 1
            type3_counts[x[2]] += 1
            type4_counts[x[3]] += 1
            type5_counts[x[4]] += 1
            type6_counts[x[5]] += 1
    else:
        for i in range(num_left_nodes, num_nodes):
            x = per_node_classify(edges, i, delta_c)
            type1_counts[x[0]] += 1
            type2_counts[x[1]] += 1
            type3_counts[x[2]] += 1
            type4_counts[x[3]] += 1
            type5_counts[x[4]] += 1
            type6_counts[x[5]] += 1

    return type1_counts, type2_counts, type3_counts, type4_counts, type5_counts, type6_counts


def per_node_classify(edges, node_id, delta_c):
    counts = [0, 0, 0, 0, 0, 0, 0]
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
                    counts[classify_butterfly3(path1 + path2, delta_c=delta_c)] += 1

    return counts


def classify_time_windowed(filepath, median, delta_c):
    with open(filepath, 'rb') as fd:
        edges = pickle.load(fd)

    counts = [0, 0, 0, 0, 0, 0, 0]
    c = delta_c // median

    for time, section in edges.items():
        for node, edge_list in section[0].items():
            paths = defaultdict(list)
            for e1 in edge_list:
                if c > 0:
                    for i in range(1-c, c):
                        for e2 in edges[time+i][1][e1[0]]:
                            if e2[0] > node:
                                paths[e2[0]].append([e1, e2])
                    for e2 in edges[time-c][1][e1[0]]:
                        if e2[0] > node and abs(e1[1] - e2[1]) <= delta_c:
                            j = custom_bisect(edges[e1[0]], e1[1] - delta_c)
                            while j < len(edges[e1[0]]) and abs(edges[e1[0]][j][1] - e1[1]) <= delta_c:
                                if node != edges[e1[0]][j][0]:
                                    paths[edges[e1[0]][j][0]].append([e1, edges[e1[0]][j]])
                                j += 1


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


# hawiki: 6995
# twwiki: 7177
# svwiki: 541
# amazon: 0
# ucforum: 67
# escorts: 0
# sdwiki: 109
# ciaodvd: 0
# mlui: 20
# mlti: 20
# ml100k: 0
# ml1m: 0  		# 541,754 / 1,000,209
# tripadvisor: 0
# diggs: 1 		# 1,267,588 / 3,018,197
# scnwiki: 140
# webuni: 0 		# 3,134,480 / 3,869,707
# twitter: 1 		# 2,108,362 / 4,664,605
# citeulike: 0 	# 1,569,397 / 2,411,819
# bibsonomyui: 0 	# 2,247,549 / 2,555,080
# kernel: 13  	# 569,861 / 1,565,683
# lastfm: 4 		# 1,652,859 / 19,150,868
# mooc: 2 		# 66,149/ 411,749

# median = 6995
# for cval in [median // 8, median // 4, median // 2, median, 2 * median, 4 * median, 8 * median]:
#     print(classify_without_listing_sorted("../edit-hawiktionary/out.edit-hawiktionary-pickled.bin", 187, delta_c=cval))

# print(enum_butterflies2("../wang-amazon/out.wang-amazon-pickled.bin", 799))

# compute_median_interarrival_time("../munmun_twitterex_ut/out.munmun_twitterex_ut", 4664605, delimiter=' ')

# print(classify_without_listing_sorted("../lastfm_band/out.lastfm_band-pickled.bin", 992, delta_c=16))

# datasets = {
#     "hawiki": ["../edit-hawiktionary/out.edit-hawiktionary-pickled.bin", 1017, 187],
#     "twwiki": ["../edit-twwiki/out.edit-twwiki-pickled.bin", 2493, 632],
#     "svwiki": ["../edit-svwikiquote/out.edit-svwikiquote-pickled.bin", 4205, 740],
#     "amazon": ["../wang-amazon/out.wang-amazon-pickled.bin", 26911, 26112],  # backwards, right=799
#     "ucforum": ["../opsahl-ucforum/out.opsahl-ucforum-pickled.bin", 1421, 899],
#     "escorts": ["../escorts/out.escorts-pickled.bin", 16730, 10106],  # backwards, right=6624
#     "sdwiki": ["../edit-sdwiki/out.edit-sdwiki-pickled.bin", 25887, 951],
#     "ciaodvd": ["../librec-ciaodvd-movie_ratings/out.librec-ciaodvd-movie_ratings-pickled.bin", 33736, 17615],
#     "mlui": ["../movielens-10m_ui/out.movielens-10m_ui-pickled.bin", 11610, 4009],
#     "mlti": ["../movielens-10m_ti/out.movielens-10m_ti-pickled.bin", 24129, 16528],
#     "ml100k": ["../movielens-100k_rating/rel.rating-pickled.bin", 2625, 943],
#     "tripadvisor": ["../wang-tripadvisor/out.wang-tripadvisor-pickled.bin", 147075, 145316],  # backwards, right=1759
#     "mooc": ["../act-mooc/mooc_actions.tsv-pickled.bin", 7144, 7047],  # backwards, right=97
#     "scnwiki": ["../edit-scnwiki/out.edit-scnwiki-pickled.bin", 59039, 2902],
#     "lkml": ["../lkml_person-thread/out.lkml_person-thread_person-thread-pickled.bin", 379554, 42045],
#     "diggs": ["../digg-votes/out.digg-votes-pickled.bin", 142962, 139409],  # backwards, right=3553
#     "lastfm": ["../lastfm_band/out.lastfm_band-pickled.bin", 175069, 992]
# }
#
# for k, v in datasets.items():
#     print(f"{k}: ")

# print(enum_butterflies2("../digg-votes/out.digg-votes-pickled.bin", 3553))

median = 109
line1s = [[], [], [], [], [], []]
line2s = [[], [], [], [], [], []]
for cval in [median // 8, median // 4, median // 2, median, 2 * median, 4 * median, 8 * median]:
    res = classify_nodes("../edit-sdwiki/out.edit-sdwiki-pickled.bin", 25887, 951, delta_c=cval)
    for j in range(6):
        line1 = ''
        line2 = ''
        for k, v in res[j].items():
            if k == 0:
                line1 += "0\t"
                line2 += "0\t"
            else:
                line1 += f"{k}\t"
                line2 += f"{v}\t"
        line1s[j].append(line1)
        line2s[j].append(line2)
for i in range(6):
    print()
    for j in range(7):
        print(line1s[i][j])
        print(line2s[i][j])
