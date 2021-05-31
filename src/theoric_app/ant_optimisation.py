import random
import sys

import numpy as np
from numpy.random import choice as np_choice
from city_graph import *


class AntColony(object):

    def __init__(self, graph, n_ants, n_best, n_iterations, decay, alpha=1, beta=1):
        """
        Args:
            distances (2D numpy.array): Square matrix of distances. Diagonal is assumed to be np.inf.
            n_ants (int): Number of ants running per iteration
            n_best (int): Number of best path who deposit pheromone
            n_iteration (int): Number of iterations
            decay (float): Rate it which pheromone decays. The pheromone value is multiplied by decay, so 0.95 will lead to decay, 0.5 to much faster decay.
            alpha (int or float): exponenet on pheromone, higher alpha gives pheromone more weight. Default=1
            beta (int or float): exponent on distance, higher beta give distance more weight. Default=1
        Example:
            ant_colony = AntColony(german_distances, 100, 20, 2000, 0.95, alpha=1, beta=2)
        """
        self.graph = graph
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta

    def run(self):
        shortest_path = None
        all_time_shortest_path = Path()
        all_time_shortest_path.length = np.inf
        for i in range(self.n_iterations):
            all_paths = self.gen_all_paths()
            self.spread_pheronome(all_paths, self.n_best, shortest_path=shortest_path)
            shortest_path = min(all_paths, key=lambda p: p.length)
        """   if len(shortest_path.nodes) == 0:
               ratio_shortest = np.inf
           else:
               ratio_shortest = shortest_path.length / len(shortest_path.nodes)
           if all_time_shortest_path.length == np.inf:
               all_time_shortest_ratio = np.inf
           else:
               all_time_shortest_ratio = all_time_shortest_path.length / len(all_time_shortest_path.nodes)"""
        if shortest_path.length < all_time_shortest_path.length:  # ratio_shortest < all_time_shortest_ratio:
            all_time_shortest_path = shortest_path
            # self.pheromone = self.pheromone * self.decay
            # for key in self.pheromone:
            #     self.pheromone[key] *= self.decay
        for edge in self.graph.edges:
            edge.pheromone *= self.decay

        return all_time_shortest_path

    def spread_pheronome(self, all_paths, n_best, shortest_path):
        sorted_paths = sorted(all_paths, key=lambda p: p.length)
        for path in sorted_paths[:n_best]:
            for i in range(len(path.nodes) - 1):
                start_node = path.nodes[i]
                end_node = path.nodes[i + 1]
                edge = start_node.neighbours[end_node.id].edge
                edge.spread_pheromone()

    # def gen_path_dist(self, path):
    #     total_dist = 0
    #     for edge in path:
    #         start, end = edge[0], edge[1]
    #         total_dist += self.distances[start][self.adj_list[start].index(end)]
    #
    #     return total_dist

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            # _, start_node = next(iter(self.graph.nodes.items()))
            start_id = random.choice(list(self.graph.nodes.keys()))
            start_node = self.graph.nodes[start_id]
            path = self.gen_path(start_node)
            all_paths.append(path)
        return all_paths

    def gen_path(self, start_node):
        print(start_node)
        final_path = Path()
        visited_edges = set()
        prev = start_node
        # while len(visited_edges) != len(self.graph.edges):
        for _ in range(100):
            path = self.pick_next_path(prev, visited_edges)
            if path is None:
                break
            final_path.concat_with(path)
            take_path(path, visited_edges)
            prev = path.nodes[-1]
        # print(final_path)

        return final_path

    def pick_next_path(self, prev, visited_edges):
        """
        :param self:
        :param prev:
        :param visited_edges:
        :return: path given by np_choice

        Get all the neighbouring_unvisited_paths and take the most attractive
        """
        paths = get_neighbouring_unvisited_paths(prev, visited_edges)
        if len(paths) == 0:
            return None
        if len(paths) == 1:
            return paths[0]
        proba_incoming = np.array(
            [path.pheromone ** (self.alpha) * ((1.0 / path.length) ** self.beta) for path in paths])
        s = proba_incoming.sum()
        proba = proba_incoming / s
        # for i in range(len(proba)):
        #
        for i in range(len(paths)):
            print(f'{i}: p = {proba[i]} {paths[i]}')
        choice = np_choice(len(paths), 1, p=proba)[0]
        res_path = paths[choice]
        print(f"Result path: ({choice}) {res_path}")
        return res_path


def get_neighbouring_unvisited_paths(start_node, visited_edges, used_edge=None, path=None):
    if path is None:
        path = Path(start_node)
    else:
        path = path.copy()
        path.add_node(start_node, used_edge)

    # if used_edge in visited_edges:
    #     return []
    if used_edge is not None and used_edge not in visited_edges:  # Stop as soon as we've taken an unvisited edge
        return [path]

    paths = []
    for (n_id, neighbour) in start_node.neighbours.items():
        if neighbour.node not in path.nodes:  # Not sure about this
            extended_paths = get_neighbouring_unvisited_paths(neighbour.node, visited_edges, neighbour.edge, path)
            for p in extended_paths:
                paths.append(p)
    return paths


def take_path(path, visited_edges):
    for i in range(len(path.nodes) - 1):
        start_node = path.nodes[i]
        end_node = path.nodes[i + 1]
        edge = start_node.neighbours[end_node.id].edge
        visited_edges.add(edge)
