import datetime
import sys
from datetime import datetime

import networkx as nx
import osmnx as ox
import osmnx.utils_graph

import directed_solver
import graph_partitionning
import graph_rendering

ox.config(use_cache=True, log_console=False)


def main():
    if len(sys.argv) < 3:
        print("Usage : python ./main [city, country] [type of road to clear the snow from]")
    """Load main graph"""
    graph = ox.graph_from_place(sys.argv[1], network_type=sys.argv[2])
    # graph = ox.graph_from_place('Villejuif, France', network_type='drive')
    # graph = ox.graph_from_place('Arracourt, France', network_type='drive')
    # graph = ox.graph_from_place('Arbois, France', network_type='drive')
    # graph = ox.graph_from_place('Arras-en-Lavedan, France', network_type='drive')
    # graph = ox.graph_from_place('Diou, France', network_type='drive')
    # graph = ox.graph_from_place('Palaiseau, France', network_type='drive')

    graph = ox.utils_graph.get_largest_component(graph, strongly=True)
    graph = nx.convert_node_labels_to_integers(graph)

    print('Graph degree =', len(graph.nodes))
    print('Number of edges =', len(graph.edges))

    sub_graphs = graph_partitionning.split_graph(graph)
    print(f'({len(sub_graphs)}) sub graphs of sizes {[len(g) for g in sub_graphs]}')

    paths = []
    for g in sub_graphs:
        print('Computing path...')
        t_start = datetime.now()
        path, ratio = directed_solver.optimal_path(g)
        t_end = datetime.now()
        print('Done, took in total:', t_end - t_start)
        print('Path length =', len(path))
        print(f'Ratio = {ratio:.2f}% (additionally covered distance compared to initial total road length)')
        print()
        paths.append(path)

    graph_rendering.render_path_or_paths(graph, paths=paths, duration_between_steps=0.3, step_size=200, edge_width=0.1)


if __name__ == '__main__':
    main()