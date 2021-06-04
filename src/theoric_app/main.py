import itertools
import os
import sys
import time
import numpy
import scipy.sparse
from datetime import datetime
from scipy.sparse.csgraph import shortest_path

from graph_adj_mat import GraphAdjMat
from graph import Graph
from multi_graph import MultiGraph
import graph_rendering
import edmonds
import euler
import utils

import networkx as nx
import osmnx as ox

ox.config(use_cache=True, log_console=False)


def main():
    # """Manually create a graph"""
    # edges = [  # 6 nodes
    #     (0, 1, 1),
    #     (0, 2, 1),
    #     (0, 3, 1),
    #     (1, 4, 1),
    #     (2, 4, 1),
    #     (4, 5, 1),
    # ]
    # initial_graph = GraphAdjMat(6)
    # initial_graph.add_edges(edges)

    # mat = [
    #     [ 0,  4,  0,  0,  0,  0,  0,  8,  0],
    #     [ 4,  0,  8,  0,  0,  0,  0, 11,  0],
    #     [ 0,  8,  0,  7,  0,  4,  0,  0,  2],
    #     [ 0,  0,  7,  0,  9,  0,  14,  0,  0],
    #     [ 0,  0,  0,  9,  0, 10,  0,  0,  0],
    #     [ 0,  0,  4,  0, 10,  0,  2,  0,  0],
    #     [ 0,  0,  0, 14,  0,  2,  0,  1,  6],
    #     [ 8, 11,  0,  0,  0,  0,  1,  0,  7],
    #     [ 0,  0,  2,  0,  0,  0,  6,  7,  0]
    #  ]
    # graph_initial = GraphAdjMat(mat=mat)

    # osmnx_graph = ox.graph_from_place('Arracourt, France', network_type='drive')
    osmnx_graph = ox.graph_from_place('Villejuif, France', network_type='drive')
    # osmnx_graph = ox.graph_from_place('Montreal, Canada', network_type='drive')
    osmnx_graph = nx.convert_node_labels_to_integers(osmnx_graph)
    graph_initial = GraphAdjMat()
    graph_initial.load_osmnx_graph(osmnx_graph)

    print('graph degree =', graph_initial.degree)
    print(graph_initial)
    # graph_initial.to_dot(filename='initial_graph')

    """Create ajd list graph for later"""
    graph_augmented = MultiGraph(edges=graph_initial.edge_list())

    """Find odd degree nodes"""
    odd_degree_nodes = graph_augmented.odd_degree_nodes()

    print(f'{len(odd_degree_nodes)} odd_degree_nodes =', odd_degree_nodes)

    """Compute all possible odd node pairs"""
    odd_node_pairs = list(itertools.combinations(odd_degree_nodes, 2))
    odd_node_pairs = [utils.normalize_pair(*p) for p in odd_node_pairs]
    print(f'{len(odd_node_pairs)} odd node pairs')

    """Compute the minimum distance for every pair"""
    csr_mat = scipy.sparse.csr_matrix(graph_initial.mat)
    print('computing odd node pairs shortest paths')
    tstart = datetime.now()
    dist_matrix = shortest_path(csr_mat, directed=False, return_predecessors=False)  # Dist matrix of the whole graph
    tend = datetime.now()
    print('done, took', tend - tstart)

    odd_node_pairs_distance_list = []  # (u, v, d)
    print('assigning each pair its min distance')
    for pair in odd_node_pairs:
        u, v = pair
        odd_node_pairs_distance_list.append((u, v, dist_matrix[u, v]))
    print('done')

    """Create a complete graph of those pairs with the minimum distance as weight"""
    graph_odd_complete = Graph(odd_node_pairs_distance_list)
    # print(graph_odd_complete.edges)

    # graph_odd_complete.to_dot(filename='graph_odd_complete')

    """Compute the minimum weight matching"""
    print('computing minimum weight matching')
    tstart = datetime.now()
    min_weight_pairs = edmonds.min_weight_matching(graph_odd_complete)
    tend = datetime.now()
    print('done, took', tend - tstart)
    print(f'{len(min_weight_pairs)} min_weight_pairs =', min_weight_pairs)

    # graph_initial.to_dot(filename='graph_initial_with_minimum_weight_matching', additional_edges=min_weight_pairs)

    """Built up the augmented graph (initial graph + "fake" edges between the pairs found in previous computation)"""
    for pair in min_weight_pairs:
        u, v = utils.normalize_pair(*pair)
        dist = dist_matrix[u, v]
        graph_augmented.add_edge(*pair, dist)

    # print(graph_augmented)
    # graph_augmented.to_dot(filename='graph_augmented')

    """Get a naive path (naive because it uses the previous fakes edges)"""
    naive_euler_circuit = list(euler.eulerian_circuit(graph_augmented))
    print(naive_euler_circuit)

    """Create the real final path by replacing the fake edges with the shortest possible path"""
    final_path = []
    for edge in naive_euler_circuit:
        if graph_initial.has_edge(*edge):
            # print(edge, 'exists')
            final_path.append(edge)
        else:
            real_path, _ = graph_initial.shortest_path(csr_mat, *edge)
            # print(edge, 'replacing with', real_path)
            final_path += real_path

    print(final_path)

    # graph_rendering.render_path_as_gif(graph_initial.edge_list(), final_path)

    # graph_rendering.render_osmnx_path(osmnx_graph, final_path, step_size=23)

    # graph_rendering.render_osmnx_path(osmnx_graph, final_path, step_size=18, edge_width=0.5)
    graph_rendering.render_osmnx_path(osmnx_graph, final_path, duration_between_steps=0.1, step_size=5, edge_width=0.5)


if __name__ == '__main__':
    main()
