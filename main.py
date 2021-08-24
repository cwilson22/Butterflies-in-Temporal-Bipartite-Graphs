import pickle
import time
import numpy
from butterflies import *
import randomizedgraph
import tempnet
import csv
import cProfile


# hawiki: 6995, 165950.30055
# twwiki: 7177, 46910.17823
# svwiki: 541, 23375.92104
# amazon: 0
# ucforum: 67, 421.48655
# escorts: 0
# sdwiki: 109, 6061.22575
# ciaodvd: 0
# mlui: 20
# mlti: 20, 1002.47338
# ml100k: 0
# ml1m: 0  		                # 541,754 / 1,000,209
# tripadvisor: 0
# diggs: 1, 1.00165 		    # 1,267,588 / 3,018,197
# scnwiki: 140, 592.32111
# webuni: 0 		            # 3,134,480 / 3,869,707
# twitter: 1 		            # 2,108,362 / 4,664,605
# citeulike: 0 	                # 1,569,397 / 2,411,819
# bibsonomyui: 0 	            # 2,247,549 / 2,555,080
# kernel: 13, 692.13965  	    # 569,861 / 1,565,683
# lastfm: 4, 14.21034  		    # 1,652,859 / 19,150,868
# mooc: 2, 6.24675 		        # 66,149/ 411,749


datasets = {
    "hawiki": ["../Data/edit-hawiktionary/out.edit-hawiktionary-pickled.bin", 1017, 187, 120268.44519, False, '\t'],
    "twwiki": ["../Data/edit-twwiki/out.edit-twwiki-pickled.bin", 2493, 632, 31286.05036, False, '\t'],
    "svwiki": ["../Data/edit-svwikiquote/out.edit-svwikiquote-pickled.bin", 4205, 740, 18646.95409, False, '\t'],
    # "amazon": ["../wang-amazon/out.wang-amazon-pickled.bin", 26911, 799],  # backwards, left=26112
    "ucforum": ["../Data/opsahl-ucforum/out.opsahl-ucforum-pickled.bin", 1421, 899, 302.50454, False, ' '],
    # "escorts": ["../escorts/out.escorts-pickled.bin", 16730, 6624],  # backwards, left=10106
    "sdwiki": ["../Data/edit-sdwiki/out.edit-sdwiki-pickled.bin", 25887, 951, 3322.47014, False, '\t'],
    # "ciaodvd": ["../librec-ciaodvd-movie_ratings/out.librec-ciaodvd-movie_ratings-pickled.bin", 33736, 17615],
    # "mlui": ["../movielens-10m_ui/out.movielens-10m_ui-pickled.bin", 11610, 4009],
    "mlti": ["../Data/movielens-10m_ti/out.movielens-10m_ti-pickled.bin", 24129, 16528, 677.61686, False, ' '],
    # "ml100k": ["../movielens-100k_rating/rel.rating-pickled.bin", 2625, 943],
    # "tripadvisor": ["../wang-tripadvisor/out.wang-tripadvisor-pickled.bin", 147075, 1759],  # backwards, left=145316
    "mooc": ["../Data/act-mooc/mooc_actions.tsv-pickled.bin", 7144, 97, 4.29754, True, '\t'],  # backwards, left=7047
    "scnwiki": ["../Data/edit-scnwiki/out.edit-scnwiki-pickled.bin", 59039, 2902, 335.82940, False, '\t'],
    "lkml": ["../Data/lkml_person-thread/out.lkml_person-thread_person-thread-pickled.bin", 379554, 42045, 159.85570, False, ' '],
    "diggs": ["../Data/digg-votes/out.digg-votes-pickled.bin", 142962, 3553, 0.86198, True],  # backwards, left=139409
    # "lastfm": ["../Data/lastfm_band/out.lastfm_band-pickled.bin", 175069, 992, 6.36454, False, ' ']
    # "covid": ["../Data/covid-tweets/covid-tweets.csv-pickled.bin", 611348, 76, 0.04243, False, ' ']
    "jpmorgan": ["../Data/jpmorgan/trans_to_client-pickled.bin", 3001, 8, 12958, False],
    "jpmorgan2": ["../Data/jpmorgan2/trans_to_sender-pickled.bin", 18411, 8, 759, False]
}


