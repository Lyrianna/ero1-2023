import datetime

import networkx as nx
import osmnx as ox
import osmnx.utils_graph
from datetime import datetime

from practical_app import directed_solver
import graph_rendering

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

    # graph = nx.MultiDiGraph()
    # # Example 1
    # graph.add_edge(0, 1, length=1)
    # graph.add_edge(0, 2, length=2)
    # graph.add_edge(1, 3, length=2)
    # graph.add_edge(1, 2, length=2)
    # graph.add_edge(2, 3, length=3)
    # graph.add_edge(3, 0, length=4)
    # # Exmple 2
    # graph.add_edge(0, 1, length=1)
    # graph.add_edge(1, 0, length=2)
    # graph.add_edge(1, 0, length=3)
    # graph.add_edge(1, 0, length=4)

    print('degree =', len(graph.nodes))

    print('Computing path...')
    t_start = datetime.now()
    path = directed_solver.optimal_path(graph)
    t_end = datetime.now()
    print('done. took in total:', t_end - t_start)
    print('path len =', len(path))

    graph_rendering.render_osmnx_path(graph, path, duration_between_steps=0.5, step_size=23, edge_width=0.5)


if __name__ == '__main__':
    main()
