'''
Filename: feature.py
Description:
FunctionList:
class Features(object):  // The class used to calculate the probability of a feature.
    1._compute_likelihood(self, link_feature, feature_likelihood)
    // Calculate the characteristic likelihood: the characteristic probability P(f|C) for a given link type.
    2.compute_feature_likelihoods(self)   // Compute likelihoods of all the features"
    3.def dump_feature(save_filename, feature)  // Save to file
'''


from collections import defaultdict
from link import IPLinks
import pickle


class Features(object):
    """The class used to calculate the probability of a feature."""
    def __init__(self, iplinks):
        if isinstance(iplinks, IPLinks):
            self.links = iplinks
        else:
            raise TypeError('input must be of type IPLinks.')
        self.fan_in_feature = defaultdict(lambda: [0.0, 0.0])
        self.fan_out_feature = defaultdict(lambda: [0.0, 0.0])
        self.as_rel_prev_feature = defaultdict(lambda: [0.0, 0.0])
        self.as_rel_next_feature = defaultdict(lambda: [0.0, 0.0])
        self.ip_distance_feature = defaultdict(lambda: [0.0, 0.0])

    def _compute_likelihood(self, link_feature, feature_likelihood):
        """Calculate the characteristic likelihood: the characteristic probability P(f|C) for a given link type."""
        # Calculate the probability of each feature
        count_class = [0.0, 0.0]
        for k, v in link_feature.items():
            if k in self.links.prob:
                feature_likelihood[v] = [x + y for x, y in zip(feature_likelihood[v], self.links.prob[k])]  # Count with eigenvalue v
                count_class = list(map(lambda x, y: x + y, self.links.prob[k], count_class))  # Total number
        for i in feature_likelihood:  # The key of feature_likelihood is the feature's v
            # Laplace smoothing (Add-1) smoothing
            feature_likelihood[i] = [(x+1)/(y+len(feature_likelihood)) for x, y in zip(feature_likelihood[i], count_class)]

    def compute_feature_likelihoods(self):
        """Compute likelihoods of all the features"""
        self._compute_likelihood(self.links.fan_in, self.fan_in_feature)
        self._compute_likelihood(self.links.fan_out, self.fan_out_feature)
        self._compute_likelihood(self.links.as_rel_prev, self.as_rel_prev_feature)
        self._compute_likelihood(self.links.as_rel_next, self.as_rel_next_feature)
        self._compute_likelihood(self.links.ip_distance, self.ip_distance_feature)

    @staticmethod
    def dump_feature(save_filename, feature):
        fileObject = open(save_filename, 'w')
        pickle.dump(feature, fileObject)
        fileObject.close()
