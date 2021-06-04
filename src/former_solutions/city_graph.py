"""

Class Edge

"""


class Edge:

    def __init__(self, length, initial_pheromone_value):
        self.length = length
        # Subject to change, use a dictionary of values instead?
        self.pheromone = initial_pheromone_value

    def spread_pheromone(self):
        self.pheromone += 1.0 / self.length

    def __str__(self):
        return f'length={self.length:.3f}, pheromone={self.pheromone:.5f}'


"""

Class Neighbour

"""


class Neighbour:

    def __init__(self, node, connecting_edge):
        self.node = node
        self.edge = connecting_edge

    def __str__(self):
        return f'(id:{self.node.id}: {self.edge})'


"""

Class Node

"""


class Node:

    def __init__(self, node_id):
        self.id = node_id
        self.neighbours = {}

    def add_neighbour(self, neighbour_node, connecting_edge):
        self.neighbours[neighbour_node.id] = Neighbour(neighbour_node, connecting_edge)

    def __str__(self):
        return f'id:{self.id} -> {[f"(id:{n_id} {neighbour.edge})" for (n_id, neighbour) in self.neighbours.items()]}'


"""

Class Path

"""


class Path:

    def __init__(self, start_node=None):
        self.length = 0
        self.pheromone = 1
        if start_node is not None:
            self.nodes = [start_node]
        else:
            self.nodes = []

    def copy(self):
        new_path = Path()
        new_path.nodes = self.nodes.copy()
        new_path.length = self.length
        return new_path

    def add_node(self, node, edge):
        self.nodes.append(node)
        self.length += edge.length
        self.pheromone *= edge.pheromone

    def concat_with(self, path):
        self.nodes.extend(path.nodes[1:])  # Remove first element of path?
        self.length += path.length
        self.pheromone *= path.pheromone

    def to_id_path(self):
        return [node.id for node in self.nodes]

    def to_pair_id_path(self):
        path = []
        prev = None
        for node in self.nodes:
            if prev is None:
                prev = node
                continue
            path.append((prev.id, node.id))
            prev = node
        return path

    def is_empty(self):
        return len(self.nodes) == 0

    def __str__(self):
        return f'len={self.length} {[str(n.id) for n in self.nodes]}'


"""

Class CityGraph

"""


class CityGraph:

    def __init__(self, osmnx_graph):
        self.degree = len(osmnx_graph.nodes())
        self.nodes = {}  # Dictionary indexed on (node_id)
        self.edges = []
        self.setup(osmnx_graph)

    def add_node(self, node_id):
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id)
        return self.nodes[node_id]

    def add_edge(self, length):
        new_edge = Edge(length, 1.0 / self.degree)
        self.edges.append(new_edge)
        return new_edge

    def setup(self, osmnx_graph):

        for (start_id, end_id, edge_data) in osmnx_graph.edges(data=True):

            edge = self.add_edge(edge_data['length'])

            start_node = self.add_node(start_id)
            end_node = self.add_node(end_id)

            start_node.add_neighbour(end_node, edge)
            if not edge_data['oneway']:
                end_node.add_neighbour(start_node, edge)
