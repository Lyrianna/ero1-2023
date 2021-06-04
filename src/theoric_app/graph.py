import graphviz
import utils


class Node:

    def __init__(self, node_id):
        self.id = node_id
        self.neighbours = []

    def add_neighbour(self, neighbour_node):
        self.neighbours.append(neighbour_node.id)

    def __str__(self):
        return f'id:{self.id} -> {self.neighbours}'


class Graph:

    """
    Undirected ! (u,v) == (v,u) !
    Args:
        edges: list of edge (u, v, w)
    """
    def __init__(self, edges):
        self.degree = 0
        self.nodes = {}  # Dictionary indexed on (node_id)
        self.edges = {}  # Dictionary indexed on (u, v) with u < v
        if edges is not None:
            for edge in edges:
                self.add_edge(*edge)

    def __str__(self):
        result = 'Graph {\n'
        for node_id, node in self.nodes.items():
            result += '  ' + str(node) + '\n'
        result += '}'
        return result

    def to_dot(self, filename=None):
        dot = graphviz.Graph()
        # Set styling
        dot.attr('node', shape='circle')
        dot.attr('edge')
        # Add nodes
        for node_id in self.nodes:
            dot.node(str(node_id))
        # Add edges
        for pair, dist in self.edges.items():
            dot.edge(str(pair[0]), str(pair[1]), label=str(dist))
        dot.render(view=True, cleanup=True, filename=filename)
        return dot

    def add_node(self, node_id):
        if node_id not in self.nodes:
            new_node = Node(node_id)
            self.degree += 1
            self.nodes[node_id] = new_node
            return new_node
        return self.nodes[node_id]

    def remove_node(self, node_id):
        node = self.nodes.get(node_id)
        if node is None:
            return
        for neighbour_id, neighbour in node.neighbours.items():
            del neighbour.node.neighbours[node_id]  # Remove neighbours ref to this node
            self.edges.pop(utils.normalize_pair(node_id, neighbour_id), None)  # Remove the edge from the graph
        self.degree -= 1
        del self.nodes[node_id]

    def has_edge(self, u, v):
        return utils.normalize_pair(u, v) in self.edges

    def get_edge(self, u, v):  # No checks!
        return self.edges[utils.normalize_pair(u, v)]

    def add_edge(self, u, v, weight):  # Undirected for now

        # Get (or create if necessary) the two nodes
        start_node = self.add_node(u)
        end_node = self.add_node(v)

        # Link the two nodes
        start_node.add_neighbour(end_node)
        end_node.add_neighbour(start_node)

        key = utils.normalize_pair(u, v)
        self.edges[key] = weight

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(*edge)

    def remove_edge(self, u, v):

        # Check if edge actually exists
        key = utils.normalize_pair(u, v)
        edge = self.edges.pop(key, None)
        if edge is None:
            return

        # If so, remove link between each node
        del self.nodes[u].neighbours[v]  # Remove neighbouring ref u -> v
        del self.nodes[v].neighbours[u]  # Remove neighbouring ref v -> u

        # Remove the edge from the graph
        del self.edges[key]

    def iter_edges(self):
        return [(*k, v) for k, v in self.edges.items()]

    def neighbours(self, node_id):
        return self.nodes[node_id].neighbours
