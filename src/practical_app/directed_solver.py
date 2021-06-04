import sys
from datetime import datetime

import scipy
import scipy.sparse
import numpy as np
import networkx as nx


def path_from_pred_matrix(pred_matrix, u, v):
    path = []
    prev = v
    node = None
    path.append((node, prev))
    while node != u:
        node = pred_matrix[u, prev]
        path.append((node, prev))
        prev = node
    path.reverse()
    path.pop()  # remove trash node
    return path


def create_current_to_old_node_label_mapping(graph):
    mapping = {}
    for node, d in graph.nodes(data=True):
        mapping[node] = d['old_label']
    return mapping


def remap_path_labels(path, mapping):

    def remap_node(node):
        return mapping[node]

    for i in range(len(path)):
        u, v = path[i]
        path[i] = (remap_node(u), remap_node(v))

    return path


def optimal_path(graph):
    """
    Find the optimal path to traverse every edge in the graph using a minimum flow approach.

    Algorithm:

    - find imbalanced nodes that need out edges / in edges

    - create a bipartite graph connecting every need_out node to every need_in nodes

    - compute bipartite minimum weight full matching

    - build temporary eulerized graph by duplicating edges along best pairs of (need_out, need_in)
    nodes found during matching

    - reconstruct path

    :param graph: OSMNX MultiDiGraph, needs to be strongly connected
    :return: the optimal path
    """

    graph = nx.convert_node_labels_to_integers(graph, label_attribute='old_label')
    label_mapping = create_current_to_old_node_label_mapping(graph)

    if not nx.is_strongly_connected(graph):
        raise Exception('Graph is not strongly connected')

    if nx.is_eulerian(graph):
        print('Graph is already Eulerian!')
        return remap_path_labels(list(nx.algorithms.eulerian_circuit(graph)), label_mapping), 0

    n = len(graph.nodes)
    edges = [(u, v, d['length']) for u, v, d in graph.edges(data=True)]
    total_cost = 0

    # print('Building adjacency matrix and in/out sets')

    # Build adj matrix of original graph and find vertex deltas
    mat = np.zeros(shape=(n, n), dtype=np.float)
    delta = [0] * n

    for u, v, c in edges:
        total_cost += c
        if mat[u, v] == 0 or c < mat[u, v]:
            mat[u, v] = c
        delta[u] += 1
        delta[v] -= 1

    # Build need_in / need_out sets
    need_in = {}
    need_out = {}

    for i in range(n):
        if delta[i] < 0:
            need_out[i] = abs(delta[i])
        elif delta[i] > 0:
            need_in[i] = delta[i]

    # print('Computing shortest paths')

    # t_start = datetime.now()

    csr_mat = scipy.sparse.csr_matrix(mat)
    dist_matrix, predecessors = scipy.sparse.csgraph.shortest_path(csr_mat, return_predecessors=True)

    # t_end = datetime.now()
    # print('Done, took: ', t_end - t_start)

    # print('Creating bipartite graph')

    bipartite_g = nx.DiGraph()

    # Generate unique ids for each combinations
    for u, u_c in need_out.items():
        for i in range(u_c):
            for v, v_c in need_in.items():
                for j in range(v_c):
                    s = f'{u}_{i}'
                    e = f'{v}_{j}'
                    bipartite_g.add_edge(s, e, weight=dist_matrix[u, v])

    # print('Computing bipartite minimum weight full matching')

    matching = nx.algorithms.bipartite.matching.minimum_weight_full_matching(bipartite_g)

    def conv(label):
        """Convert custom matching label back to initial node"""
        return int(label.split('_')[0])

    # Convert to list
    matching = list((conv(k), conv(v)) for k, v in matching.items())

    # Convert unique ids back to original ids
    matching = [(u, v) for u, v in matching if u in need_out]  # Keep only valid edges (a -> b and not b -> a)

    eulerized_graph = nx.MultiDiGraph()

    for u, v, c in edges:
        eulerized_graph.add_edge(u, v, weight=c)

    additional_cost = 0

    # For reach matched pair, double up edges along their path
    for u, v in matching:

        # Reconstruct shortest path of the pair from predecessors matrix
        sp = path_from_pred_matrix(predecessors, u, v)

        # Add edges of path
        for i, j in sp:
            c = mat[i, j]
            additional_cost += c
            eulerized_graph.add_edge(i, j, weight=c)

    ratio = 100 * additional_cost / total_cost

    # print(f'Total city road length = {int(total_cost)}')
    # print(f'Additional travelled distance (already visited roads) = {int(additional_cost)}')
    # print(f'Ratio = {additional_cost}')

    final_path = list(nx.algorithms.eulerian_circuit(eulerized_graph))
    final_path = remap_path_labels(final_path, label_mapping)

    return final_path, ratio
