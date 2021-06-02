import networkx as nx
import osmnx as ox
import osmnx.utils_graph
from cdlib import algorithms


ox.config(use_cache=True, log_console=False)

MAX_NB_OF_NODES = 15000


def split_graph(graph):

    final_graphs = []
    to_split = set()
    to_split.add(graph.copy())

    while len(to_split) > 0:

        print('final graphs =', final_graphs)
        print('to split =', to_split)

        g = to_split.pop()
        print(f'g has {len(g.nodes)} nodes')

        initial_nodes = set(g.nodes)
        community_map = algorithms.infomap(g).to_node_community_map()
        communities = {}

        for node, comm_ids in community_map.items():
            comm_id = comm_ids[0]
            comm_set = communities.get(comm_id, set())
            comm_set.add(node)
            communities[comm_id] = comm_set

        for comm_id, comm_set in communities.items():

            sub_g = g.copy()
            sub_g.remove_nodes_from(initial_nodes - comm_set)  # Remove nodes that are not in the community

            sub_g = osmnx.utils_graph.get_largest_component(sub_g, strongly=True)

            print(f'sub_g has {len(sub_g.nodes)} nodes')
            if len(sub_g.nodes) > MAX_NB_OF_NODES:
                to_split.add(sub_g)
            else:
                final_graphs.append(sub_g)

    return final_graphs


def main():
    # graph = ox.graph_from_place('Villejuif, France', network_type='drive')
    graph = ox.graph_from_place('Montreal, Canada', network_type='drive')
    graph = nx.convert_node_labels_to_integers(graph)

    sub_graphs = split_graph(graph)
    print('graphs of sizes ', [len(g) for g in sub_graphs])

    node_colors_dict = dict.fromkeys(graph.nodes)
    edge_colors_dict = dict.fromkeys(graph.edges)

    colors = ['darkviolet', 'blue', 'deeppink', 'lime', 'indigo', 'deepskyblue', 'green',
        'maroon', 'teal', 'yellow', 'fuchsia', 'gold', 'orange', 'aqua', 'red','mint']

    for i, g in enumerate(sub_graphs):
        color = colors[i % len(colors)]
        for node in g.nodes:
            node_colors_dict[node] = color
        for edge in g.edges:
            edge_colors_dict[edge] = color

    node_colors = [node_colors_dict.get(node, 0) for node in graph.nodes]
    edge_colors = [edge_colors_dict.get(edge, 0) for edge in graph.edges]

    edge_colors = [c if c is not None else 'white' for c in edge_colors]

    print(f'{len(sub_graphs)} sub graphs', [nx.is_strongly_connected(g) for g in sub_graphs])

    ox.plot_graph(graph,
                  node_size=0, node_zorder=2, node_color=node_colors,
                  edge_linewidth=0.1,  edge_color=edge_colors,
                  show=False, close=True, save=True, filepath='output.png')


if __name__ == '__main__':
    main()
