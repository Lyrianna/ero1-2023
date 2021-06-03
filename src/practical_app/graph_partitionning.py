import osmnx.utils_graph
from cdlib import algorithms

MAX_NB_OF_NODES = 15000


def split_graph(graph):

    # if len(graph.nodes) <= MAX_NB_OF_NODES:
    #     return [graph]

    final_graphs = []
    to_split = set()
    to_split.add(graph.copy())

    while len(to_split) > 0:

        # print('final graphs =', final_graphs)
        # print('to split =', to_split)

        g = to_split.pop()
        # print(f'g has {len(g.nodes)} nodes')

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

            # print(f'sub_g has {len(sub_g.nodes)} nodes')
            if len(sub_g.nodes) > MAX_NB_OF_NODES:
                to_split.add(sub_g)
            else:
                final_graphs.append(sub_g)

    return final_graphs
