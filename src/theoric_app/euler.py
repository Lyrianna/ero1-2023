import multi_graph


def is_eulerian(G):

    """
    :param G: MultiGraph
    :return: whether or not the graph is eulerian
    """
    # An undirected Eulerian graph has no vertices of odd degrees
    if any([node.degree % 2 != 0 for node in G.nodes.values()]):
        return False

    # Graph must be connected, not checking for now

    return True


def eulerian_circuit(G, source=None):

    """
    :param G: MultiGraph
    :param source: optional starting node
    :return: an eulerian circuit
    """

    if not is_eulerian(G):
        raise Exception('MultiGraph is not Eulerian!')

    # Make a copy of the graph
    g = multi_graph.MultiGraph(graph=G)

    # set starting node
    v = source if source is not None else next(iter(g.nodes))

    vertex_stack = [v]
    last_vertex = None
    while vertex_stack:
        current_vertex = vertex_stack[-1]
        current_node = g.nodes[current_vertex]
        if current_node.degree == 0:
            if last_vertex is not None:
                yield last_vertex, current_vertex
            last_vertex = current_vertex
            vertex_stack.pop()
        else:
            random_neighbour = next(iter(current_node.neighbours))
            vertex_stack.append(random_neighbour.node.id)
            g.remove_edge(current_node, random_neighbour.edge)
