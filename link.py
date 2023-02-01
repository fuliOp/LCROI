'''
Filename: link.py
Description: Process IP links and construct feature attributes.
FunctionList:
1.def ip2long(ip)  // Convert an IP string to long
class IPLinks(object):  // The class of IP links
    1.def ip_links(self)  // Handle IP links
    2.def init_prob(self)   // Determine relationship probabilities and relationships from IP2AS data initialization.
    3.def assign_fan_in(self)  // the fan in feature
    4.def assign_fan_out(self)  // the fan out feature
    5.def assign_as_rel_prev(self)  // the AS relationship feature
    6.def assign_as_rel_next(self)  // the AS relationship feature
    7.def assign_ip_distance(self)  // the IP vector distance feature
    8.def construct_attributes(self)  // Construct feature attributes
'''


from traceparser import IpPath
from collections import defaultdict
import numpy as np
import pickle
import socket
import struct
import random
# from aliasresolution import IPs


# Convert an IP string to long
def ip2long(ip):
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]


def save_dict(filename, dict):
    f = open(filename, 'ab')
    string = pickle.dumps(dict)
    f.write(string)
    f.close()


class IPLinks(object):
    def __init__(self):
        self.router_link = {}  # (ip1,ip2):(R1,R2)
        self.asn = {}  # (ip1,ip2):(AS1,AS2)
        self.as_rel = {}  # (ip1,ip2):AS1和AS2的关系
        self.prev_link = defaultdict(set)  # (ip1,ip2):[prev_ip_link]
        self.next_link = defaultdict(set)  # (ip1,ip2):[next_ip_link]

        self.prob = {}  # The key of the self.prob dictionary is a link pair, and the value is a tuple (the probability that the link is intra,inter)
        self.rel1 = {}  # Initial:intra/inter
        self.rel2 = {}  # After the iteration:intra/inter

        self.fan_in = {}  #
        self.fan_out = {}  #
        self.as_rel_prev = {}  #
        self.as_rel_next = {}  #
        self.ip_distance = {}  #

    def ip_links(self):
        ip_router_dict = np.load('aliasresolution/ip_router_dict.npy', allow_pickle=True).item()
        ip_ixp = np.load('ip2as/ip_ixp.npy', allow_pickle=True).item()  # IP addresses belonging to IXPs
        ip_rs = np.load('ip2as/ip_rs.npy', allow_pickle=True).item()  # IP addresses belonging to the RouteServers

        ip_as_dict = defaultdict(str)
        with open('ip2as/ip_as_dict.txt', 'r') as f:  # A dictionary: key is IP, value is ASN.
            ip_as_dict1 = eval(f.read())
        ip_as_dict.update(ip_as_dict1)

        as_rel_dict = defaultdict(str)
        as_rel_dict_load = np.load('as_rel/as_rel.npy', allow_pickle=True).item()
        as_rel_dict.update(as_rel_dict_load)

        ixp_link = set()
        route_server_link = set()

        count = 0

        with open('ip_paths.pkl', 'rb') as f1:
            while True:
                try:
                    ip_path = pickle.load(f1)
                    if len(ip_path.path) > 1:
                        count += 1
                        print('Number of IP paths processed', count)

                        if ip_path.path[-1] == ip_path.dst[-1]:
                            ip_path.path.remove(ip_path.path[-1])

                        # route_server_link
                        for ip in ip_path.path:
                            if ip_rs[ip]:
                                index = ip_path.path.index(ip)
                                if 0 < index < len(ip_path.path) - 1:
                                    route_server_link.add((ip_path.path[index - 1], ip_path.path[index + 1]))
                                ip_path.path.remove(ip)

                        # ixp_link
                        ip_link_list = []
                        if len(ip_path.path) > 1:
                            for i in range(len(ip_path.path) - 1):
                                ip1, ip2 = ip_path.path[i], ip_path.path[i+1]
                                ip_link_list.append((ip1, ip2))
                                if i+2 < len(ip_path.path) and ip_ixp[ip2] and ip_ixp[ip_path.path[i+2]]:
                                    ixp_link.add((ip2, ip_path.path[i+2]))
                                else:
                                    if ip_ixp[ip2]:
                                        ixp_link.add((ip1, ip2))

                        # prev next
                        if len(ip_path.path) > 1:
                            for i in range(1, len(ip_link_list)):
                                prev_link = ip_link_list[i - 1]
                                self.prev_link[ip_link_list[i]].add(prev_link)
                            for i in range(0, len(ip_link_list)-1):
                                # if ip_link_list[i] not in self.next_link:
                                #     self.next_link[ip_link_list[i]] = set()
                                next_link = ip_link_list[i + 1]
                                self.next_link[ip_link_list[i]].add(next_link)

                        # as_rel
                        for i in range(0, len(ip_link_list)):
                            ip1, ip2 = ip_link_list[i]
                            self.router_link[ip_link_list[i]] = (ip_router_dict[ip1], ip_router_dict[ip2])
                            self.asn[ip_link_list[i]] = (ip_as_dict[ip1], ip_as_dict[ip2])
                            if ip_as_dict[ip1] == '' and ip_as_dict[ip2] == '':
                                self.as_rel[ip_link_list[i]] = 'nn'
                            elif ip_as_dict[ip1] == '' and ip_as_dict[ip2] == '-1':
                                self.as_rel[ip_link_list[i]] = 'n-1'
                            elif ip_as_dict[ip1] == '-1' and ip_as_dict[ip2] == '':
                                self.as_rel[ip_link_list[i]] = '-1n'
                            elif ip_as_dict[ip1] == '' and int(ip_as_dict[ip2]) < -1:
                                self.as_rel[ip_link_list[i]] = 'n-'
                            elif ip_as_dict[ip2] == '' and int(ip_as_dict[ip1]) < -1:
                                self.as_rel[ip_link_list[i]] = '-n'
                            elif ip_as_dict[ip1] == '' and int(ip_as_dict[ip2]) > 0:
                                self.as_rel[ip_link_list[i]] = 'n+'
                            elif ip_as_dict[ip2] == '' and int(ip_as_dict[ip1]) > 0:
                                self.as_rel[ip_link_list[i]] = '+n'
                            elif ip_as_dict[ip1] == '-1' and ip_as_dict[ip2] == '-1':
                                self.as_rel[ip_link_list[i]] = '-1-1'
                            elif ip_as_dict[ip2] == '-1' and ip_as_dict[ip1] == '-1':
                                self.as_rel[ip_link_list[i]] = '-1-1'
                            elif ip_as_dict[ip1] == '-1' and int(ip_as_dict[ip2]) < -1:
                                self.as_rel[ip_link_list[i]] = '-1-'
                            elif ip_as_dict[ip2] == '-1' and int(ip_as_dict[ip1]) < -1:
                                self.as_rel[ip_link_list[i]] = '--1'
                            elif ip_as_dict[ip1] == '-1' and int(ip_as_dict[ip2]) > 0:
                                self.as_rel[ip_link_list[i]] = '-1+'
                            elif ip_as_dict[ip2] == '-1' and int(ip_as_dict[ip1]) > 0:
                                self.as_rel[ip_link_list[i]] = '+-1'
                            elif int(ip_as_dict[ip1]) < -1 and int(ip_as_dict[ip2]) < -1:
                                self.as_rel[ip_link_list[i]] = '--'
                            elif int(ip_as_dict[ip2]) < -1 and int(ip_as_dict[ip1]) < -1:
                                self.as_rel[ip_link_list[i]] = '--'
                            elif int(ip_as_dict[ip1]) < -1 and int(ip_as_dict[ip2]) > 0:
                                self.as_rel[ip_link_list[i]] = '-+'
                            elif int(ip_as_dict[ip2]) < -1 and int(ip_as_dict[ip1]) > 0:
                                self.as_rel[ip_link_list[i]] = '+-'
                            elif ip_as_dict[ip1] == ip_as_dict[ip2]:
                                self.as_rel[ip_link_list[i]] = 'same'
                            else:
                                self.as_rel[ip_link_list[i]] = as_rel_dict[(ip_as_dict[ip1], ip_as_dict[ip2])]
                except EOFError:
                    break

        # np.save('IPLinks/ip_link_router_link.npy', self.router_link)
        # np.save('IPLinks/ip_link_asn.npy', self.asn)
        # np.save('IPLinks/ip_link_as_rel.npy', self.as_rel)
        # np.save('IPLinks/ip_link_prev_link.npy', self.prev_link)
        # np.save('IPLinks/ip_link_next_link.npy', self.next_link)

    def init_prob(self):
        """Determine relationship probabilities and relationships from IP2AS data initialization.
        The key of the self.prob dictionary is an IP link pair, and the value is a tuple (probability that the link is intra,inter)."""
        # print(len(self.router_link))
        for iplink in self.router_link:
            # print(iplink)
            as1, as2 = self.asn[iplink]
            # print(as1, as2)
            if as1 != as2:
                self.prob[iplink] = (0.0, 1.0)
                self.rel1[iplink] = 'inter'
            else:
                self.prob[iplink] = (1.0, 0.0)
                self.rel1[iplink] = 'intra'
            if self.as_rel[iplink] == 'p2c':
                self.prob[iplink] = (1.0, 0.0)
                self.rel1[iplink] = 'intra'
            if self.as_rel[iplink] == 'same':
                for n in self.next_link[iplink]:
                    rel = self.as_rel[n]
                    if rel == 'p2c':
                        self.prob[iplink] = (0.0, 1.0)
                        self.rel1[iplink] = 'inter'
                        break

    def assign_fan_in(self):
        for link in self.prob:
            self.fan_in[link] = 0
            for p in self.prev_link[link]:
                AS1, AS2 = self.asn[p]
                if AS1 != AS2:
                    self.fan_in[link] += 1

    def assign_fan_out(self):
        for link in self.prob:
            self.fan_out[link] = 0
            for n in self.next_link[link]:
                AS1, AS2 = self.asn[n]
                if AS1 != AS2:
                    self.fan_out[link] += 1

    def assign_as_rel_prev(self):
        for link in self.prob:
            self.as_rel_prev[link] = set()
            rel2 = self.as_rel[link]
            for p in self.prev_link[link]:
                rel1 = self.as_rel[p]
                self.as_rel_prev[link].add((rel1, rel2))
            self.as_rel_prev[link] = frozenset(self.as_rel_prev[link])

    def assign_as_rel_next(self):
        for link in self.prob:
            self.as_rel_next[link] = set()
            rel1 = self.as_rel[link]
            for n in self.next_link[link]:
                rel2 = self.as_rel[n]
                self.as_rel_next[link].add((rel1, rel2))
            self.as_rel_next[link] = frozenset(self.as_rel_next[link])

    def assign_ip_distance(self):
        for link in self.prob:
            ip1, ip2 = link
            ip1_1 = int(ip1.split('.')[0])
            ip1_2 = int(ip1.split('.')[1])
            ip1_3 = int(ip1.split('.')[2])
            ip1_4 = int(ip1.split('.')[3])
            ip1_arr = [ip1_1, ip1_2, ip1_3, ip1_4]
            ip2_1 = int(ip2.split('.')[0])
            ip2_2 = int(ip2.split('.')[1])
            ip2_3 = int(ip2.split('.')[2])
            ip2_4 = int(ip2.split('.')[3])
            ip2_arr = [ip2_1, ip2_2, ip2_3, ip2_4]
            self.ip_distance[link] = int(np.linalg.norm(np.array(ip1_arr) - np.array(ip2_arr)))

    def construct_attributes(self):
        self.assign_fan_in()
        self.assign_fan_out()
        self.assign_as_rel_prev()
        self.assign_as_rel_next()
        self.assign_ip_distance()

    def origin_txt(self, feature, file1, file2):
        with open(file1, 'a') as f:
            for link in self.prob:
                if self.rel1[link] == 'intra':
                    x1 = feature[link]
                    f.write(str(x1) + '\n')
        with open(file2, 'a') as f2:
            for link in self.prob:
                if self.rel1[link] == 'inter':
                    x2 = feature[link]
                    f2.write(str(x2) + '\n')

