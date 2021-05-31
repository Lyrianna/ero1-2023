import itertools
import os
import sys
import time
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


def render_path_as_gif(initial_graph_edges, path,
                       img_size=1000, duration_between_steps=0.8, edge_batch_size=1):
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
                ga.highlight_edge(*edge, color='red')

    # for raw_edge in path:
    #     new_edge = utils.normalize_pair(*raw_edge)
    #     draw_path()
    #     ga.highlight_edge(*new_edge, color='red')
    #     drawn_path.append(new_edge)
    #     visit_times[new_edge] += 1
    #     ga.next_step()

    cs = edge_batch_size  # Chunk size to process paths by
    for chunk in [path[cs * i:cs * (i + 1)] for i in range(len(path) // cs + 1)]:
        for raw_edge in chunk:
            new_edge = utils.normalize_pair(*raw_edge)
            drawn_path.append(new_edge)
            visit_times[new_edge] += 1
        draw_path()
        ga.highlight_edge(*drawn_path[-1], color='yellow')  # Mark last visited edge in red
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


# def convert_osmnx_geo_coords_to_image_coords(osmnx_graph):
#     def keep_significant(value):
#         return int(str(int(value * 10000000))[2:])
#
#     node_coords = {}
#     min_c = sys.maxsize, sys.maxsize
#     max_c = 0, 0
#     for node_id, data in osmnx_graph.nodes(data=True):
#         x, y = keep_significant(data['x']), keep_significant(data['y'])
#         node_coords[node_id] = (x, y)
#         min_c = (min(min_c[0], x), min(min_c[1], y))
#         max_c = (max(max_c[0], x), max(max_c[1], y))
#         # print(node_id, '->', (x, y), (data['x'], data['y']))
#
#     # print('min_x =', min_c[0], 'min_y =', min_c[1])
#     # print('max_x =', max_c[0], 'max_y =', max_c[1])
#
#     # diff = (max_c[0] - min_c[0], max_c[1] - min_c[1])
#     # ratio = diff[0] / diff[1]
#     # print('diff =', diff)
#     # print('ratio =', ratio)
#
#     for node_id, coords in node_coords.items():
#         new_coords = (coords[0] - min_c[0], coords[1] - min_c[1])
#         new_coords = (new_coords[0] / 100, new_coords[1] / 100)
#         node_coords[node_id] = new_coords
#         # print(node_id, '->', new_coords)
#
#     return node_coords


def render_osmnx_path(osmnx_graph, edge_path, duration_between_steps=0.5, step_size=1):

    time_stamp = int(time.time())
    output_dir = f'render_files_{time_stamp}'
    os.makedirs(output_dir)

    visit_times = {}
    for edge in edge_path:
        visit_times[utils.normalize_pair(*edge)] = 0

    def get_edge_color(path, u, v, highlight_last=False):
        if highlight_last and ((u, v) == path[-1] or (v, u) == path[-1]):  # Highlight last visited edge
            return 'yellow'
        if visit_times.get(utils.normalize_pair(u, v), 0) > 1:  # Already visited edge
            return 'blue'
        if (u, v) in path or (v, u) in path:  # Visited edge
            return 'red'
        return 'w'

    def get_edge_colors(path, highlight_last=False):
        return [get_edge_color(path, u, v, highlight_last) for (u, v) in osmnx_graph.edges()]

    files = []

    def render_path(path, filename, highlight_last=False):
        edge_colors = get_edge_colors(path, highlight_last)
        ox.plot_graph(osmnx_graph, node_color='w', node_edgecolor='k', node_size=5, node_zorder=3,
                      edge_color=edge_colors, edge_linewidth=1,
                      show=False, close=True, save=True, filepath=filename)
        files.append(filename)

    # # Render step by step
    # for i in range(len(edge_path)):
    #     current_path = edge_path[:(i + 1)]
    #     render_path(current_path, f'{output_dir}/step_{i:05}.png', highlight_last=True)
    #     visit_times[utils.normalize_pair(*edge_path[i])] += 1  # Update last visited pair

    # Render by big steps
    for i in range(len(edge_path) // step_size + 1):
        start_i, end_i = step_size * i, step_size * (i + 1)
        current_path = edge_path[:end_i]
        render_path(current_path, f'{output_dir}/step_{i:05}.png', highlight_last=True)
        for edge in edge_path[start_i:end_i]:
            visit_times[utils.normalize_pair(*edge)] += 1

    # Render final step
    render_path(edge_path, f'{output_dir}/step_{len(edge_path)}.png')

    print(files)

    # Render final gif
    with imageio.get_writer(f'osmnx_render_{time_stamp}.gif', mode='I', duration=duration_between_steps) as writer:
        for file in files:
            image = imageio.imread(file)
            writer.append_data(image)

    print(output_dir)


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

    # osmnx_graph = ox.graph_from_place('Arracourt, France', network_type='drive')
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
    print(f'{len(odd_node_pairs)} odd node pairs')

    """Compute the minimum distance for every pair"""
    odd_node_pairs_shortest_distance = {}
    csr_mat = scipy.sparse.csr_matrix(graph_initial.mat)
    print('computing odd node pairs shortest paths')
    tstart = datetime.now()
    for pair in odd_node_pairs:
        _, odd_node_pairs_shortest_distance[pair] = GraphAdjMat.shortest_path(csr_mat, *pair)
        # print(f'pair={pair} dist={dist}')
    tend = datetime.now()
    print('done, took', tend - tstart)

    """Create a complete graph of those pairs with the minimum distance as weight"""
    odd_node_pairs_list = [(*pair, dist) for pair, dist in odd_node_pairs_shortest_distance.items()]
    graph_odd_complete = Graph(odd_node_pairs_list)
    # print(graph_odd_complete.edges)

    # graph_odd_complete.to_dot(filename='graph_odd_complete')

    """Compute the minimum weight matching"""
    print('computing minimum weight matching')
    tstart = datetime.now()
    min_weight_pairs = edmonds.min_weight_matching(graph_odd_complete)
    tend = datetime.now()
    print('done, took', tend - tstart)
    print('min_weight_pairs =', min_weight_pairs)

    # graph_initial.to_dot(filename='graph_initial_with_minimum_weight_matching', additional_edges=min_weight_pairs)

    """Built up the augmented graph (initial graph + "fake" edges between the pairs found in previous computation)"""
    graph_augmented = MultiGraph(edges=graph_initial.edge_list())
    for pair in min_weight_pairs:
        pair = utils.normalize_pair(*pair)
        graph_augmented.add_edge(*pair, odd_node_pairs_shortest_distance[pair])

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

    # render_path_as_gif(graph_initial.edge_list(), final_path)

    render_osmnx_path(osmnx_graph, final_path, step_size=23)


if __name__ == '__main__':
    main()