def calculate_mean(file, num_left_nodes):
    with open(file, 'rb') as fd:
        edges = pickle.load(fd)
    times = []
    for elis in edges[:num_left_nodes]:
        for ed in elis:
            times.append(ed[1])
    times.sort()
    inter = []
    i = 1
    while i < len(times):
        inter.append(times[i] - times[i-1])
        i += 1
    np_inp = numpy.array(inter)
    return numpy.mean(np_inp)


def unique_edges(file, num_left_nodes, num_events):
    with open(file, 'rb') as fd:
        edges = pickle.load(fd)

    d = set()
    ct = 0

    for i, elis in enumerate(edges[:num_left_nodes]):
        for ed in elis:
            if ed[0]*num_left_nodes + i in d:
                ct += 1
            else:
                d.add(ed[0]*num_left_nodes + i)

    return num_events - ct


def reject_outliers(data, m=2.5):
    return data[abs(data - numpy.mean(data)) < m * numpy.std(data)]


def adj_to_tij(file, num_left_nodes):
    with open(file, 'rb') as fd:
        edges = pickle.load(fd)

    new_tij = tempnet.classes.tij()

    for i, ed_list in enumerate(edges[:num_left_nodes]):
        for ed in ed_list:
            new_tij.add_event(ed[1], i, ed[0])

    return new_tij


def tij_to_sorted_list(tij_data):
    edges = []
    for edge in tij_data.display():
        edges.append((edge[1], edge[2], edge[0]))
    return edges


def get_filtered_edges_to_tij(file):
    with open(file, 'rb') as fd:
        edges = pickle.load(fd)

    new_tij = tempnet.classes.tij()
    for edge in edges:
        new_tij.add_event(edge[2], edge[0], edge[1])

    return new_tij


def adj_to_sorted_list(edges, num_left_nodes):
    new_edges = []
    for i, e_list in enumerate(edges[:num_left_nodes]):
        for ed in e_list:
            new_edges.append((i, ed[0], ed[1]))
    return new_edges.sort(key=lambda echo: echo[2])


def sorted_list_to_adj(edges, num_nodes):
    new_edges = [[] for i in range(num_nodes)]
    for ed in edges:
        new_edges[ed[0]].append((ed[1], ed[2]))
        new_edges[ed[1]].append((ed[0], ed[2]))
    for e_list in new_edges:
        e_list.sort(key=lambda echo: echo[1])
    return new_edges


def check_bipartite(adj_list):
    cur = [0]
    seen = [0]*len(adj_list)
    colors = [-1]*len(adj_list)
    seen[0] = 1
    colors[0] = 0
    while cur:
        nex = cur.pop(0)
        for ed in adj_list[nex]:
            if seen[ed[0]] == 0:
                cur.append(ed[0])
                seen[ed[0]] = 1
                colors[ed[0]] = (colors[nex] + 1) % 2
            elif colors[ed[0]] == colors[nex]:
                return False
    return True


def time_rev(sorted_list):
    i = 0
    new_edges = []
    while i < len(sorted_list):
        new_edges.append((sorted_list[i][0], sorted_list[i][1], sorted_list[len(sorted_list)-i-1][2]))
        i += 1
    new_edges.reverse()
    return new_edges


def shuffle_good_bad(num_left_nodes, num_nodes):
    with open('../Data/jpmorgan2/trans_to_sender-pickled.bin', 'rb') as f:
        edges = pickle.load(f)

    new_edges = [[] for i in range(num_nodes)]
    good_bad = []
    for edge_list in edges[:num_left_nodes]:
        for edge in edge_list:
            good_bad.append(edge[3])
    random.shuffle(good_bad)
    j = 0
    for n, edge_list in enumerate(edges[:num_left_nodes]):
        for edge in edge_list:
            new_edges[n].append((edge[0], edge[1], good_bad[j]))
            new_edges[edge[0]].append((n, edge[1], good_bad[j]))
            j += 1
    for e_list in new_edges:
        e_list.sort(key=lambda echo: echo[1])
    with open('../Data/jpmorgan2/sender_good_bad_shuffled.bin', 'wb') as f:
        pickle.dump(new_edges, f)


def run_classify_all_dc(name, ext, ref=False):
    median = datasets[name][3]
    for cval in [median / 8, median / 4, median / 2, median, 2 * median, 4 * median, 8 * median, 16 * median, 32 * median, 64 * median, 128 * median]:  # , 256*median, 512*median]:
        if ref:
            print(classify_without_listing_sorted_mod(ext, datasets[name][2],
                                                      round(cval), reverse=datasets[name][4], ref_given=True))
        else:
            print(classify_without_listing_sorted_mod(datasets[name][0].replace('pickled', ext), datasets[name][2], round(cval), reverse=datasets[name][4]))


