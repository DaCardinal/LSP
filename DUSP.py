from __future__ import print_function
from collections import defaultdict
import sys
import EWG
import IndexMinPQ


class DijkstraUndirected(object):
    def __init__(self, G, s):
        self.distTo = {}
        self.edgeTo = {}
        self.pq = IndexMinPQ.IndexMinPQ(G.V())

        self.edgeTo = defaultdict(int)
        self.distTo = defaultdict(int)

        for i in range(G.V()):
            self.distTo[i] = sys.maxint

        self.distTo[s] = 0

        self.pq.insert(s, self.distTo[s])

        while not self.pq.isEmpty():
            v = self.pq.delMin()

            for j in G.adj(v):
                self.relax(j, v)

    def relax(self, e, v):
        w = e.other(v)

        if self.distTo[w] > self.distTo[v] + e.weight():
            self.distTo[w] = self.distTo[v] + e.weight()
            self.edgeTo[w] = e

            if self.pq.contains(w):
                self.pq.changeKey(w, self.distTo[w])
            else:
                self.pq.insert(w, self.distTo[w])

    def distanceTo(self, v):
        return self.distTo[v]

    def hasPathTo(self, v):
        return self.distTo[v] < sys.maxint

    def pathTo(self, v):

        if not self.hasPathTo(v):
            return []

        path = []
        x = v
        e = self.edgeTo[v]

        while e:
            path.append(x)
            x = e.other(x)
            e = self.edgeTo[x]
        path.append(x)
        path.reverse()

        return path

# Test main method
def main():
    e = EWG.EdgeWeightedGraph(6)

    e.EdgeWeightedGraph(0, 1, 6)
    e.EdgeWeightedGraph(0, 2, 9)
    e.EdgeWeightedGraph(0, 3, 11)
    e.EdgeWeightedGraph(1, 2, 5)
    e.EdgeWeightedGraph(2, 5, 3)
    e.EdgeWeightedGraph(1, 4, 9)
    e.EdgeWeightedGraph(5, 4, 2)

    source = 0
    dest = 5

    d = DijkstraUndirected(e, source)

    # Print distances
    for t in range(6):
        print('From {0} to {1}, distance is {2}'.format(source, t, d.distanceTo(t)))

    # Find a path
    pathway = d.pathTo(dest)

    if pathway:
        print('Pathway from {0} to {1}: '.format(source, dest), end="")

        for p in pathway:
            print('{0} '.format(p), end="")

        print('')
    else:
        print("No Path")