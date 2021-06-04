import osmnx.utils_graph
from cdlib import algorithms


def split_graph(graph, max_nodes_per_sub_graph=10000):
    """
    Split a given graph into subgraphs using infomap's community detection algorithm

    :param graph: OSMNX graph to split
    :param max_nodes_per_sub_graph:
    :return:
    """

    if len(graph.nodes) <= max_nodes_per_sub_graph:
        return [graph]

    final_graphs = []
    to_split = set()
    to_split.add(graph.copy())

    while len(to_split) > 0:

        g = to_split.pop()

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

            if len(sub_g.nodes) > max_nodes_per_sub_graph:
                to_split.add(sub_g)
            else:
                final_graphs.append(sub_g)

    return final_graphs
