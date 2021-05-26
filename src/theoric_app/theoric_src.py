"""
Parsing du .dot et parcours du graph entier.

Problème numéro uno : Trouver une solution de parcours opti -> Cours de THEG incoming :ono:
|
-> Ant Optimisation
Problème numéro deuxio : Choisir ce qu'on préfère entre un parcours complet et un parcours rapide :oof:
"""
import sys

import networkx as nx
import osmnx as ox


def getDistanceMatrix(graph):
    D = nx.linalg.graphmatrix.adjacency_matrix(graph)

    print(D)

    return D


def main():
    # Load graph from dot file
    city_name = sys.argv[1]
    city = ox.graph_from_place(city_name, network_type='drive')

    D = getDistanceMatrix(city)


# ants = ao.AntColony(D, 40, 20, 40, 0.95)
# optimized_path = ants.run()

# nodes, edges = ox.gra(city)
# print(edges)


if __name__ == '__main__':
    main()
