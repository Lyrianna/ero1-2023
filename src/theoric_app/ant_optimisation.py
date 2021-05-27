import random
import sys

import numpy as np
from numpy.random import choice as np_choice


class AntColony(object):

    def __init__(self, adj_list, distances, pheromones, n_ants, n_best, n_iterations, decay, alpha=1, beta=1):
        """
        Args:
            distances (2D numpy.array): Square matrix of distances. Diagonal is assumed to be np.inf.
            n_ants (int): Number of ants running per iteration
            n_best (int): Number of best ants who deposit pheromone
            n_iteration (int): Number of iterations
            decay (float): Rate it which pheromone decays. The pheromone value is multiplied by decay, so 0.95 will lead to decay, 0.5 to much faster decay.
            alpha (int or float): exponenet on pheromone, higher alpha gives pheromone more weight. Default=1
            beta (int or float): exponent on distance, higher beta give distance more weight. Default=1
        Example:
            ant_colony = AntColony(german_distances, 100, 20, 2000, 0.95, alpha=1, beta=2)
        """
        self.adj_list = adj_list
        self.distances = distances
        self.pheromone = pheromones
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta

    def run(self):
        shortest_path = None
        all_time_shortest_path = ("placeholder", np.inf)
        for i in range(self.n_iterations):
            all_paths = self.gen_all_paths()
            self.spread_pheronome(all_paths, self.n_best, shortest_path=shortest_path)
            shortest_path = min(all_paths, key=lambda x: x[1])
            print(shortest_path)
            if shortest_path[1] < all_time_shortest_path[1]:# or all_time_shortest_path[1] == np.inf:
                all_time_shortest_path = shortest_path
            # self.pheromone = self.pheromone * self.decay
            for key in self.pheromone:
                self.pheromone[key] *= self.decay
        return all_time_shortest_path

    def spread_pheronome(self, all_paths, n_best, shortest_path):
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        for path, dist in sorted_paths[:n_best]:
            for move in path:
                start, end = move[0], move[1]
                end_index = self.adj_list[start].index(end)
                self.pheromone[start][end_index] += 1.0 / self.distances[start][end_index]

    def gen_path_dist(self, path):
        total_dist = 0
        for edge in path:
            start, end = edge[0], edge[1]
            total_dist += self.distances[start][self.adj_list[start].index(end)]

        return total_dist

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            start_node = next(iter(self.adj_list))
            path = self.gen_path(start_node)
            all_paths.append((path, self.gen_path_dist(path)))
        return all_paths

    def gen_path(self, start_node):
        path = []
        visited = set()
        visited.add(start_node)
        prev = start_node
        for _ in self.adj_list:
            move = self.pick_move(self.adj_list[prev], self.pheromone[prev], self.distances[prev], visited)
            # neighbours = self.adj_list[prev]
            # if not neighbours:
            #     break
            # move = neighbours[random.randint(0, len(neighbours) - 1)]
            # if move in visited:
            #     move = neighbours[random.randint(0, len(neighbours) - 1)]
            if not move:
                break
            path.append((prev, move))
            prev = move
            visited.add(move)
        return path

    # Pick best move from neighbours
    def pick_move(self, adj, pheromone, dist, visited):

        pheromone = np.copy(pheromone)
        for node in visited:
            try:
                i = adj.index(node)
                pheromone[i] = 0
            except ValueError:
                continue

        row = pheromone ** self.alpha * ((1.0 / dist) ** self.beta)
        s = row.sum()
        if s == 0:
            return None
        norm_row = row / s
        if np.isnan(norm_row).any():
            return None

        # Array de len -> self.all_inds <=> range(len(array))
        move = np_choice(range(len(dist)), 1, p=norm_row)[0]
        return adj[move]
