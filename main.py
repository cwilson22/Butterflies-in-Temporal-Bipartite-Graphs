import time
import numpy
from butterflies import *
import randomizedgraph


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
    "hawiki": ["../Data/edit-hawiktionary/out.edit-hawiktionary-pickled.bin", 1017, 187, 120268.44519, False],
    "twwiki": ["../Data/edit-twwiki/out.edit-twwiki-pickled.bin", 2493, 632, 31286.05036, False],
    "svwiki": ["../Data/edit-svwikiquote/out.edit-svwikiquote-pickled.bin", 4205, 740, 18646.95409, False],
    # "amazon": ["../wang-amazon/out.wang-amazon-pickled.bin", 26911, 799],  # backwards, left=26112
    "ucforum": ["../Data/opsahl-ucforum/out.opsahl-ucforum-pickled.bin", 1421, 899, 302.50454, False],
    # "escorts": ["../escorts/out.escorts-pickled.bin", 16730, 6624],  # backwards, left=10106
    "sdwiki": ["../Data/edit-sdwiki/out.edit-sdwiki-pickled.bin", 25887, 951, 3322.47014, False],
    # "ciaodvd": ["../librec-ciaodvd-movie_ratings/out.librec-ciaodvd-movie_ratings-pickled.bin", 33736, 17615],
    # "mlui": ["../movielens-10m_ui/out.movielens-10m_ui-pickled.bin", 11610, 4009],
    "mlti": ["../movielens-10m_ti/out.movielens-10m_ti-pickled.bin", 24129, 16528, 677.61686, False],
    # "ml100k": ["../movielens-100k_rating/rel.rating-pickled.bin", 2625, 943],
    # "tripadvisor": ["../wang-tripadvisor/out.wang-tripadvisor-pickled.bin", 147075, 1759],  # backwards, left=145316
    "mooc": ["../act-mooc/mooc_actions.tsv-pickled.bin", 7144, 97, 4.29754, True],  # backwards, left=7047
    "scnwiki": ["../edit-scnwiki/out.edit-scnwiki-pickled.bin", 59039, 2902, 335.82940, False],
    "lkml": ["../lkml_person-thread/out.lkml_person-thread_person-thread-pickled.bin", 379554, 42045, 159.85570, False],
    "diggs": ["../digg-votes/out.digg-votes-pickled.bin", 142962, 3553, 0.86198, True],  # backwards, left=139409
    "lastfm": ["../lastfm_band/out.lastfm_band-pickled.bin", 175069, 992, 6.36454, False]
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


if __name__ == '__main__':

    # t = time.time()
    # median = datasets["scnwiki"][3]
    # for cval in [median / 8, median / 4, median / 2, median, 2 * median, 4 * median, 8 * median]:
    #     print(classify_without_listing_sorted_mod("../edit-scnwiki/out.edit-scnwiki-pickled.bin", 2902, delta_c=round(cval), reverse=False))
    # print(time.time() - t)
    # t = time.time()
    # for cval in [median / 8, median / 4, median / 2, median, 2 * median, 4 * median, 8 * median]:
    #     print(classify_without_listing_sorted("../edit-scnwiki/out.edit-scnwiki-pickled.bin", 2902, delta_c=round(cval), reverse=False))
    # print(time.time() - t)

    print(classify_time_windowed("../Data/edit-hawiktionary/out.edit-hawiktionary-win-temp-adj.bin", 120268, 120268))

