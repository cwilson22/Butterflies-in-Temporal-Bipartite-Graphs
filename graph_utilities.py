import csv
import math
import pickle
import re
from collections import defaultdict
import numpy
from graph_tool.all import *


datasets = {
    "hawiki": ["../edit-hawiktionary/out.edit-hawiktionary-pickled.bin", 1017, 187],
    "twwiki": ["../edit-twwiki/out.edit-twwiki-pickled.bin", 2493, 632],
    "svwiki": ["../edit-svwikiquote/out.edit-svwikiquote-pickled.bin", 4205, 740],
    "amazon": ["../wang-amazon/out.wang-amazon-pickled.bin", 26911, 26112],  # backwards, right=799
    "ucforum": ["../opsahl-ucforum/out.opsahl-ucforum-pickled.bin", 1421, 899],
    "escorts": ["../escorts/out.escorts-pickled.bin", 16730, 10106],  # backwards, right=6624
    "sdwiki": ["../edit-sdwiki/out.edit-sdwiki-pickled.bin", 25887, 951],
    "ciaodvd": ["../librec-ciaodvd-movie_ratings/out.librec-ciaodvd-movie_ratings-pickled.bin", 33736, 17615],
    "mlui": ["../movielens-10m_ui/out.movielens-10m_ui-pickled.bin", 11610, 4009],
    "mlti": ["../movielens-10m_ti/out.movielens-10m_ti-pickled.bin", 24129, 16528],
    "ml100k": ["../movielens-100k_rating/rel.rating-pickled.bin", 2625, 943],
    "tripadvisor": ["../wang-tripadvisor/out.wang-tripadvisor-pickled.bin", 147075, 145316],  # backwards, right=1759
    "mooc": ["../act-mooc/mooc_actions.tsv-pickled.bin", 7144, 7047],  # backwards, right=97
    "scnwiki": ["../edit-scnwiki/out.edit-scnwiki-pickled.bin", 59039, 2902],
    "lkml": ["../lkml_person-thread/out.lkml_person-thread_person-thread-pickled.bin", 379554, 42045],
    "diggs": ["../digg-votes/out.digg-votes-pickled.bin", 142962, 139409],  # backwards, right=3553
    "lastfm": ["../lastfm_band/out.lastfm_band-pickled.bin", 175069, 992]
}


