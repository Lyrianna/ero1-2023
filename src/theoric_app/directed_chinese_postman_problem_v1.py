import numpy as np
import scipy
import scipy.sparse


def shortest_path(mat, u, v):
    """
    :param mat: weighted mat
    :param u: starting node
    :param v: end node
    :return: dist_matrix, path
    """
    # Convert mat to csr_mat?
    dist_matrix, predecessors = scipy.sparse.csgraph.shortest_path(
        mat, directed=True, indices=u, return_predecessors=True)
    print(predecessors)
    node = v
    path = []
    while node != u:
        path.append(node)
        node = predecessors[node]
    path.append(node)
    path.reverse()
    return dist_matrix, path


def dcpp(n, mat):
    """
    Only works for strongly connected graph

    :param n: degree of the graph
    :param mat: weighted adjacency matrix
    :return: optimal
    """

    """
    Step 1:
        Set the initial solution: f(i, j) = 0, R(i. j) = d(i, j), w(i, j) = 0, for all (i, j) E A and p(i) = 0
        for all i E V.
    """

    f = np.zeros(shape=(n, n))
    r = mat.copy()
    w = np.zeros(shape=(n, n))
    p = [0] * n

    # -------------------
    # Not sure about this
    for i in range(n):
        for j in range(n):
            if mat[i, j] != 0:
                p[i] -= 1
                p[j] += 1
    # -------------------

    def feasible(u, v):
        return f[u, v] >= 1

    def select_unfeasible_arc():
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if not feasible(i, j):
                    return i, j
        return None

    def increase_arc(u, v):
        f[u, v] += 1
        # -------
        p[u] -= 1
        p[v] += 1
        # -------

    def decrease_arc(u, v):
        """
        Arcs are changed only from unfeasible into feasible,
        that is, f(i, j) will not be decreased when it is equal to 0 or 1
        """
        if f[u, v] > 1:
            f[u, v] -= 1
            # -------
            p[u] += 1
            p[v] -= 1
            # -------

    def arc_path_from_path(path):
        arc_path = []
        prev = None
        for v in path:
            arc_path.append((prev, v))
            prev = v
        arc_path.pop(0)
        return arc_path

    while True:

        """
        Step 2:
            Check the status of the arcs.
            If all arcs are feasible, the algorithm stops and the optimal enlarged Euler network is found.
            Else, select an unfeasible arc, say (t, s), and go go Step 3.
        """

        print(f)

        unfeasible_arc = select_unfeasible_arc()
        if unfeasible_arc is None:  # All arcs arcs feasible
            break

        print(unfeasible_arc)

        t, s = unfeasible_arc

        # Find shortest path from s to all other vertex SP(s, i), i E V
        # Let d(i) = length of SP(s, i)
        d, sp = shortest_path(mat, s, t)

        cycle_ts = [t, s] + sp

        for i, j in arc_path_from_path(cycle_ts):
            # If arc is along orientation of cycle_ts ?!?!?
            if p[i] > p[j]:  # along?
                increase_arc(i, j)
            elif p[i] < p[j]:  # against?
                decrease_arc(i, j)

        """
        Step 4:
            W, 8 = lined, d(t)) + R(i, j) - min(d( j), d(t)];
            if f(i, j) = 0, then set w(i, j) = 0 and w(j, i) = inf
            if f(i, j) = 1, then set w(i, j) = R(i, j) and w(j, i) = inf
            if f(i, j) >, 2, then set wfi, j) = w(j, i) = 0.
            Go to Step 2.
        """
        for i in range(n):
            for j in range(n):

                r[i, j] = min(d[i], d[t]) + r[i, j] - min(d[j], d[t])

                if f[i, j] == 0:
                    w[i, j] = 0
                    w[j, i] = np.inf

                elif f[i, j] == 1:
                    w[i, j] = r[i, j]
                    w[j, i] = np.inf

                elif f[i, j] >= 2:
                    w[i, j] = 0
                    w[j, i] = 0

    return f
