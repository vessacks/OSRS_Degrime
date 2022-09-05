import numpy as np
import time


def speed(mean = .7, stdev = .3, max = .85, min = .6):
    speed = np.random.normal(mean,stdev)
    while speed > max or speed < min:
        speed = np.random.normal(mean,stdev)
    return speed

