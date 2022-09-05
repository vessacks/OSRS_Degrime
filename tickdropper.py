import numpy as np
import time


def tick_dropper(odds=100, sleep_time = .6):
    if np.random.randint(0,odds) == 1:
        time.sleep(sleep_time)
