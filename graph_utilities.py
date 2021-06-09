import csv
import pickle
from collections import defaultdict

import numpy
from graph_tool.all import *


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
                edges[int(row[0])-1].append((int(row[1])-1+num_left_nodes, int(row[3])))
                edges[int(row[1])-1+num_left_nodes].append((int(row[0])-1, int(row[3])))

    for edge_list in edges:
        edge_list.sort(key=lambda echo: echo[1])

    with open(path + "-pickled.bin", 'wb') as pickle_file:
        pickle.dump(edges, pickle_file)


def import_graph_numpy_with_sort(path, num_nodes, num_left_nodes, delimiter='\t'):
    edges = [[] for x in range(num_nodes)]

    with open(path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        for row in rd:
            if row[0].isnumeric():
                edges[int(row[0])-1].append((int(row[1])-1+num_left_nodes, int(row[3])))
                edges[int(row[1])-1+num_left_nodes].append((int(row[0])-1, int(row[3])))

    for i in range(num_nodes):
        edges[i].sort(key=lambda echo: echo[1])
        edges[i] = numpy.array(edges[i])

    result = numpy.array(edges, dtype=object)
    numpy.save(path + ".npy", result)


def import_graph_efficient(path, num_nodes, num_left_nodes, delimiter='\t'):
    adjacent = [set() for x in range(num_nodes)]


    with open(path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        for row in rd:
            if row[0].isnumeric():
                edges[int(row[0])-1].append((int(row[1])-1+num_left_nodes, int(row[3])))
                edges[int(row[1])-1+num_left_nodes].append((int(row[0])-1, int(row[3])))

    for i in range(num_nodes):
        edges[i].sort(key=lambda echo: echo[1])
        edges[i] = numpy.array(edges[i])

    result = numpy.array(edges, dtype=object)
    numpy.save(path + ".npy", result)


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


import_graph_numpy_with_sort("../edit-ngwiki/out.edit-ngwiki", 663, 221)
