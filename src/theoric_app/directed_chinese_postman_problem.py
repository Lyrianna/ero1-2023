import numpy as np


class CPP:

    def __init__(self, n):
        mat_shape = (n, n)
        self.n = n
        self.delta = [0] * n
        self.defined = np.full(shape=mat_shape, fill_value=False)
        self.c = np.zeros(shape=mat_shape)  # floats
        self.f = np.zeros(shape=mat_shape, dtype=np.int8)
        self.arcs = np.zeros(shape=mat_shape, dtype=np.int8)
        self.path = np.zeros(shape=mat_shape, dtype=np.int8)
        self.basic_cost = 0.

        self.neg = []
        self.pos = []

    def solve(self):

        print('\n--- Initialization')
        print('c =\n', self.c)
        print('defined =\n', self.defined)
        print('path =\n', self.path)
        print('arcs =\n', self.arcs)
        print('delta =\n', self.delta)

        print('\n--- Least cost paths')
        self.least_cost_paths()
        print('path =\n', self.path)
        print('c =\n', self.c)
        print('defined =\n', self.defined)

        print('\n--- Check valid')
        self.check_valid()

        print('\n--- Find unbalanced')
        self.find_unbalanced()
        print('neg =\n', self.neg)
        print('pos =\n', self.pos)

        print('\n--- Find feasible')
        self.find_feasible()
        print('f =\n', self.f)
        print('delta =\n', self.delta)

        print('\n--- Improvements')
        while self.improvements():
            continue

    def add_arc(self, u, v, cost):

        self.basic_cost += cost

        if not self.defined[u, v] or self.c[u, v] > cost:
            self.c[u, v] = cost
            self.defined[u, v] = True
            self.path[u, v] = v

        self.arcs[u, v] += 1
        self.delta[u] += 1
        self.delta[v] -= 1

    def add_arcs(self, arcs):
        print('add_arcs')
        for arc in arcs:
            print(arc)
            self.add_arc(*arc)

    def least_cost_paths(self):
        for k in range(self.n):
            for i in range(self.n):
                if self.defined[i, k]:
                    for j in range(self.n):
                        if self.defined[k, j] \
                                and (not self.defined[i, j] or self.c[i, j] > (self.c[i, k] + self.c[k, j])):
                            self.path[i, j] = self.path[i, k]
                            self.c[i, j] = self.c[i, k] + self.c[k, j]
                            self.defined[i, j] = True
                            if i == j and self.c[i, j] < 0:
                                return  # stop on negative cycle

    def check_valid(self):
        for i in range(self.n):
            for j in range(self.n):
                if not self.defined[i, j]:
                    raise Exception('Graph is not strongly connected')
            if self.c[i, i] < 0:
                raise Exception('Graph has negative cycle')

    def find_unbalanced(self):

        n_neg, n_pos = 0, 0  # number of vertices of negative/positive delta

        for i in range(self.n):
            if self.delta[i] < 0:
                n_neg += 1
            elif self.delta[i] > 0:
                n_pos += 1

        self.neg = [0] * n_neg
        self.pos = [0] * n_pos
        n_neg, n_pos = 0, 0

        for i in range(self.n):  # initialise sets
            if self.delta[i] < 0:
                self.neg[n_neg] = i
                n_neg += 1
            elif self.delta[i] > 0:
                self.pos[n_pos] = i
                n_pos += 1

    def find_feasible(self):

        delta = self.delta.copy()

        for i in self.neg:
            for j in self.pos:
                self.f[i, j] = min(-delta[i], delta[j])
                delta[i] += self.f[i, j]
                delta[j] -= self.f[i, j]

    def improvements(self):

        residual = CPP(self.n)

        for i in self.neg:
            for j in self.pos:
                residual.add_arc(i, j, self.c[i, j])
                if self.f[i, j] != 0:
                    residual.add_arc(j, i, -self.c[i, j])

        residual.least_cost_paths()  # find a negative cycle

        for i in range(self.n):

            if residual.c[i, i] < 0:  # cancel the cycle (if any)

                k, u, v = 0, 0, 0
                k_unset = True

                u = i
                while True:  # find k to cancel
                    v = residual.path[u, i]
                    if residual.c[u, v] < 0 and (k_unset or k > self.f[v, u]):
                        k = self.f[v, u]
                        k_unset = False
                    u = v
                    if u == i:
                        break

                u = i
                while True:  # cancel k along the cycle
                    v = residual.path[u, i]
                    if residual.c[u, v] < 0:
                        self.f[v, u] -= k
                    else:
                        self.f[u, v] += k
                    u = v
                    if u == i:
                        break

                return True  # have another go
        return False  # no improvements found

    def cost(self):
        return self.basic_cost + self.phi()

    def phi(self):
        phi = 0.
        for i in range(self.n):
            for j in range(self.n):
                phi += self.c[i, j] * self.f[i, j]
        return phi

    def find_path(self, from_v, f):  # find a path between unbalanced vertices
        for i in range(self.n):
            if f[from_v][i] > 0:
                return i
        return None

    def get_optimal_path(self, start_v):

        v = start_v

        f = self.f.copy()
        arcs = self.arcs.copy()

        path = []

        while True:

            u = v
            v = self.find_path(u, f)

            if v is not None:
                f[u, v] -= 1  # remove path
                while u != v:  # break down path into its arcs
                    p = self.path[u, v]
                    print(f'Take arc {u, p}')
                    path.append((u, v))
                    u = p
            else:
                bridge_v = self.path[u, start_v]
                if arcs[u][bridge_v] == 0:
                    break  # finished if bridge already used
                v = bridge_v
                for i in range(self.n):  # find an unused arc, using bridge last
                    if i != bridge_v and arcs[u, i] > 0:
                        v = i
                        break
                arcs[u, v] -= 1  # decrement count of parallel arcs
                print(f'Take arc {u, v}')
                path.append((u, v))

        return path
