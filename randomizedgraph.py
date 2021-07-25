import pickle
import random
import sys
from numpy.random import permutation


def timestamp_shuffle(filepath, num_left_nodes):
    with open(filepath + "-pickled.bin", 'rb') as fd:
        edges = pickle.load(fd)

    simple_list = []
    for n, edge_list in enumerate(edges[:num_left_nodes]):
        for e in edge_list:
            simple_list.append((n, e[0], e[1]))

    new_edges = [[] for x in range(len(edges))]
    order = permutation(len(simple_list))
    i = 0
    while i < len(simple_list):
        new_edges[simple_list[i][0]].append((simple_list[i][1], simple_list[order[i]][2]))
        new_edges[simple_list[i][1]].append((simple_list[i][0], simple_list[order[i]][2]))
        i += 1

    for edge_list in new_edges:
        edge_list.sort(key=lambda echo: echo[1])

    with open(filepath + "-tshuffled.bin", 'wb') as pickle_file:
        pickle.dump(new_edges, pickle_file)


def link_shuffle(filepath, num_left_nodes):
    with open(filepath + "-pickled.bin", 'rb') as fd:
        edges = pickle.load(fd)

    new_edges = [[] for x in range(len(edges))]

    for edge_list in edges[:num_left_nodes]:
        for ed in edge_list:
            new_l = random.randint(0, num_left_nodes-1)
            new_r = random.randint(num_left_nodes, len(edges)-1)
            new_edges[new_l].append((new_r, ed[1]))
            new_edges[new_r].append((new_l, ed[1]))

    with open(filepath + "-linkshuffled.bin", 'wb') as pickle_file:
        pickle.dump(new_edges, pickle_file)


def link_shuffle_preserve_left_nodes(filepath, num_left_nodes):
    with open(filepath + "-pickled.bin", 'rb') as fd:
        edges = pickle.load(fd)

    new_edges = [[] for x in range(len(edges))]

    for node, edge_list in enumerate(edges[:num_left_nodes]):
        for ed in edge_list:
            new_r = random.randint(num_left_nodes, len(edges)-1)
            new_edges[node].append((new_r, ed[1]))
            new_edges[new_r].append((node, ed[1]))

    with open(filepath + "-leftlinkshuffled.bin", 'wb') as pickle_file:
        pickle.dump(new_edges, pickle_file)


def link_shuffle_degree_constrained(filepath, num_left_nodes, num_shuffles):
    with open(filepath + "-pickled.bin", 'rb') as fd:
        edges = pickle.load(fd)

    for i in range(num_shuffles):
        l1 = random.randint(0, num_left_nodes-1)
        l2 = random.randint(0, num_left_nodes-1)
        while not edges[l1]:
            l1 = random.randint(0, num_left_nodes - 1)
        while not edges[l2]:
            l2 = random.randint(0, num_left_nodes - 1)
        e1 = random.randint(0, len(edges[l1]) - 1)
        e2 = random.randint(0, len(edges[l2]) - 1)
        if l1 == l2 and e1 == e2:
            continue
        r1 = edges[l1][e1][0]
        r2 = edges[l2][e2][0]
        n1 = [x for x, y in enumerate(edges[r1]) if y[0] == l1 and y[1] == edges[l1][e1][1]][0]
        n2 = [x for x, y in enumerate(edges[r2]) if y[0] == l2 and y[1] == edges[l2][e2][1]][0]
        edges[r1].append((l2, edges[l2][e2][1]))
        edges[r2].append((l1, edges[l1][e1][1]))
        edges[r1].pop(n1)
        if r1 == r2 and n2 > n1:
            edges[r2].pop(n2-1)
        else:
            edges[r2].pop(n2)
        edges[l1].append((r2, edges[l1][e1][1]))
        edges[l2].append((r1, edges[l2][e2][1]))
        edges[l1].pop(e1)
        if l1 == l2 and e2 > e1:
            edges[l2].pop(e2-1)
        else:
            edges[l2].pop(e2)
        # print(l1, l2, e1, e2, r1, r2)

    for edge_list in edges:
        edge_list.sort(key=lambda echo: echo[1])

    with open(filepath + "-deg_constrain.bin", 'wb') as pickle_file:
        pickle.dump(edges, pickle_file)


