import functools


class Edge(object):
    def __init__(self, v, w, weight):
        self.v = v
        self.w = w
        self.wght = weight

    def weight(self):
        return self.wght

    def endpoint(self):
        return self.v

    def other(self, vertex):

        if vertex == self.v:
            return self.w
        elif vertex == self.w:
            return self.v
        else:
            return -1

    def compareTo(self, edge):
        return compareTo(self.wght, edge.wght)

    def toString(self):
        return "Edge with verticies:{0},{1}, Weight:{2}".format(self.v, self.w, self.wght)


@functools.total_ordering
class compareTo:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __lt__(self, other):
        if self.a == other.a:
            return self.b < other.b
        return self.a < other.b

    def __eq__(self, other):
        return self.a == other.b and self.b == other.b


