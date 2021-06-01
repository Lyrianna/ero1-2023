import community.community_louvain
import networkx as nx
import osmnx as ox
from cdlib import algorithms


ox.config(use_cache=True, log_console=False)


def main():
    graph = ox.graph_from_place('Villejuif, France', network_type='drive')
    # graph = ox.graph_from_place('Montreal, Canada', network_type='drive')
    graph = nx.convert_node_labels_to_integers(graph)
    # graph = ox.get_undirected(graph)

    # odd_degree_nodes = [n for n, nbrs_dict in graph.adjacency() if len(nbrs_dict) % 2 != 0]
    # print(f'{len(odd_degree_nodes)} odd_degree_nodes =', odd_degree_nodes)

    # Villejuif, 10 was good (5 partitions)
    # partition = community.community_louvain.best_partition(graph, resolution=10)
    # print(partition)
    # node_colors = list(partition.values())

    # components = nx.algorithms.components.kosaraju_strongly_connected_components(graph)
    # node_colors = [0] * len(graph.nodes)
    # i = 0
    # for c in components:
    #     for node in c:
    #         node_colors[node] = i
    #     i += 1

    coms = algorithms.infomap(graph)
    print(coms)

    # ox.plot_graph(graph,
    #               node_size=1, node_zorder=2, node_color=c,
    #               edge_linewidth=0.1,
    #               show=False, close=True, save=True, filepath='output.png')


if __name__ == '__main__':
    main()