def link_shuffle_degree_constrained_t_random(filepath, num_left_nodes, num_shuffles):
    with open(filepath + "-pickled.bin", 'rb') as fd:
        edges = pickle.load(fd)

    for i in range(num_shuffles):
        l1 = random.randint(0, num_left_nodes-1)
        l2 = random.randint(0, num_left_nodes-1)
        while not edges[l1]:
            l1 = random.randint(0, num_left_nodes - 1)
        while not edges[l2]:
            l2 = random.randint(0, num_left_nodes - 1)
        e1 = random.randint(0, len(edges[l1]) - 1)
        e2 = random.randint(0, len(edges[l2]) - 1)
        if l1 == l2 and e1 == e2:
            continue
        r1 = edges[l1][e1][0]
        r2 = edges[l2][e2][0]
        n1 = [x for x, y in enumerate(edges[r1]) if y[0] == l1 and y[1] == edges[l1][e1][1]][0]
        n2 = [x for x, y in enumerate(edges[r2]) if y[0] == l2 and y[1] == edges[l2][e2][1]][0]
        edges[r1].append((l2, edges[l2][e2][1]))
        edges[r2].append((l1, edges[l1][e1][1]))
        edges[r1].pop(n1)
        if r1 == r2 and n2 > n1:
            edges[r2].pop(n2-1)
        else:
            edges[r2].pop(n2)
        edges[l1].append((r2, edges[l1][e1][1]))
        edges[l2].append((r1, edges[l2][e2][1]))
        edges[l1].pop(e1)
        if l1 == l2 and e2 > e1:
            edges[l2].pop(e2-1)
        else:
            edges[l2].pop(e2)

    simple_list = []
    for n, edge_list in enumerate(edges[:num_left_nodes]):
        for e in edge_list:
            simple_list.append((n, e[0], e[1]))

    new_edges = [[] for x in range(len(edges))]
    order = permutation(len(simple_list))
    i = 0
    while i < len(simple_list):
        new_edges[simple_list[i][0]].append((simple_list[i][1], simple_list[order[i]][2]))
        new_edges[simple_list[i][1]].append((simple_list[i][0], simple_list[order[i]][2]))
        i += 1

    for edge_list in new_edges:
        edge_list.sort(key=lambda echo: echo[1])

    with open(filepath + "-deg_constrain_rt.bin", 'wb') as pickle_file:
        pickle.dump(new_edges, pickle_file)


def time_reverse(filepath, num_nodes):
    with open(filepath + "-edges_filtered.bin", 'rb') as fd:
        edges = pickle.load(fd)

    new_edges = [[] for x in range(num_nodes)]
    for i in range(len(edges)//2):
        new_edges[edges[i][0]].append((edges[i][1], edges[len(edges)-i-1][2]))
        new_edges[edges[i][1]].append((edges[i][0], edges[len(edges)-i-1][2]))
        new_edges[edges[len(edges)-i-1][0]].append((edges[len(edges)-i-1][1], edges[i][2]))
        new_edges[edges[len(edges)-i-1][1]].append((edges[len(edges)-i-1][0], edges[i][2]))

    if len(edges) % 2 == 1:
        i = len(edges)//2
        new_edges[edges[i][0]].append((edges[i][1], edges[i][2]))
        new_edges[edges[i][1]].append((edges[i][0], edges[i][2]))

    for edge_list in new_edges:
        edge_list.sort(key=lambda echo: echo[1])

    with open(filepath + "-timerev.bin", 'wb') as pickle_file:
        pickle.dump(new_edges, pickle_file)

# 2563
# 9208
# 17517
# 33720
# 70629
# 95580
# 411749
# 681366
# 1565683
# 3018197
# 19150868


# if __name__ == '__main__':
#     # link_shuffle("../edit-svwikiquote/out.edit-svwikiquote", 740)
#     # link_shuffle_preserve_left_nodes("../edit-svwikiquote/out.edit-svwikiquote", 740)
#     # file = "../edit-svwikiquote/out.edit-svwikiquote"
#     # n_left = 740
#     # n_events = 17517
#     # timestamp_shuffle(file, n_left)
#     # link_shuffle_degree_constrained(file, n_left, n_events)
#     # link_shuffle_degree_constrained_t_random(file, n_left, n_events)
#     # time_reverse(file, n_left)
#
#     # with open("../edit-rmwikibooks/out.edit-rmwikibooks-pickled.bin", 'rb') as fd:
#     #     edges = pickle.load(fd)
#     # for i, ed in enumerate(edges):
#     #     print(i, ed)
#     # print("\n------------------------------------------------------------------------------------------\n")
#     # with open("../edit-rmwikibooks/out.edit-rmwikibooks-tshuffled.bin", 'rb') as fd:
#     #     edges = pickle.load(fd)
#     # for i, ed in enumerate(edges):
#     #     print(i, ed)
