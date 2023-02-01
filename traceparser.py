'''
Filename: traceparser
Description: Processing traceroute paths in json format, extracting source address, destination address, IP path, and RTT.
FunctionList:
1.class IpPath  // IP path
2.class Traces // Process traceroute paths
    def parse_trace_paths(self, trace_file) //Process traceroute paths
3.def pickle_load() // Load the file of processed ip_paths（ip_paths.pkl）
'''


import jsonpath
import os
import json
import pickle


class IpPath(object):
    """ IP paths"""
    def __init__(self):
        self.src = ''
        self.dst = ''
        self.path = []
        self.rtt = []

    def __str__(self):
        return "src:{}\ndst:{}\npath:{}\nrtt:{}".format(self.src, self.dst, self.path, self.rtt)


class Traces(object):
    """ Class for parsing traceroute paths """
    def __init__(self):
        self.ip_paths = []   # a list of IP paths

    @staticmethod
    def save_ip_path(ip_path):
        f = open("ip_paths.pkl", 'ab')
        string = pickle.dumps(ip_path)
        f.write(string)
        f.close()

    def parse_trace_paths(self, trace_file):
        """ Process traceroute paths"""
        with open(trace_file, 'r') as f:
            f.readline()  # Skip the first line
            for line in f:
                trace = json.loads(line)
                ip_path = IpPath()
                ip_path.src = jsonpath.jsonpath(trace, "$.src")
                ip_path.dst = jsonpath.jsonpath(trace, "$.dst")
                ip_path.path = jsonpath.jsonpath(trace, "$.hops[*].addr")  # all IP addresses
                ip_path.rtt = jsonpath.jsonpath(trace, "$.hops[*].rtt")    # all RTTs
                if ip_path.path is not False:
                    self.save_ip_path(ip_path)


def pickle_load():
    with open("ip_paths.pkl", 'rb') as f:
        count = 0
        while True:
            try:
                ip_path = pickle.load(f)
                count += 1
                print('count', count)
            except EOFError:
                break


if __name__ == '__main__':
    file_path = "traceroute_files"   # Folder containing traceroute files in json format
    for filename in os.listdir(file_path):
        traces = Traces()
        traces.parse_trace_paths(file_path + '/' + filename)
    pickle_load()