def import_graph(path, num_nodes, num_left_nodes, delimiter='\t'):
    g = Graph(directed=False)
    g.add_vertex(num_nodes)
    temporal = g.new_edge_property("int")
    g.edge_properties["timestamps"] = temporal

    with open(path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        for row in rd:
            if row[0].isnumeric():
                new_edge = g.add_edge(g.vertex(int(row[0]) - 1), g.vertex(int(row[1]) + num_left_nodes - 1))
                g.ep.timestamps[new_edge] = int(row[3])

    g.save(path + ".xml.gz")


def import_graph_basic_with_sort(path, num_nodes, num_left_nodes, delimiter='\t'):
    edges = [[] for x in range(num_nodes)]

    with open(path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        for row in rd:
            if row[0].isnumeric():
                edges[int(row[0])].append((int(row[1]), int(float(row[2]))))
                edges[int(row[1])].append((int(row[0]), int(float(row[2]))))

    for edge_list in edges:
        edge_list.sort(key=lambda echo: echo[1])

    with open(path + "-pickled.bin", 'wb') as pickle_file:
        pickle.dump(edges, pickle_file)


def import_graph_basic_with_sort2(path, num_nodes, num_left_nodes, delimiter='\t'):
    edges = [[] for x in range(num_nodes)]

    with open(path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        for row in rd:
            if row[0].isnumeric():
                edges[int(row[1])-1].append((int(row[0])-1+num_left_nodes, float(row[3])))
                edges[int(row[0])-1+num_left_nodes].append((int(row[1])-1, float(row[3])))

    for edge_list in edges:
        edge_list.sort(key=lambda echo: echo[1])

    with open(path + "-pickled.bin", 'wb') as pickle_file:
        pickle.dump(edges, pickle_file)


def import_graph_temporal_adjacency(path, num_left_nodes, timestep, delimiter='\t'):
    edges = []
    with open(path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        for row in rd:
            if row[0].isnumeric():
                edges.append((int(row[0]), int(row[1]), int(float(row[3]))))
    edges.sort(key=lambda echo: echo[2])

    min_t = edges[0][2]
    win_temp = {0: [{}, {}]}

    t_iter = 0
    for edge in edges:
        while edge[2] - min_t >= (t_iter + 1) * timestep:
            t_iter += 1
            if edge[2] - min_t < (t_iter + 1) * timestep:
                win_temp[t_iter] = [{}, {}]
        if edge[0] not in win_temp[t_iter][0]:
            win_temp[t_iter][0][edge[0]] = []
        if edge[1]+num_left_nodes not in win_temp[t_iter][1]:
            win_temp[t_iter][1][edge[1]+num_left_nodes] = []
        win_temp[t_iter][0][edge[0]].append((edge[1]+num_left_nodes, edge[2]-min_t))
        win_temp[t_iter][1][edge[1]+num_left_nodes].append((edge[0], edge[2]-min_t))

    with open(path + "-win-temp-adj.bin", 'wb') as pickle_file:
        pickle.dump(win_temp, pickle_file)


def import_graph_filtered_edges(path, num_left_nodes):
    with open(path, 'rb') as fd:
        g = pickle.load(fd)

    list_of_edges = []
    for i, e_list in enumerate(g[:num_left_nodes]):
        for edge in e_list:
            list_of_edges.append((i, edge[0], edge[1]))

    list_of_edges.sort(key=lambda echo: echo[2])

    list_of_edges = [list_of_edges[i] for i in range(len(list_of_edges)) if list_of_edges[i-1][2] != list_of_edges[i][2]]

    with open(path.replace('pickled', 'edges_filtered'), 'wb') as pickle_file:
        pickle.dump(list_of_edges, pickle_file)


def import_edges_sorted(path, num_left_nodes):
    with open(path, 'rb') as fd:
        g = pickle.load(fd)

    list_of_edges = []
    for i, e_list in enumerate(g[:num_left_nodes]):
        for edge in e_list:
            list_of_edges.append((i, edge[0], edge[1]))

    list_of_edges.sort(key=lambda echo: echo[2])

    with open(path.replace('pickled', 'edges_sorted'), 'wb') as pickle_file:
        pickle.dump(list_of_edges, pickle_file)


def draw_graph(path, num_nodes, num_left_nodes):
    g = load_graph(path + ".xml.gz")
    n1 = g.new_vertex_property("bool")
    for i in range(num_left_nodes):
        v = g.vertex(i)
        n1[v] = True
    for i in range(num_left_nodes, num_nodes):
        v = g.vertex(i)
        n1[v] = False
    pos = sfdp_layout(g)
    graph_draw(g, pos=pos, vertex_fill_color=n1, vertex_text=g.vertex_index, output=path + "-sfdp.pdf")


def check_efficiency(filepath, num_left_nodes):
    with open(filepath, 'rb') as fd:
        g = pickle.load(fd)

    left_sum = 0
    right_sum = 0
    for elist in g[:num_left_nodes]:
        left_sum += len(elist)**2
    for elist in g[num_left_nodes:]:
        right_sum += len(elist)**2

    return left_sum < right_sum


def import_graph_basic_with_sort_jp(path, num_nodes, num_left_nodes, delimiter=','):
    edges = [[] for x in range(num_nodes)]

    with open(path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        for row in rd:
            if row is not None and row[0] != '':
                x = row[0]
                t = int(x[2:4])*86400*372+int(x[5:7])*86400*31+int(x[8:10])*86400+int(x[11:13])*3600+int(x[14:16])*60+int(x[17:19])
                edges[int(row[0])].append((int(row[1]), int(float(row[2]))))
                edges[int(row[1])].append((int(row[0]), int(float(row[2]))))

    for edge_list in edges:
        edge_list.sort(key=lambda echo: echo[1])

    with open(path + "-pickled.bin", 'wb') as pickle_file:
        pickle.dump(edges, pickle_file)


keywds = {'PAY-CHECK': 0, 'MOVE-FUNDS': 1, 'QUICK-PAYMENT': 2, 'DEPOSIT-CASH': 3, 'MAKE-PAYMENT': 4, 'WITHDRAWAL': 5, 'EXCHANGE': 6, 'DEPOSIT-CHECK': 7}


def sanitize_data():
    with open('../Data/jpmorgan2/JPMAIR_synthetic-data-Payment-Fraud-1000-100.csv') as fd:
        with open('../Data/jpmorgan2/trans_to_client.csv', 'w') as fw:
            rdr = csv.reader(fd)
            wtr = csv.writer(fw)
            id_ctr = 8
            found_ids = {}
            for row in rdr:
                if row != [] and row[0] != 'Time_step':
                    x = row[0]
                    t = int(x[2:4]) * 86400 * 372 + int(x[5:7]) * 86400 * 31 + int(x[8:10]) * 86400 + int(x[11:13]) * 3600 + int(x[14:16]) * 60 + int(x[17:19])
                    typ = keywds[row[12]]
                    good = row[11]
                    val = row[10]
                    sender = row[2]
                    bene = row[7]
                    sen = ''
                    ben = ''
                    if sender != '':
                        if sender not in found_ids:
                            found_ids[sender] = id_ctr
                            id_ctr += 1
                        sen = found_ids[sender]
                    if bene != '':
                        if bene not in found_ids:
                            found_ids[bene] = id_ctr
                            id_ctr += 1
                        ben = found_ids[bene]
                    wtr.writerow((typ, sen, ben, val, good, t))


# import_graph_basic_with_sort2("../lastfm_band/out.lastfm_band", 175069, 174077, delimiter=' ')
# import_graph_basic_with_sort("../lastfm_band/out.lastfm_band", datasets["lastfm"][1], datasets["lastfm"][2], delimiter=' ')

# print(check_efficiency(datasets["lastfm"][0], datasets["lastfm"][2]))

# for key, val in datasets.items():
#     print(key + ": " + str(check_efficiency(val[0], val[2])))

# import_graph_temporal_adjacency("../Data/edit-hawiktionary/out.edit-hawiktionary", 187, 120268)

# with open("../Data/edit-hawiktionary/out.edit-hawiktionary-win-temp-adj.bin", 'rb') as fd:
#     g = pickle.load(fd)
# for k, v in g.items():
#     print(k, v)

# import_edges_sorted("../Data/digg-votes/out.digg-votes-pickled.bin", 3553)

# import_graph_basic_with_sort("../Data/covid-tweets/covid-tweets.csv", 611348, 64, delimiter=' ')

# sanitize_data()
