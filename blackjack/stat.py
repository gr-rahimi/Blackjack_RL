from collections import deque
import numpy as np
import time
import matplotlib.pyplot as plt

class Stat(object):

    def __init__(self,fig , ax, samples, per_sample_iteratins):
        self._fig = fig
        self._ax = ax
        self._samples = samples
        self._iter = 0
        self._sum = 0
        self._per_sample_iterations = per_sample_iteratins
        self._container = deque([0.0] * self._samples, maxlen=samples)
        self._line,  = self._ax.plot(np.linspace(0, samples, samples), self._container)

    def AddSample(self, sample):
        self._iter+=1
        self._sum += sample

        if self._iter == self._per_sample_iterations:
            self._container.appendleft(self._sum/self._per_sample_iterations)
            self._iter = 0
            self._sum = 0.0
            self._line.set_ydata(self._container)
            self._ax.relim()
            self._ax.autoscale_view()
            self._fig.canvas.draw()
            self._fig.canvas.flush_events()
            plt.pause(0.001)
    def setName(self, name):
        self._line.set_label(name)











