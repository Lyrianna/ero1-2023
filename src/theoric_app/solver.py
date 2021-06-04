import itertools
import scipy.sparse
from scipy.sparse.csgraph import shortest_path
from datetime import datetime

from graph import Graph
import multi_graph
import edmonds
import euler
import utils


def solve(initial_graph):

    """Create ajd list graph for later"""
    euler_graph = multi_graph.MultiGraph(edges=initial_graph.edge_list())

    """Find odd degree nodes"""
    odd_degree_nodes = euler_graph.odd_degree_nodes()

    print(f'{len(odd_degree_nodes)} odd_degree_nodes =', odd_degree_nodes)

    """Compute all possible odd node pairs"""
    odd_node_pairs = list(itertools.combinations(odd_degree_nodes, 2))
    odd_node_pairs = [utils.normalize_pair(*p) for p in odd_node_pairs]
    print(f'{len(odd_node_pairs)} odd node pairs')

    """Compute the minimum distance for every pair"""
    print('computing odd node pairs shortest paths...')
    tstart = datetime.now()
    csr_mat = scipy.sparse.csr_matrix(initial_graph.mat)
    dist_matrix = shortest_path(csr_mat, directed=False, return_predecessors=False)  # Dist matrix of the whole graph
    tend = datetime.now()
    print('done, took', tend - tstart)

    odd_node_pairs_distance_list = []  # (u, v, d)
    for pair in odd_node_pairs:
        u, v = pair
        odd_node_pairs_distance_list.append((u, v, dist_matrix[u, v]))

    """Create a complete graph of those pairs with the minimum distance as weight"""
    print('creating euler graph')
    graph_odd_complete = Graph(odd_node_pairs_distance_list)

    """Compute the minimum weight matching"""
    print('computing minimum weight matching...')
    tstart = datetime.now()
    min_weight_pairs = edmonds.min_weight_matching(graph_odd_complete)
    tend = datetime.now()
    print('done, took', tend - tstart)
    print(f'{len(min_weight_pairs)} min_weight_pairs =', min_weight_pairs)

    """Built up the euleur graph (initial graph + "fake" edges between the pairs found in previous computation)"""
    for pair in min_weight_pairs:
        u, v = utils.normalize_pair(*pair)
        dist = dist_matrix[u, v]
        euler_graph.add_edge(*pair, dist)

    """Get a naive path (naive because it uses the previous fakes edges)"""
    naive_euler_circuit = list(euler.eulerian_circuit(euler_graph))
    print(naive_euler_circuit)

    """Create the real final path by replacing the fake edges with the shortest possible path"""
    final_path = []
    for edge in naive_euler_circuit:
        if initial_graph.has_edge(*edge):
            final_path.append(edge)
        else:
            real_path, _ = initial_graph.shortest_path(csr_mat, *edge)
            final_path += real_path

    return final_path
