"""
@description: this file contains many statistic helper functions
"""
import pylab as p
import math
import numpy


class histogram:
    def __init__(self):
        self.bucket = []
        self._max = 0.0
        self._min = 0.0
        self._mean = 0.0
        self._mean_pos = 0.0
        self._mean_neg = 0.0
        self._count = 0
        self._count_pos = 0.0
        self._count_neg = 0.0
        self._var = 0
        self._zero = 0
    
    @staticmethod
    def cosine_distance(u, v):
        """
        Returns the cosine of the angle between vectors v and u. This is equal to
        u.v / |u||v|.
        """
        return numpy.dot(u, v) / (math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v)))
    
    def add(self, val):
        """ uncomment this condition if you need filtering """
        #if val == None or not (val > 0.01 or val < -0.01):
        #if False:
        if not (val > 0 or val < 0):
            self._zero += 1
            pass
        else:
            if self._count == 0:
                self._max = val
                self._min = val
                self._mean = val
                self._count += 1
                self._var = 0.0
                if val < 0:
                    self._mean_neg = val
                    self._count_neg = 1
                elif val > 0:
                    self._mean_pos = val
                    self._count_pos = 1
            else:
                if val > self._max:
                    self._max = val
                if val < self._min:
                    self._min = val
                self._count += 1
                old_mean = self._mean
                self._mean += (val - self._mean) / float(self._count)
                self._var += (val - old_mean) * (val - self._mean)
                if val < 0:
                    if self._count_neg == 0:
                        self._mean_neg = val
                        self._count_neg = 1
                    else:
                        self._count_neg += 1
                        self._mean_neg += (val - self._mean_neg) / float(self._count_neg)
                elif val > 0:
                    if self._count_pos == 0:
                        self._mean_pos = val
                        self._count_pos = 1
                    else:
                        self._count_pos += 1
                        self._mean_pos += (val - self._mean_pos) / float(self._count_pos)
            self.bucket.append(val)
    
    def min(self):
        return self._min

    def max(self):
        return self._max

    def avg(self):
        return self._mean

    def avg_pos(self):
        return self._mean_pos
    
    def avg_neg(self):
        return self._mean_neg
    
    def count(self):
        return self._count
    
    def count_pos(self):
        return self._count_pos
    
    def count_neg(self):
        return self._count_neg

    def count_zero(self):
        return self._zero

    def var(self):
        if self._count < 2:
            return 0.0
        return self._var / float(self._count -1)

    def std(self):
        return self.var() ** 0.5

    
    
    def histogram(self, bnum):
        beam_num = bnum
        beam_width = (self._max - self._min)/float(beam_num)
        index = []
        for i in range(beam_num):
            index.append(self._min+beam_width*i)
        distribution = [0]*beam_num
        for e in self.bucket:
            if e == self._max:
                distribution[beam_num-1] += 1
            else:
                distribution[int(math.floor((e - self._min)/beam_width))] += 1
        return (index, distribution)
        
    def draw_histogram(self, bnum, filename):
        (index, distribution) = self.histogram(bnum)
        fig = p.figure()
        ax = fig.add_subplot(1,1,1)
        x_axis = [i for i in range(len(index))]
        x_stick = ["%.2f" %(index[i]) for i in range(len(index))]
        for i in range(len(x_stick)):
            if (i+1)%2 == 0:
                x_stick[i] = ""
        ax.bar(x_axis, distribution, width=0.8, facecolor='blue')
        ax.set_xticks(x_axis)
        ax.set_xticklabels(x_stick)
        p.savefig(filename)
        return (index, distribution)
    
    
    def histogram_fixed(self, filename):
        """
        In this function, we have fixed number of bars
        """
        index = []
        for i in range(53):
            index.append(-0.52+i*0.02)
        #print index
        distribution = [0]*53
        for e in self.bucket:
            if e > 0.5:
                distribution[53-1] += 1
            elif e < -0.5:
                distribution[0] += 1
            else:
                distribution[int(math.floor((e + 0.52)/0.02))] += 1
        fig = p.figure(figsize=(16, 8), dpi=80)
        ax = fig.add_subplot(1,1,1)
        x_axis = [i for i in range(len(index))]
        ax.bar(x_axis, distribution, width=0.8, facecolor='blue')
        ax.set_xticks(x_axis)
        x_stick = ["%.2f" %(index[i]) for i in range(len(index))]
        for i in range(len(x_stick)):
            if (math.fabs(index[i])+0.001)%0.1 > 0.01:
                x_stick[i] = ""
            else:
                pass
        ax.set_xticklabels(x_stick)
        p.savefig(filename)
        return (index, distribution)
    
    def histogram_2(self):
        """
        We generate a distribution from -1 to 1 with the interval of 0.05
        there are 42 bars in the distribution
        """
        distribution = [0]*42
        for e in self.bucket:
            if e < -1.0:
                distribution[0] += 1
            elif e >= 1.0:
                distribution[41] += 1
            else:
                distribution[int(1+math.floor((e + 1.0)/0.05))] += 1
        sumd = math.fsum(distribution)
        if sumd > 0:
            for i in range(len(distribution)):
                distribution[i] = distribution[i]/sumd
        return distribution
    
    def histogram_2_normalized(self):
        """
        We generate a distribution from -1 to 1 with the interval of 0.05
        there are 42 bars in the distribution
        The value is normalized using [x_i -E(X)]/sigma(X)
        """
        distribution = [0]*42
        for e in self.bucket:
            if e < -1.0:
                distribution[0] += 1
            elif e >= 1.0:
                distribution[41] += 1
            else:
                distribution[int(1+math.floor((e + 1.0)/0.05))] += 1
        for i in range(len(distribution)):
            distribution[i] = (distribution[i] - self.avg())/self.std()
        return distribution
    
    
        
    
"""        
def main():
    myhist = histogram()
    myhist.histogram_fixed("sds")
    
if __name__ == "__main__":
    main()
"""