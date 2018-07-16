from collections import defaultdict

import Edge


class EdgeWeightedGraph(object):

    def __init__(self, vertex):
        self.v = vertex
        self.e = 0
        self.adjacent = {}
        self.adjacent = defaultdict(list)
        # self.adj = {k: [] for k in range(vertex)}

    def V(self):
        return self.v

    def E(self):
        return self.e

    def EdgeWeightedGraph(self, v, w, weight):
        new_edge = Edge.Edge(v, w, weight)
        self.addEdge(new_edge)

    def addEdge(self, new_edge):
        v = new_edge.endpoint()
        w = new_edge.other(v)

        self.adjacent[v].append(new_edge)
        self.adjacent[w].append(new_edge)
        self.e += 1

    def validateVertex(self, v):
        if v < 0 or v >= self.v:
            print 'Houston we have a problem'

    def adj(self, v):
        return self.adjacent[v]

    def degree(self, v):
        return len(self.adjacent[v])

    def edges(self):
        _edges = []

        for v in range(self.v + 1):
            for e in self.adjacent[v]:
                if e.other(v) > v:
                    _edges.append(e)
        return _edges