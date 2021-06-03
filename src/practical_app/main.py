import datetime

import networkx as nx
import osmnx as ox
import osmnx.utils_graph
from datetime import datetime

import directed_solver

ox.config(use_cache=True, log_console=False)


def main():
    # graph = ox.graph_from_place('Montreal, Canada', network_type='drive')
    graph = ox.graph_from_place('Villejuif, France', network_type='drive')
    # graph = ox.graph_from_place('Arracourt, France', network_type='drive')
    # graph = ox.graph_from_place('Arbois, France', network_type='drive')
    # graph = ox.graph_from_place('Arras-en-Lavedan, France', network_type='drive')
    # graph = ox.graph_from_place('Diou, France', network_type='drive')
    # graph = ox.graph_from_place('Palaiseau, France', network_type='drive')

    graph = ox.utils_graph.get_largest_component(graph, strongly=True)
    graph = nx.convert_node_labels_to_integers(graph)

    print('Graph degree =', len(graph.nodes))
    print('Number of edges =', len(graph.edges))

    print('Computing path...')
    t_start = datetime.now()
    path, ratio = directed_solver.optimal_path(graph)
    t_end = datetime.now()
    print('Done, took in total:', t_end - t_start)
    print('Path length =', len(path))
    print(f'Ratio = {ratio:.2f}% (additionally covered distance compared to initial total road length)')
    print(path)

    # graph_rendering.render_osmnx_path(graph, path, duration_between_steps=0.3, step_size=1000, edge_width=0.1)
    # graph_rendering.render_osmnx_path(graph, path, duration_between_steps=0.3, step_size=50, edge_width=0.5)


if __name__ == '__main__':
    main()
