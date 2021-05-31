import graphviz

class Edge:

    def __init__(self, u, v, weight):
        self.pair = (u, v) if u < v else (v, u)
        self.weight = weight

    def __str__(self):
        return f'w={self.weight:.3f}'


class Neighbour:

    def __init__(self, node, edge):
        self.node = node
        self.edge = edge

    def __str__(self):
        return f'(id:{self.node.id}, {self.edge})'


class Node:

    def __init__(self, node_id):
        self.id = node_id
        self.degree = 0
        self.neighbours = []

    def add_neighbour(self, neighbour_node, connecting_edge):
        self.degree += 1
        self.neighbours.append(Neighbour(neighbour_node, connecting_edge))

    def remove_neighbour(self, connecting_edge):
        self.degree -= 1
        neighbour = next((n for n in self.neighbours if n.edge == connecting_edge), None)
        self.neighbours.remove(neighbour)
        return neighbour

    def __str__(self):
        return f'id:{self.id} -> {[str(n) for n in self.neighbours]}'


class MultiGraph:

    """
    Undirected ! (u,v) == (v,u) !
    Args:
        edges: list of edge (u, v, w)
    """
    def __init__(self, graph=None, edges=None):
        self.degree = 0
        self.nodes = {}  # Dictionary indexed on (node_id)
        self.edges = []  # List of edges (u, v, w) (not unique!)
        if graph is not None:
            self.degree = graph.degree
            self.nodes = graph.nodes.copy()
            self.edges = graph.edges.copy()
        if edges is not None:
            for edge in edges:
                self.add_edge(*edge)

    def __str__(self):
        result = 'MultiGraph {\n'
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
        for edge in self.edges:
            dot.edge(str(edge.pair[0]), str(edge.pair[1]), label=str(edge.weight))
        dot.render(view=True, cleanup=True, filename=filename)
        return dot

    def add_node(self, node_id):
        if node_id not in self.nodes:
            new_node = Node(node_id)
            self.degree += 1
            self.nodes[node_id] = new_node
            return new_node
        return self.nodes[node_id]

    def add_edge(self, u, v, weight):  # Undirected for now

        # Create connecting edge
        edge = Edge(u, v, weight)

        # Get (or create if necessary) the two nodes
        start_node = self.add_node(u)
        end_node = self.add_node(v)

        # Link the two nodes
        start_node.add_neighbour(end_node, edge)
        end_node.add_neighbour(start_node, edge)

        self.edges.append(edge)

    def remove_edge(self, node, edge):

        # Remove linking edges
        neighbour = node.remove_neighbour(edge)
        neighbour.node.remove_neighbour(edge)

        # Remove global ref to edge
        self.edges.remove(edge)

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(*edge)
