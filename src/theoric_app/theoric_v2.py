import itertools

import numpy
import scipy.sparse
from datetime import datetime

from graph_adj_mat import GraphAdjMat
from graph import Graph
from multi_graph import MultiGraph
import edmonds
import euler
import utils

import gvanim
import imageio

import networkx as nx
import osmnx as ox


def render_path_as_gif(initial_graph_edges, path, img_size=1000, duration_between_steps=0.8, edge_batch_size=1):
    """
    Render final path as a gif (optional)
    """
    ga = gvanim.Animation()
    for edge in initial_graph_edges:
        ga.add_edge(edge[0], edge[1])
    ga.next_step()

    visit_times = {}
    for edge in path:
        edge = utils.normalize_pair(*edge)
        visit_times[edge] = 0

    drawn_path = []

    def draw_path():
        for edge in drawn_path:
            if visit_times[edge] > 1:
                ga.highlight_edge(*edge, color='blue')
            else:
                ga.highlight_edge(*edge, color='green')

    # for raw_edge in path:
    #     new_edge = utils.normalize_pair(*raw_edge)
    #     draw_path()
    #     ga.highlight_edge(*new_edge, color='red')
    #     drawn_path.append(new_edge)
    #     visit_times[new_edge] += 1
    #     ga.next_step()

    cs = edge_batch_size  # Chunk size to process paths by
    for chunk in [path[cs*i:cs*(i+1)] for i in range(len(path) // cs + 1)]:
        for raw_edge in chunk:
            new_edge = utils.normalize_pair(*raw_edge)
            drawn_path.append(new_edge)
            visit_times[new_edge] += 1
        draw_path()
        ga.highlight_edge(*drawn_path[-1], color='red')  # Mark last visited edge in red
        ga.next_step()

    # Final result
    draw_path()
    ga.next_step()

    ga_graphs = ga.graphs()
    files = gvanim.render(ga_graphs, 'render/step', 'png', size=img_size)
    print(files)
    with imageio.get_writer('render.gif', mode='I', duration=duration_between_steps) as writer:
        for file in files:
            image = imageio.imread(file)
            writer.append_data(image)


def render_osmnx_path(osmnx_graph, edge_path):
    path = [edge[0] for edge in edge_path]
    path.append(edge_path[0][0])
    print(path)
    ox.plot_graph_route(osmnx_graph, route=path, route_color='r', route_linewidth=3, orig_dest_size=30,
                        node_size=2, save=True, filepath=f'output.png', dpi=1000)


def main():

    """Manually create a graph"""
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

    osmnx_graph = ox.graph_from_place('Villejuif, France', network_type='drive')
    osmnx_graph = nx.convert_node_labels_to_integers(osmnx_graph)
    graph_initial = GraphAdjMat()
    graph_initial.load_osmnx_graph(osmnx_graph)

    print('graph degree =', graph_initial.degree)
    print(graph_initial)
    # graph_initial.to_dot(filename='initial_graph')

    """Find odd degree nodes"""
    odd_degree_nodes = graph_initial.odd_degree_nodes()
    print(f'{len(odd_degree_nodes)} odd_degree_nodes =', odd_degree_nodes)

    """Compute all possible odd node pairs"""
    odd_node_pairs = list(itertools.combinations(odd_degree_nodes, 2))
    odd_node_pairs = [utils.normalize_pair(*p) for p in odd_node_pairs]
    # print('odd_node_pairs =', odd_node_pairs)
    print(f'{len(odd_node_pairs)} odd_node_pairs')

    """Compute the minimum distance for every pair"""
    odd_node_pairs_shortest_distance = {}
    csr_mat = scipy.sparse.csr_matrix(graph_initial.mat)
    print('computing odd node pairs shortest paths')
    tstart = datetime.now()
    print(tstart)
    for pair in odd_node_pairs:
        _, odd_node_pairs_shortest_distance[pair] = GraphAdjMat.shortest_path(csr_mat, *pair)
        # print(f'pair={pair} dist={dist}')
    tend = datetime.now()
    print(tend)
    print('done, took', tend - tstart)

    """Create a complete graph of those pairs with the minimum distance as weight"""
    odd_node_pairs_list = [(*pair, dist) for pair, dist in odd_node_pairs_shortest_distance.items()]
    graph_odd_complete = Graph(odd_node_pairs_list)
    # print(graph_odd_complete.edges)

    # graph_odd_complete.to_dot(filename='graph_odd_complete')

    """Compute the minimum weight matching"""
    print('computing minimum weight matching')
    tstart = datetime.now()
    print(tstart)
    min_weight_pairs = edmonds.min_weight_matching(graph_odd_complete)
    tend = datetime.now()
    print(tend)
    print('done, took', tend - tstart)
    print('min_weight_pairs =', min_weight_pairs)

    # graph_initial.to_dot(filename='graph_initial_with_minimum_weight_matching', additional_edges=min_weight_pairs)

    """Built up the augmented graph (initial graph + "fake" edges between the pairs found in previous computation)"""
    graph_augmented = MultiGraph(edges=graph_initial.edge_list())
    for pair in min_weight_pairs:
        pair = utils.normalize_pair(*pair)
        graph_augmented.add_edge(*pair, odd_node_pairs_shortest_distance[pair])

    print(graph_augmented)
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

    render_path_as_gif(graph_initial.edge_list(), final_path, img_size=6880, duration_between_steps=1, edge_batch_size=10)
    # render_osmnx_path(osmnx_graph, final_path)


if __name__ == '__main__':
    main()