if __name__ == '__main__':

    # dat = datasets["diggs"]
    # name = dat[0]
    # median = dat[3]
    # n_left = dat[2]
    # rev = dat[4]
    # t = time.time()
    # print(name)
    # for cval in [median / 8, median / 4, median / 2, median, 2 * median, 4 * median, 8 * median, 16 * median, 32 * median, 64 * median, 128 * median]:
    #     print(classify_without_listing_sorted_mod(name, n_left, delta_c=round(cval), reverse=rev))
    # print(time.time() - t)
    # print()
    # with open("../Data/edit-hawiktionary/out.edit-hawiktionary-pickled.bin", 'rb') as fd:
    #     edgs = pickle.load(fd)
    # for i, ed in enumerate(edgs):
    #     print(i, ed)

    # gra = get_filtered_edges_to_tij("../Data/edit-hawiktionary/out.edit-hawiktionary-edges_sorted.bin")
    # lks = tempnet.utils.tij_to_link_timeline(gra)
    # shuffled = tempnet.randomisations.my_P__k_pTheta(lks, 187, 1017)
    # back = tempnet.utils.link_timeline_to_sorted_edges(shuffled)
    # back_as_adj = sorted_list_to_adj(back, 1017)
    # with open("../Data/edit-hawiktionary/out.edit-hawiktionary-deg_constrain.bin", 'wb') as f:
    #     pickle.dump(back_as_adj, f)

    # print(classify_without_listing_sorted_mod("../Data/edit-hawiktionary/out.edit-hawiktionary-pickled.bin", 187, 120268))
    # print(classify_without_listing_sorted_mod("../Data/edit-hawiktionary/out.edit-hawiktionary-deg_constrain.bin", 187, 1202680000))

    # randomizedgraph.time_reverse("../Data/edit-hawiktionary/out.edit-hawiktionary", 1017)
    # print(classify_without_listing_sorted_mod("../Data/edit-hawiktionary/out.edit-hawiktionary-timerev.bin", 187, 120268))
    # with open("../Data/edit-hawiktionary/out.edit-hawiktionary-edges_filtered.bin", 'rb') as fil:
    #     filt = pickle.load(fil)
    # print(classify_without_listing_sorted_mod(sorted_list_to_adj(filt, 1017), 187, 120268, ref_given=True))



    # randomizedgraph.time_reverse("../Data/edit-rmwikibooks/out.edit-rmwikibooks", 70)
    # with open("../Data/edit-rmwikibooks/out.edit-rmwikibooks-edges_filtered.bin", 'rb') as fd:
    #     edges = pickle.load(fd)
    # for e in edges:
    #     print(e)
    # print("\n--------\n")
    # with open("../Data/edit-rmwikibooks/out.edit-rmwikibooks-timerev.bin", 'rb') as fd:
    #     edges = pickle.load(fd)
    # for i, e in enumerate(edges[:21]):
    #     print(i, e)

    # x = classify_all_4event("../Data/edit-hawiktionary/out.edit-hawiktionary-edges_filtered.bin", 69950, 69950)
    # x2 = classify_all_4event2("../Data/edit-hawiktionary/out.edit-hawiktionary-edges_filtered.bin", 69950, 69950)
    # print(classify_all_4event("../Data/edit-hawiktionary/out.edit-hawiktionary-edges_filtered.bin", 69950, 2*69950))
    # print(classify_all_4event2("../Data/edit-hawiktionary/out.edit-hawiktionary-edges_filtered.bin", 1, 2))
    # print(classify_all_4event2("../Data/edit-twwiki/out.edit-twwiki-edges_filtered.bin", 100, 200))
    # print(classify_all_4event2("../Data/edit-twwiki/out.edit-twwiki-edges_filtered.bin", 7177, 2*7177))

    # median = 120268.44519
    # for cval in [median / 8, median / 4, median / 2, median, 2 * median, 4 * median, 8 * median, 16 * median,
    #              32 * median, 64 * median, 128 * median]:
    #     print(classify_without_listing_sorted_mod("../Data/edit-hawiktionary/out.edit-hawiktionary-timerev.bin", 187, delta_c=round(cval), reverse=False))
    #     print(classify_without_listing_sorted_mod("../Data/edit-hawiktionary/out.edit-hawiktionary-pickled.bin", 187, delta_c=round(cval), reverse=False))

    # print(classify_all_4event("../Data/movielens-10m_ti/out.movielens-10m_ti-edges_filtered.bin", 100, 200))
    # print(classify_without_listing_sorted_mod("../Data/movielens-10m_ti/out.movielens-10m_ti-pickled.bin", 16528, 10))


    # print(classify_time_windowed("../Data/edit-hawiktionary/out.edit-hawiktionary-win-temp-adj.bin", 120268, 8*120268))
    # print(classify_without_listing_sorted_mod("../Data/edit-hawiktionary/out.edit-hawiktionary-pickled.bin", 187, 8*120268))

    # for nam, dat in datasets.items():
    #     print(nam)
    #     print('1..', end='')
    #     gra = get_filtered_edges_to_tij(dat[0].replace('pickled', 'edges_sorted'))
    #     print('2..', end='')
    #     lks = tempnet.utils.tij_to_link_timeline(gra)
    #     print('3')
    #     shuffled = tempnet.randomisations.my_P__k_pTheta(lks, dat[2], dat[1])
    #     print('4..', end='')
    #     back = tempnet.utils.link_timeline_to_sorted_edges(shuffled)
    #     print('5..', end='')
    #     back_as_adj = sorted_list_to_adj(back, dat[1])
    #     with open(dat[0].replace('pickled', 'deg_constrain'), 'wb') as f:
    #         pickle.dump(back_as_adj, f)
    #     print('6')
    #     run_classify_all_dc(nam, 'deg_constrain')
    #     print()

    # for nam, dat in datasets.items():
    #     print(nam)
    #     gra = get_filtered_edges_to_tij(dat[0].replace('pickled', 'edges_sorted'))
    #     # grout = gra.out()
    #     # ti = grout[0].time
    #     # tf = grout[-1].time
    #     print('A')
    #     lks = tempnet.utils.tij_to_link_timeline(gra)
    #     print('B')
    #     shuffled = tempnet.randomisations.P__w_pTheta(lks)
    #     print('C')
    #     back = tempnet.utils.link_timeline_to_sorted_edges(shuffled)
    #     print('D')
    #     adjs = sorted_list_to_adj(back, dat[1])
    #     print('E')
    #     run_classify_all_dc(nam, adjs, ref=True)
    #     print()


    # with open('../Data/edit-hawiktionary/out.edit-hawiktionary-pickled.bin', 'rb') as f:
    #     edges = pickle.load(f)
    # for i, elis in enumerate(edges):
    #     print(i, elis)
    #
    dat = datasets["jpmorgan2"]
    gra = get_filtered_edges_to_tij(dat[0].replace('pickled', 'edges_sorted'))
    lks = tempnet.utils.tij_to_link_timeline(gra)
    shuffled = tempnet.randomisations.P__pitau_pidtau_t1(lks)
    back = tempnet.utils.link_timeline_to_sorted_edges(shuffled)
    back_as_adj = sorted_list_to_adj(back, dat[1])
    run_classify_all_dc("jpmorgan2", back_as_adj, ref=True)
    #
    # for i, ed in enumerate(back_as_adj):
    #     print(i, ed)
    # print(check_bipartite(back_as_adj))

    # with open('../Data/covid-tweets/covid-tweets-2.csv') as f:
    #     rd = csv.reader(f, delimiter=' ')
    #     max_node = 0
    #     for row in rd:
    #         if row[1] != '' and int(row[1]) > max_node:
    #             max_node = int(row[1])
    # print(max_node)

    # mean = 12958
    # n_left = 8
    # for cval in [mean / 8, mean / 4, mean / 2, mean, 2 * mean, 4 * mean, 8 * mean, 16 * mean, 32 * mean, 64 * mean, 128 * mean]:
    #     print(classify_without_listing_sorted_mod('../Data/jpmorgan/good_bad_shuffled.bin', n_left, delta_c=round(cval)))

    # analyze_per_node_butterflies('../Data/jpmorgan2/trans_to_bene-pickled.bin', 8, 4*759)

    # print(calculate_mean('../Data/covid-tweets/covid-tweets-2.csv-pickled.bin', 76))

    # analyze_good_versus_bad('../Data/jpmorgan/trans_to_client-pickled.bin', 8, 48*12958, 2)

    # shuffle_good_bad(8, 18411)
