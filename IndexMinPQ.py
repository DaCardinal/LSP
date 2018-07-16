
from collections import defaultdict


class MinHeap:
    def __init__(self):
        self._a = [0]
        self.count = 0;

    def __iter__(self):
        return self

    def next(self):
        if not self.isEmpty():
            return self.delMin()
        else:
            raise StopIteration()

    def _swim(self, k):
        while (k > 1 and self._a[k] < self._a[k / 2]):
            self._exchange(k, k / 2)
            k = k / 2

    def _exchange(self, x, y):
        w = self._a[x]
        self._a[x] = self._a[y]
        self._a[y] = w

    def _sink(self, k, l=None):
        if l is None:
            l = self.count

        while (2 * k <= l):
            j = 2 * k
            if not j + 1 > l and self._a[j] > self._a[j + 1]:
                j += 1
            if (j < self.count and self._a[k] > self._a[j]):
                self._exchange(k, j)
            if not (self._a[k] > self._a[j]):
                break
            k = j

    def append(self, n):
        self._a.append(n)
        self.count += 1
        self._swim(self.count)

    def delMin(self):
        mn = self._a[1]
        self._exchange(1, self.count)
        self.count -= 1

        del self._a[-1]
        self._sink(1)

        return mn

    def isEmpty(self):
        return self.count < 1


class IndexMinPQ:
    def __init__(self, maxN):
        if maxN < 0:
            raise ValueError('Minimum size of an IndexMinPQ must be greater than 0')
        self.maxN = maxN
        self.n = 0

        self.pq = {}
        self.keys = {}
        self.qp = {}

        self.pq = defaultdict(int)
        self.keys = defaultdict(int)
        self.qp = defaultdict(int)

        for i in range(maxN + 1):
            self.qp[i] = -1

    def isEmpty(self):
        return self.n == 0

    def contains(self, i):
        if i < 0 or i >= self.maxN:
            raise ValueError('index out of bounds')
        return self.qp[i] != -1

    def size(self):
        return self.n

    def insert(self, i, key):
        if i < 0 or i >= self.maxN:
            raise ValueError('index out of bounds')
        if self.contains(i):
            raise ValueError('index is already in the priority queue')

        self.n += 1
        self.qp[i] = self.n
        self.pq[self.n] = i
        self.keys[i] = key
        self.swim(self.n)

    def minIndex(self):
        if self.n == 0:
            raise ValueError('Priority queue underflow')
        return self.pq[1]

    def minKey(self):
        if self.n == 0:
            raise ValueError('Priority queue underflow')
        return self.keys[self.pq[1]]

    def delMin(self):
        if self.n == 0:
            raise ValueError('Priority queue underflow')

        min = self.pq[1]
        self.exchange(1, self.n)
        self.n -= 1
        self.sink(1)
        self.qp[min] = -1
        # del self.keys[self.pq[self.n + 1]]
        del self.keys[min]
        self.pq[self.n + 1] = -1

        return min

    def keyOf(self, i):
        if i < 0 or i >= self.maxN:
            raise ValueError('index out of bounds')
        if not self.contains(i):
            raise ValueError('index is already in the priority queue')
        else:
            return self.keys[i]

    def changeKey(self, i, key):
        if i < 0 or i >= self.maxN:
            raise ValueError('index out of bounds')
        if not self.contains(i):
            raise ValueError('index is already in the priority queue')

        self.keys[i] = key
        self.swim(self.qp[i])
        self.sink(self.qp[i])

    def change(self, i, key):
        self.changeKey(i, key)

    def decreaseKey(self, i, key):
        if i < 0 or i >= self.maxN:
            raise ValueError('index out of bounds')
        if not self.contains(i):
            raise ValueError('index is already in the priority queue')
        if self.keys[i] < key:
            raise ValueError('Calling decreaseKey with given argument will not strictly decrease the key')

        self.keys[i] = key
        self.swim(self.qp[i])

    def increaseKey(self, i, key):
        if i < 0 or i >= self.maxN:
            raise ValueError('index out of bounds')
        if not self.contains(i):
            raise ValueError('index is already in the priority queue')
        if self.keys[i] > key:
            raise ValueError('Calling increaseKey with given argument will not strictly increase the key')

        self.keys[i] = key
        self.sink(self.qp[i])

    def delete(self, i):
        if i < 0 or i >= self.maxN:
            raise ValueError('index out of bounds')
        if not self.contains(i):
            raise ValueError('index is already in the priority queue')

        index = self.qp[i]
        self.exchange(index, self.n)
        self.n -= 1

        self.swim(index)
        self.sink(index)

        del self.keys[i]
        self.qp[i] = -1

    def greater(self, i, j):
        return self.keys[self.pq[i]] > self.keys[self.pq[j]]

    def exchange(self, i, j):
        swap = self.pq[i]
        self.pq[i] = self.pq[j]
        self.pq[j] = swap
        self.qp[self.pq[i]] = i
        self.qp[self.pq[j]] = j

    def swim(self, k):
        while k > 1 and self.greater(k / 2, k):
            self.exchange(k, k / 2)
            k /= 2

    def sink(self, k):
        while 2 * k <= self.n:
            j = 2 * k

            if j < self.n and self.greater(j, j + 1):
                j += 1

            if not self.greater(k, j):
                break
            self.exchange(k, j)
            k = j

    def __str__(self):
        return "IndexMinPQ of max:{0}, size:{1}, keys:{2}, queue:{3}".format(self.maxN, self.n, self.keys, self.pq)

    def __keyContainmentCheck(self, i):
        if self.contains(i):
            raise ValueError('provided index is already contained within the priority queue')

    def __missingKeyCheck(self, i):
        if not self.contains(i):
            raise ValueError('Provided key is not contained within the priority queue')