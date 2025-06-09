import math
import heapq
import matplotlib.pyplot as plt


# Road Segment class
class RoadSegment:
    def __init__(self, start, direction, length = 10, priority = 0):
        self.start = start
        self.dire