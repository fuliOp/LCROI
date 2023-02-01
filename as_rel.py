'''
Filename: as_rel.py
Description: AS relationship
FunctionList:
1.def save_as_rel_dict()  // AS relationship
'''


import numpy as np


def save_as_rel_dict():  # AS relationship
    as_rel = {}
    with open('20190101.as-rel.txt', 'r') as f1:  # CAIDA
        for line in f1:
            if not line.startswith("#"):
                AS1, AS2, rel = line.strip().split("|")
                if rel == '0':
                    as_rel[(AS1, AS2)] = 'p2p'
                    as_rel[(AS2, AS1)] = 'p2p'
                elif rel == '-1':
                    as_rel[(AS1, AS2)] = 'p2c'
                    as_rel[(AS2, AS1)] = 'c2p'

    with open('20190101_as_rel.txt', 'r') as f2:  # The result of ProbLink
        for line in f2:
            AS1, AS2, rel = line.strip().split("|")
            if rel == '0':
                as_rel[(AS1, AS2)] = 'p2p'
                as_rel[(AS2, AS1)] = 'p2p'
            elif rel == '-1':
                as_rel[(AS1, AS2)] = 'p2c'
                as_rel[(AS2, AS1)] = 'c2p'
            elif rel == '1':
                as_rel[(AS1, AS2)] = 'sibling'
                as_rel[(AS2, AS1)] = 'sibling'
    np.save('as_rel.npy', as_rel)


if __name__ == '__main__':
    save_as_rel_dict()
    as_rel = np.load('as_rel.npy', allow_pickle=True).item()


