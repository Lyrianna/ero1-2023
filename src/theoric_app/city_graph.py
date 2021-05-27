class Edge:

    def __init__(self, length, initial_pheromone_value):
        self.length = length
        # Subject to change, use a dictionary of values instead?
        self.pheromone_value = initial_pheromone_value
        self.visited = False

    def __str__(self):
        return f'length={self.length:.3f}, pheromone={self.pheromone_value:.5f}, visited={self.visited}'


# class Neighbour:
#
#     def __init__(self, node, connecting_edge):
#         self.node = node
#         self.edge = connecting_edge
#
#     def __str__(self):
#         return f'(id:{self.node.id}: {self.edge})'
#

class Node:

    def __init__(self, node_id):
        self.id = node_id
        self.neighbours = {}

    def add_neighbour(self, neighbour_id, edge):
        self.neighbours[neighbour_id] = edge

    def get_neighbouring_unvisited_paths(self):
        paths = []
        # ...
        # TODO
        # ...
        return paths

    def __str__(self):
        return f'id:{self.id} -> {[f"(id:{k} {v})" for (k, v) in self.neighbours.items()]}'


class CityGraph:

    def __init__(self, osmnx_graph):
        self.degree = len(osmnx_graph.nodes())
        self.nodes = {}  # Dictionary indexed on (node_id)
        self.edges = []
        # self.edges = {}  # Dictionary indexed on (a_node_id, b_node_id) or (b_node_id, a_node_id)
        self.setup(osmnx_graph)

    def add_node(self, node_id):
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id)
        return self.nodes[node_id]

    def add_edge(self, length):
        # if (start_id, end_id) in self.edges:
        #     return self.edges[(start_id, end_id)]
        # elif (end_id, start_id) in self.edges:
        #     return self.edges[(end_id, start_id)]
        # else:
        #     self.edges[(start_id, end_id)] = new_edge
        new_edge = Edge(length, 1.0 / self.degree)
        self.edges.append(new_edge)
        return new_edge

    def setup(self, osmnx_graph):

        for (start_id, end_id, edge_data) in osmnx_graph.edges(data=True):

            edge = self.add_edge(edge_data['length'])

            start_node = self.add_node(start_id)
            end_node = self.add_node(end_id)

            start_node.add_neighbour(end_id, edge)
            if not edge_data['oneway']:
                end_node.add_neighbour(start_id, edge)
