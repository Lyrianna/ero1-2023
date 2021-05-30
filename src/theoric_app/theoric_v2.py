import itertools

from graph_adj_mat import GraphAdjMat
from graph import Graph
from multi_graph import MultiGraph
import edmonds
import euler
import utils

import gvanim
import imageio


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
    mat = [
        [ 0,  4,  0,  0,  0,  0,  0,  8,  0],
        [ 4,  0,  8,  0,  0,  0,  0, 11,  0],
        [ 0,  8,  0,  7,  0,  4,  0,  0,  2],
        [ 0,  0,  7,  0,  9,  0,  14,  0,  0],
        [ 0,  0,  0,  9,  0, 10,  0,  0,  0],
        [ 0,  0,  4,  0, 10,  0,  2,  0,  0],
        [ 0,  0,  0, 14,  0,  2,  0,  1,  6],
        [ 8, 11,  0,  0,  0,  0,  1,  0,  7],
        [ 0,  0,  2,  0,  0,  0,  6,  7,  0]
     ]
    # initial_graph = GraphAdjMat(6)
    # initial_graph.add_edges(edges)
    graph_initial = GraphAdjMat(mat=mat)
    print(graph_initial)
    # graph_initial.to_dot(filename='initial_graph')

    """Find odd degree nodes"""
    odd_degree_nodes = graph_initial.odd_degree_nodes()
    print('odd_degree_nodes =', odd_degree_nodes)

    """Compute all possible odd node pairs"""
    odd_node_pairs = list(itertools.combinations(odd_degree_nodes, 2))
    odd_node_pairs = [utils.normalize_pair(*p) for p in odd_node_pairs]
    print('odd_node_pairs =', odd_node_pairs)

    """Compute the minimum distance for every pair"""
    odd_node_pairs_shortest_distance = {}
    for pair in odd_node_pairs:
        path, dist = graph_initial.shortest_path(*pair)
        _, odd_node_pairs_shortest_distance[pair] = graph_initial.shortest_path(*pair)
        print(f'pair={pair} dist={dist}')

    """Create a complete graph of those pairs with the minimum distance as weight"""
    odd_node_pairs_list = [(*pair, dist) for pair, dist in odd_node_pairs_shortest_distance.items()]
    graph_odd_complete = Graph(odd_node_pairs_list)
    print(graph_odd_complete.edges)

    # graph_odd_complete.to_dot(filename='graph_odd_complete')

    """Compute the minimum weight matching"""
    min_weight_pairs = edmonds.min_weight_matching(graph_odd_complete)
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
            print(edge, 'exists')
            final_path.append(edge)
        else:
            real_path, _ = graph_initial.shortest_path(*edge)
            print(edge, 'replacing with', real_path)
            final_path += real_path

    print(final_path)

    """
    Render final path as a gif (optional)
    """
    ga = gvanim.Animation()
    for edge in graph_initial.edge_list():
        ga.add_edge(edge[0], edge[1])
    ga.next_step()

    visit_times = {}
    for edge in final_path:
        edge = utils.normalize_pair(*edge)
        visit_times[edge] = 0

    drawn_path = []

    def draw_path():
        for edge in drawn_path:
            if visit_times[edge] > 1:
                ga.highlight_edge(*edge, color='blue')
            else:
                ga.highlight_edge(*edge, color='green')

    for raw_edge in final_path:
        new_edge = utils.normalize_pair(*raw_edge)
        draw_path()
        ga.highlight_edge(*new_edge, color='red')
        drawn_path.append(new_edge)
        visit_times[new_edge] += 1
        ga.next_step()

    # Final result
    draw_path()
    ga.next_step()

    ga_graphs = ga.graphs()
    files = gvanim.render(ga_graphs, 'render/step', 'png', size=1000)
    print(files)
    with imageio.get_writer('render.gif', mode='I', duration=0.8) as writer:
        for file in files:
            image = imageio.imread(file)
            writer.append_data(image)


if __name__ == '__main__':
    main()
