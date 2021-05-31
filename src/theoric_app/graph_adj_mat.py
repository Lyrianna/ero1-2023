import numpy as np
from scipy.sparse.csgraph import shortest_path

import graphviz


class GraphAdjMat:

    def __init__(self, degree=0, mat=None, edges=None, osmnx_graph=None, no_edge_value=0):
        self.degree = degree

        if mat is not None:
            self.degree = len(mat)
            self.mat = np.array(mat)
        else:
            self.mat = np.full([degree, degree], no_edge_value)
        self.no_edge_value = no_edge_value

        if edges is not None:
            self.add_edges(edges)

    def __str__(self):
        return str(self.mat)

    def add_edge(self, u, v, w):
        self.mat[u, v] = w
        self.mat[v, u] = w  # Undirected for now

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(*edge)  # '*' unpacks the edge values

    def has_edge(self, u, v):
        return self.mat[u, v] != self.no_edge_value

    def node_degree(self, node):
        return sum(map(lambda x: x != self.no_edge_value, self.mat[node]))

    def odd_degree_nodes(self):
        nodes = []
        for i in range(self.degree):
            if self.node_degree(i) % 2 != 0:
                nodes.append(i)
        return nodes

    def edge_list(self):
        """
        :return: an edge list (u, v, w) representing this graph, useful to convert to adjacency list representation
        """
        edges = []
        for i in range(self.degree):
            for j in range(i + 1, self.degree):
                if self.has_edge(i, j):
                    edges.append((i, j, self.mat[i, j]))
        return edges

    @staticmethod
    def shortest_path(csr_mat, u, v):
        """
        :param csr_mat: compressed sparse row matrix (using csr_matrix on self.mat)
        :param u: starting node
        :param v: end node
        :return: path, length
        """
        distance_matrix, predecessors = shortest_path(csr_mat, directed=False, indices=u, return_predecessors=True)
        node = v
        path = []
        while node != u:
            path.insert(0, (predecessors[node], node))
            node = predecessors[node]
        return path, distance_matrix[v]

    def to_dot(self, filename=None, additional_edges=None):
        dot = graphviz.Graph()
        # Set styling
        dot.attr('node', shape='circle')
        dot.attr('edge')
        # Add nodes
        for i in range(self.degree):
            if self.node_degree(i) != 0:  # Do not show isolated nodes
                dot.node(str(i))
        # Add edges
        for i in range(self.degree):
            for j in range(i + 1, self.degree):
                if additional_edges is not None and ((i, j) in additional_edges or (j, i) in additional_edges):
                    dot.edge(str(i), str(j), color='red')
                if self.mat[i, j] != 0:
                    dot.edge(str(i), str(j), label=str(self.mat[i, j]))
        dot.render(view=True, cleanup=True, filename=filename)
        return dot

    def load_osmnx_graph(self, osmnx_graph):

        self.no_edge_value = 0
        self.degree = len(osmnx_graph.nodes)
        self.mat = np.full([self.degree, self.degree], self.no_edge_value)

        for (start_id, end_id, edge_data) in osmnx_graph.edges(data=True):
            if start_id == end_id:
                continue
            self.add_edge(start_id, end_id, edge_data['length'])
