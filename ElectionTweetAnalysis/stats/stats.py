"""
@description: this file contains many statistic helper functions
"""
import matplotlib.pyplot as plt
import pylab as p
import math

class histogram:
    def __init__(self):
        self.bucket = []
        self._max = 0.0;
        self._min = 0.0;
        self._mean = 0.0;
        self._count = 0;
        
    def add(self, val):
        if self._count == 0:
            self._max = val
            self._min = val
            self._mean = val
            self._count = 1
        else:
            if val > self._max:
                self._max = val
            if val < self._min:
                self._min = val
            self._mean = (self._mean*self._count + val)/float(self._count+1)
            self._count += 1
        self.bucket.append(val)
    
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
        
    def draw_histogram(self, bnum,filename):
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
    
    """ In this function, we have fixed number of bars """
    def histogram_fixed(self, filename):
        index = []
        for i in range(53):
            index.append(-0.52+i*0.02)
        print index
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
"""        
def main():
    myhist = histogram()
    myhist.histogram_fixed("sds")
    
if __name__ == "__main__":
    main()
"""