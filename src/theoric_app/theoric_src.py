"""
Parsing du .dot et parcours du graph entier.

Problème numéro uno : Trouver une solution de parcours opti -> Cours de THEG incoming :ono:
|
-> Ant Optimisation
Problème numéro deuxio : Choisir ce qu'on préfère entre un parcours complet et un parcours rapide :oof:
"""
import math
import sys

import networkx as nx
import ant_optimisation as ao
import osmnx as ox
import numpy as np

from ant_optimisation import AntColony
import ant_colony as ac


def getDistanceMatrix(graph):
    mat = nx.to_numpy_array(graph, weight='length')
    mat[mat == 0.] = sys.maxsize
    return mat


def get_adj_list(city_graph):
    # Initialize tmp adj_list with nodes
    tmp = {}
    for node in city_graph.nodes():
        tmp[node] = ([], [], [])

    # Populate
    for edge in city_graph.edges(data=True):
        start, end, data = edge[0], edge[1], edge[2]
        tmp[start][0].append(end)
        tmp[start][1].append(data['length'])
        tmp[start][2].append(1)
        if not data['oneway']:
            tmp[end][0].append(start)
            tmp[end][1].append(data['length'])
            tmp[end][2].append(1)

    # Remove dead ends
    # tmp = {key: _ for key, _ in tmp.items() if len(tmp[key][0]) != 0}

    adj_list = {}
    distances = {}
    pheromones = {}
    for key in tmp:
        adj_list[key] = tmp[key][0]
        distances[key] = np.array(tmp[key][1])
        pheromones[key] = np.array(tmp[key][2]) / len(tmp[key][2])

    return adj_list, distances, pheromones


def main():
    # Load graph from osmnx
    city_name = sys.argv[1]
    print(city_name)
    city = ox.graph_from_place(city_name, network_type='drive')

    adj_list, distances, pheromones = get_adj_list(city)
    # for key in adj_list:
    #     print(key, '=', adj_list[key], ',', distances[key], ',', pheromones[key])

    ants = AntColony(adj_list, distances, pheromones, 40, 20, 150, 0.95)
    optimized_path = ants.run()

    print("shorted_path: {}".format(optimized_path))

    ec = ['r' if (u, v) in optimized_path[0] else 'w' for u, v, k in city.edges(keys=True)]
    fig, ax = ox.plot_graph(city, node_color='w', node_edgecolor='k', node_size=30,
                            node_zorder=3, edge_color=ec, edge_linewidth=3)

    # distances = np.array([[np.inf, 2, 2, 5, 7],
    #                       [2, np.inf, 4, 8, 2],
    #                       [2, 4, np.inf, 1, 3],
    #                       [5, 8, 1, np.inf, 2],
    #                       [7, 2, 3, 2, np.inf]])
    #
    # ant_colony = ac.AntColony(distances, 1, 1, 100, 0.95, alpha=1, beta=1)
    # shortest_path = ant_colony.run()
    # print("shorted_path: {}".format(shortest_path))


if __name__ == '__main__':
    main()
