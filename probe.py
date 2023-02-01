'''
Filename: probe.py
Description: Inferring intra-domain links and inter-domain links
FunctionList:
1.def compute_class_prior(iplinks)  // Compute class prior probability: P(C)
2.def naive_bayes(iplinks, features)   // Inference using the Naive Bayesian algorithm
'''


import argparse
from traceparser import IpPath
from link import IPLinks
from feature import Features
import math
import numpy as np
import pickle
import sys


def save_dict(filename, dict):
    f = open(filename, 'ab')
    string = pickle.dumps(dict)
    f.write(string)
    f.close()


def compute_class_prior(iplinks):
    """Compute class prior probability: P(C)  """
    # The prior probability P(C) is used to assign links L is the probability of each type
    # P(C) is the proportion of each link type in the data
    intra_count, inter_count = 0, 0
    for link, rel in iplinks.rel1.items():
        if rel == 'intra':
            intra_count += 1
        else:
            inter_count += 1
    sum_class = intra_count + inter_count
    return list(map(lambda x: float(x)/sum_class, (intra_count, inter_count)))


def naive_bayes(iplinks, features):
    """Inference using the Naive Bayesian algorithm"""
    for iter in range(100):
        print('Number of iterations', iter)
        if isinstance(features, Features):
            features = features
        inferred_link = set()
        class_prior = compute_class_prior(iplinks)  # Calculating class prior probabilities
        print('class_prior', class_prior)
        log_class_prior = list(map(lambda x: math.log10(x), class_prior))  # Logarithmic values of class prior probabilities
        print('log_class_prior', log_class_prior)

        link_prob = {}
        for link in iplinks.prob:
            if link in inferred_link:
                continue
            log_prob = log_class_prior  # logMN = logM + logN
            # print('初始', log_prob)
            # log_prob + log P(f1|C) + log P(f2|C) + ... + log P(fn|C)

            # fan_in feature
            if link in iplinks.fan_in:
                log_prob = list(map(lambda x, y: x + y, log_prob, list(map(lambda x: math.log10(x),
                                                    features.fan_in_feature[iplinks.fan_in[link]]))))

            # fan_out feature
            if link in iplinks.fan_out:
                log_prob = list(map(lambda x, y: x + y, log_prob, list(map(lambda x: math.log10(x),
                                                    features.fan_out_feature[iplinks.fan_out[link]]))))

            # as_rel_prev feature
            if link in iplinks.as_rel_prev:
                log_prob = list(map(lambda x, y: x + y, log_prob, list(map(lambda x: math.log10(x),
                                                    features.as_rel_prev_feature[iplinks.as_rel_prev[link]]))))

            # as_rel_next feature
            if link in iplinks.as_rel_next:
                log_prob = list(map(lambda x, y: x + y, log_prob, list(map(lambda x: math.log10(x),
                                                    features.as_rel_next_feature[iplinks.as_rel_next[link]]))))

            # ip_distance feature
            if link in iplinks.ip_distance:
                log_prob = list(map(lambda x, y: x + y, log_prob, list(map(lambda x: math.log10(x),
                                                    features.ip_distance_feature[iplinks.ip_distance[link]]))))

            intra = math.exp(log_prob[0]) / (math.exp(log_prob[0]) + math.exp(log_prob[1]))
            inter = math.exp(log_prob[1]) / (math.exp(log_prob[0]) + math.exp(log_prob[1]))
            if inter / intra > 0.09:
                iplinks.rel2[link] = 'inter'
                link_prob[link] = ('inter', inter)
            else:
                iplinks.rel2[link] = 'intra'
                link_prob[link] = ('intra', intra)
            inferred_link.add(link)

        rel_change_count = 0
        for link in iplinks.rel1:
            if iplinks.rel2[link] != iplinks.rel1[link]:   # Link type changes compared to the initial type
                rel_change_count += 1
        print('rel_change_count', rel_change_count)

        intra2inter_count = 0
        inter2intra_count = 0
        for link in iplinks.rel1:
            if iplinks.rel1[link] == 'intra' and iplinks.rel2[link] == 'inter':
                intra2inter_count += 1
            if iplinks.rel1[link] == 'inter' and iplinks.rel2[link] == 'intra':
                inter2intra_count += 1
        print('intra2inter_count', intra2inter_count)
        print('inter2intra_count', inter2intra_count)

        for link in iplinks.rel1:
            iplinks.rel1[link] = iplinks.rel2[link]  # 更新

        if rel_change_count < 100:
            print('Number of iterations', iter)
            save_dict('link_prob.pkl', link_prob)
            break


if __name__ == '__main__':
    class_IPLinks = IPLinks()
    class_IPLinks.ip_links()
    # class_IPLinks.router_link = np.load('IPLinks/ip_link_router_link.npy', allow_pickle=True).item()
    # class_IPLinks.asn = np.load('IPLinks/ip_link_asn.npy', allow_pickle=True).item()
    # class_IPLinks.as_rel = np.load('IPLinks/ip_link_as_rel.npy', allow_pickle=True).item()
    # class_IPLinks.prev_link = np.load('IPLinks/ip_link_prev_link.npy', allow_pickle=True).item()
    # class_IPLinks.next_link = np.load('IPLinks/ip_link_next_link.npy', allow_pickle=True).item()

    class_IPLinks.init_prob()
    # class_IPLinks.prob = np.load('IPLinks/self.prob.npy', allow_pickle=True).item()
    # class_IPLinks.rel1 = np.load('IPLinks/self.rel1.npy', allow_pickle=True).item()

    print('Link attributes constructed...')
    class_IPLinks.construct_attributes()

    print('Feature likelihoods computed...')
    class_Features = Features(class_IPLinks)
    class_Features.compute_feature_likelihoods()

    print('naive_bayes...')
    naive_bayes(class_IPLinks, class_Features)


