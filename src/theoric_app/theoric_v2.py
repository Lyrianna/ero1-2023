"""
Here we go again :bye:
"""
import itertools

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

from graphviz import Digraph


class Graph:

    def __init__(self, degree):
        self.degree = degree
        self.mat = np.zeros([degree, degree])

    def __str__(self):
        return str(self.mat)

    def add_edge(self, u, v, w):
        self.mat[u, v] = w
        self.mat[v, u] = w  # Undirected for now

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(*edge)  # '*' unpacks the edge values

    def node_degree(self, node):
        return sum(map(lambda x: x != 0, self.mat[node]))

    def odd_degree_nodes(self):
        nodes = []
        for i in range(self.degree):
            if self.node_degree(i) % 2 != 0:
                nodes.append(i)
        return nodes

    def shortest_path(self, u, v):
        graph = csr_matrix(self.mat)
        distance_matrix, predecessors = shortest_path(graph, directed=False, indices=u, return_predecessors=True)
        # Might need to retrieve the path later on using the predecessors matrix
        return distance_matrix[v]

    def to_dot(self):
        dot = Digraph()
        # Set styling
        dot.attr('node', shape='circle')
        dot.attr('edge', dir='none', color='blue')
        # Add nodes
        for i in range(self.degree):
            if self.node_degree(i) != 0:  # Do not show isolated nodes
                dot.node(str(i))
        # Add edges
        for i in range(self.degree):
            for j in range(i + 1, self.degree):
                if self.mat[i, j] != 0:
                    # dot.edge(str(i), str(j), str(self.mat[i, j]))
                    dot.edge(str(i), str(j))
        dot.render(view=True, cleanup=True)


def create_complete_graph(degree, pair_weights):
    graph = Graph(degree)
    for p, d in pair_weights.items():
        graph.add_edge(*p, d)
    return graph


def main():

    """Manually create a graph"""
    edges = [
        (0, 1, 1),
        (0, 2, 1),
        (0, 3, 1),
        (1, 4, 1),
        (2, 4, 1),
        (4, 5, 1),
    ]
    graph = Graph(6)
    graph.add_edges(edges)
    print(graph)
    # graph.to_dot()

    """Find odd degree nodes"""
    odd_degree_nodes = graph.odd_degree_nodes()
    print('odd_degree_nodes =', odd_degree_nodes)

    """Compute all possible odd node pairs"""
    odd_node_pairs = list(itertools.combinations(odd_degree_nodes, 2))
    print(odd_node_pairs)

    """Compute the minimum distance for every pair"""
    odd_node_pairs_shortest_distance = {}
    for pair in odd_node_pairs:
        odd_node_pairs_shortest_distance[pair] = graph.shortest_path(*pair)

    # for kv in shortest_paths.items():
    #     print(*kv)
    print(odd_node_pairs_shortest_distance.values())

    """Create a complete graph of those pairs with the minimum distance as weight"""
    graph_odd_complete = create_complete_graph(graph.degree, odd_node_pairs_shortest_distance)
    print(graph_odd_complete)
    # graph_odd_complete.to_dot()

    """
    Compute Minimum Weight Matching, the hardest part :)
    (Edmonds’ Maximum Matching Algorithm)
    .
    .
    .
    """


if __name__ == '__main__':
    main()
