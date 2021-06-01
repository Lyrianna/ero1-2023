import networkx as nx
import osmnx as ox
from cdlib import algorithms


ox.config(use_cache=True, log_console=False)


def main():
    # graph = ox.graph_from_place('Villejuif, France', network_type='drive')
    graph = ox.graph_from_place('Montreal, Canada', network_type='drive')
    graph = nx.convert_node_labels_to_integers(graph)

    coms = algorithms.infomap(graph)
    community_map = coms.to_node_community_map()
    node_colors = [community_map[node] for node in graph.nodes]

    ox.plot_graph(graph,
                  node_size=1, node_zorder=2, node_color=node_colors,
                  edge_linewidth=0.1,
                  show=False, close=True, save=True, filepath='output.png')


if __name__ == '__main__':
    main()
