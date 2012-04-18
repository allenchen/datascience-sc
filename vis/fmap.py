import random

__author__ = "Allen Chen"
__email__ = "allen.sl.chen@gmail.com"

# I really like collections.defaultdict.  Unfortunately, it is a huge pain to
# use it as a frequency map because it's not easy enough to sample from it, 
# and some simple statistical operations are absent.
# So that's why this exists.  You can use a dictionary as a frequency map and
# things like sampling, totals and top_n are less annoying.

class fmap(dict):
    def __init__(self):
        self.total = 0
        super(fmap,self).__init__()

    def __getitem__(self, k):
        if k not in self:
            return 0
        else:
            return super(fmap,self).__getitem__(k)

    def __delitem__(self, k):
        self.total -= self.__getitem__(k)
        super(fmap, self).__delitem__(k)

    def __setitem__(self, k, v):
        # Setting any entry to zero removes it from the fmap.
        if v == 0:
            self.__delitem__(k)
        else:
            self.total += (v - self.__getitem__(k))
            super(fmap, self).__setitem__(k,v)

    # Sample from the keys with weight given by the value of each key
    # If there is nothing to sample from (ie. no keys, or all keys == 0),
    # then sample() returns None.
    def sample(self):
        if (self.total <= 0):
            raise SamplingError, "Nothing to sample from (self.total <= 0)"

        r = random.randrange(1, self.total + 1)
        count = 0
        for k,v in self.iteritems():
            if (r > count and r <= count + v):
                return k
            count += v
        
        raise SamplingError, "Invalid key/values for sampling - you might " + \
            "have a negative value in the map or total may have been modified."

    # Returns the probability that a particular key k will be chosen by
    # random weighted sampling.
    def get_probability(self, k):
        if (self.total <= 0):
            # Nothing to sample from - will raise divide by zero error
            return 0
        return self.__getitem__(k)/float(self.total)

    # Gets the top n keys with the highest frequency/probability from
    # highest to lowest frequency.
    # Negative n retrieves the lowest n.
    def get_top_n(self, n, emitFrequencies=False):
        if n == 0 or self.total <= 0:
            raise SamplingError,"n == 0 or no data supplied to map (total == 0)."
            return []

        sortReverse = True
        if n < 0:
            sortReverse = False
            n *= -1

        window = []
        for k in self.iterkeys():
            window.append((k,self.__getitem__(k)))
            window.sort(lambda x,y: cmp(x[1], y[1]), reverse=sortReverse)
            window = window[:n]

        if emitFrequencies:
            return window

        return map(lambda x: x[0], window)

    # Returns the average frequency
    def average(self):
        return self.total/float(len(self.keys()))

    # Returns a copy of the fmap
    def copy(self):
        newfmap = fmap()
        for k,v in self.iteritems():
            newfmap[k] = v
        newfmap.total = self.total
        return newfmap
    
    # Adds Gaussian noise to each point with mean mu and standard deviation sigma
    def add_gaussian_noise(self, mu, sigma):
        for k in self.keys():
            self[k] += random.gauss(mu,sigma)

    # Returns the mean frequency value of the keys in the fmap
    def average_frequency_value(self):
        return self.total/float(self.__len__())

class SamplingError(StandardError):
    pass
