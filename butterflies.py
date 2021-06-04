from graph_tool.all import *
from collections import defaultdict


def enum_butterflies(path, num_left_nodes):
    g = load_graph(path + ".xml.gz")
    # butterflies = []
    num_butterflies = 0
    for i in range(num_left_nodes):
        c = defaultdict(int)
        d = defaultdict(lambda: defaultdict(int))
        m = defaultdict(int)
        # paths = []
        for neighbor1 in g.get_all_neighbors(g.vertex(i)):
            m[neighbor1] += 1
            for neighbor2 in g.get_all_neighbors(g.vertex(neighbor1)):
                if neighbor2 != i:
                    c[neighbor2] += 1
                    if m[neighbor1] == 1:
                        d[neighbor2][neighbor1] += 1
                        # paths.append([i, neighbor2, neighbor1])
        for k, v in c.items():
            num_butterflies += v * (v-1) / 2
            for m_key, d_val in d[k].items():
                num_butterflies -= d_val * m[m_key] * (d_val * m[m_key] - 1) / 2
        print(i, num_butterflies, c, m, d)
        # for j, path1 in enumerate(paths):
        #     for path2 in paths[j+1:]:
        #         if path1[1] == path2[1]:
        #             butterflies.append(path1 + [path2[2]])
        # print(i, c, butterflies)
    return num_butterflies / 2


def list_butterflies(path, num_left_nodes):
    g = load_graph(path + ".xml.gz")
    butterflies = []
    # num_butterflies = 0
    for i in range(num_left_nodes):
        c = defaultdict(int)
        d = defaultdict(lambda: defaultdict(int))
        m = defaultdict(int)
        paths = []
        for neighbor1 in g.get_all_neighbors(g.vertex(i)):
            m[neighbor1] += 1
            for neighbor2 in g.get_all_neighbors(g.vertex(neighbor1)):
                if neighbor2 != i:
                    c[neighbor2] += 1
                    if m[neighbor1] == 1:
                        d[neighbor2][neighbor1] += 1
                    paths.append([i, neighbor2, neighbor1])
        # for k, v in c.items():
        #     num_butterflies += v * (v-1) / 2
        #     for m_key, d_val in d[k].items():
        #         num_butterflies -= d_val * m[m_key] * (d_val * m[m_key] - 1) / 2
        # print(i, num_butterflies, c, m, d)
        for j, path1 in enumerate(paths):
            for path2 in paths[j+1:]:
                if path1[1] == path2[1] and path1[2] != path2[2]:
                    butterflies.append(path1 + [path2[2]])
        print(i, c, butterflies)
    return butterflies


def list_butterflies(path, num_left_nodes):
    g = load_graph(path + ".xml.gz")
    butterflies = []
    # num_butterflies = 0
    for i in range(num_left_nodes):
        c = defaultdict(int)
        d = defaultdict(lambda: defaultdict(int))
        m = defaultdict(int)
        paths = []
        for e1 in g.get_all_edges(g.vertex(i)):
            m[neighbor1] += 1
            for e2 in g.get_all_edges(g.vertex(e1.target())):
                if e2.source() != i:
                    c[neighbor2] += 1
                    if m[neighbor1] == 1:
                        d[neighbor2][neighbor1] += 1
                    paths.append([i, neighbor2, neighbor1])
        for j, path1 in enumerate(paths):
            for path2 in paths[j+1:]:
                if path1[1] == path2[1] and path1[2] != path2[2]:
                    butterflies.append(path1 + [path2[2]])
        print(i, c, butterflies)
    return butterflies


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


print(list_butterflies("edit-rmwikibooks/out.edit-rmwikibooks", 21))
