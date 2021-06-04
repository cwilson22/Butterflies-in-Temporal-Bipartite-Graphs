import csv
import pickle
from collections import defaultdict
from graph_tool.all import *


def import_graph(path, num_nodes, num_left_nodes):
    g = Graph(directed=False)
    g.add_vertex(num_nodes)
    temporal = g.new_edge_property("int")
    g.edge_properties["timestamps"] = temporal

    with open(path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            if row[0].isnumeric():
                new_edge = g.add_edge(g.vertex(int(row[0]) - 1), g.vertex(int(row[1]) + num_left_nodes - 1))
                g.ep.timestamps[new_edge] = int(row[3])

    g.save(path + ".xml.gz")


def import_graph_basic(path, num_nodes, num_left_nodes):
    V = (list(range(num_left_nodes)), list(range(num_left_nodes, num_nodes)))
    E = defaultdict(list)

    with open(path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            if row[0].isnumeric():
                E[int(row[0])-1].append((int(row[1]) - 1, int(row[3])))
                E[int(row[1])-1].append((int(row[0]) - 1, int(row[3])))

    with open(path + "-pickled.bin", 'wb') as pickle_file:
        pickle.dump((V, E), pickle_file)


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


# import_graph("edit-rmwikibooks/out.edit-rmwikibooks", 70, 21)
# draw_graph("edit-rmwikibooks/out.edit-rmwikibooks", 70, 21)

# import_graph_basic("edit-rmwikibooks/out.edit-rmwikibooks", 70, 21)
