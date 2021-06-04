import graph_adj_mat
# import networkx as nx
# import osmnx as ox
# ox.config(use_cache=True, log_console=False)
import graph_rendering
import solver


def main():
    """Manually create a graph"""
    mat = [
        [0, 4, 0, 0, 0, 0, 0, 8, 0],
        [4, 0, 8, 0, 0, 0, 0, 11, 0],
        [0, 8, 0, 7, 0, 4, 0, 0, 2],
        [0, 0, 7, 0, 9, 0, 14, 0, 0],
        [0, 0, 0, 9, 0, 10, 0, 0, 0],
        [0, 0, 4, 0, 10, 0, 2, 0, 0],
        [0, 0, 0, 14, 0, 2, 0, 1, 6],
        [8, 11, 0, 0, 0, 0, 1, 0, 7],
        [0, 0, 2, 0, 0, 0, 6, 7, 0]
    ]
    graph_initial = graph_adj_mat.GraphAdjMat(mat=mat)

    # osmnx_graph = ox.graph_from_place('Villejuif, France', network_type='drive')
    # osmnx_graph = ox.graph_from_place('Montreal, Canada', network_type='drive')
    # osmnx_graph = nx.convert_node_labels_to_integers(osmnx_graph)
    # graph_initial = graph_adj_mat.GraphAdjMat()
    # graph_initial.load_osmnx_graph(osmnx_graph)

    print('graph degree =', graph_initial.degree)
    print(graph_initial)
    # graph_initial.to_dot(filename='graph_initial')

    final_path = solver.solve(graph_initial)
    print('path of length =', len(final_path))
    print('path =', final_path)
    graph_rendering.render_path_as_gif(graph_initial.edge_list(), final_path)


# graph_rendering.render_osmnx_path(osmnx_graph, final_path, step_size=23)
# graph_rendering.render_osmnx_path(osmnx_graph, final_path, step_size=18, edge_width=0.5)
# graph_rendering.render_osmnx_path(osmnx_graph, final_path, duration_between_steps=0.1, step_size=5, edge_width=0.5)


if __name__ == '__main__':
    main()
