import numpy as np


class CPP:

    def __init__(self, n):
        mat_shape = (n, n)
        self.n = n
        self.delta = [0] * n
        self.defined = np.full(shape=mat_shape, fill_value=False)
        self.c = np.zeros(shape=mat_shape, dtype=np.float)  # floats
        self.f = np.zeros(shape=mat_shape, dtype=np.int)
        self.arcs = np.zeros(shape=mat_shape, dtype=np.int)
        self.path = np.zeros(shape=mat_shape, dtype=np.int)
        self.basic_cost = 0.

        self.neg = set()
        self.pos = set()

    def solve(self):
        print('--- Computing least cost paths')
        self.least_cost_paths()
        print('--- Checking validity of graph')
        self.check_valid()
        print('--- Finding unbalanced nodes')
        self.find_unbalanced()
        print('--- Finding feasible edges')
        self.find_feasible()
        print('--- Improving...')
        while self.improvements():
            continue

    def add_arc(self, u, v, cost):

        # if u < 0 or v < 0:
        #     print(f'adding arc with negative indexes?! {(u, v, cost)}')

        self.basic_cost += cost

        if not self.defined[u, v] or self.c[u, v] > cost:
            self.c[u, v] = cost
            self.defined[u, v] = True
            self.path[u, v] = v

        self.arcs[u, v] += 1
        self.delta[u] += 1
        self.delta[v] -= 1

    def add_arcs(self, arcs):
        for arc in arcs:
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
                                print(f'negative cycle on node {i}')
                                return  # stop on negative cycle
                        # if self.defined[k, j]:
                        #     combined_cost = self.c[i, k] + self.c[k, j]
                        #     # If path not defined or better path available
                        #     if not self.defined[i, j] or combined_cost < self.c[i, j]:
                        #         self.path[i, j] = self.path[i, k]
                        #         self.c[i, j] = combined_cost
                        #         self.defined[i, j] = True
                        #         if i == j and self.c[i, j] < 0:
                        #             print(f'negative cycle on node {i}')
                        #             return  # stop on negative cycle

    def check_valid(self):
        for i in range(self.n):
            for j in range(self.n):
                if not self.defined[i, j]:
                    raise Exception('Graph is not strongly connected')
            if self.c[i, i] < 0:
                raise Exception('Graph has negative cycle')

    def find_unbalanced(self):

        for i in range(self.n):  # initialise sets
            if self.delta[i] < 0:
                self.neg.add(i)
            elif self.delta[i] > 0:
                self.pos.add(i)

    def find_feasible(self):

        # delta = self.delta.copy()

        for i in self.neg:
            for j in self.pos:
                self.f[i, j] = min(-self.delta[i], self.delta[j])
                self.delta[i] += self.f[i, j]
                self.delta[j] -= self.f[i, j]

    def improvements(self):

        print('improving')

        sort_neg = list(self.neg)
        sort_pos = list(self.pos)
        sort_neg.sort()
        sort_pos.sort()
        print('neg =', sort_neg)
        print('pos =', sort_pos)

        residual = CPP(self.n)

        for i in self.neg:
            for j in self.pos:
                residual.add_arc(i, j, self.c[i, j])
                # if i == 385 or j == 385:
                #     print(f'added arc {(i, j, self.c[i, j])}')
                if self.f[i, j] != 0:
                    residual.add_arc(j, i, -self.c[i, j])
                    # if i == 385 or j == 385:
                    #     print(f'added arc {(j, i, -self.c[i, j])}')

        residual.least_cost_paths()  # find a negative cycle

        for i in range(self.n):

            if residual.c[i, i] < 0:  # cancel the cycle (if any)

                print(f'residual.c[{i}, {i}] = {residual.c[i, i]}')

                k, u, v = 0, 0, 0
                k_unset = True

                u = i
                count = 0
                while True:  # find k to cancel
                    v = residual.path[u, i]
                    print(f'residual.path[{u}, {i}] = {v}')
                    print('1 -', (u, v))
                    # print(residual.path)
                    if residual.c[u, v] < 0 and (k_unset or k > self.f[v, u]):
                        print('entered if')
                        k = self.f[v, u]
                        k_unset = False
                    u = v
                    count += 1
                    if u == i:
                        break
                    if count > 10:
                        raise Exception('max iteration reached')

                u = i
                while True:  # cancel k along the cycle
                    v = residual.path[u, i]
                    print(f'residual.path[{u}, {i}] = {v}')
                    print('2 -', (u, v))
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
                path.append((u, v))

        return path
