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
from city_graph import CityGraph

from src.former_solutions.ant_optimisation import AntColony

output_dir = '../theoric_app/output_files'
ox.config(use_cache=True, log_console=True)


def main():
    # Load graph from osmnx
    city_name = sys.argv[1]
    print(city_name)
    osmnx_graph = ox.graph_from_place(city_name, network_type='drive')
    osmnx_graph = nx.convert_node_labels_to_integers(osmnx_graph)

    city_graph = CityGraph(osmnx_graph)

    ants = AntColony(city_graph, 1, 20, 1, 0.95, alpha=1.5, beta=0.5)
    path = ants.run()

    print(path)

    id_path = path.to_id_path()
    pair_id_path = path.to_pair_id_path()

    print(id_path)
    print(pair_id_path)

    # output_folder = f'{output_dir}/{city_name}-{calendar.timegm(time.gmtime())}'
    # os.mkdir(output_folder)
    #
    # for i in range(len(pair_id_path)):
    #     ec = ['r' if (u, v) in pair_id_path[:i] else 'w' for u, v, k in osmnx_graph.edges(keys=True)]
    #     print(ec)
    #     ox.plot_graph(osmnx_graph, node_color='w', node_edgecolor='k', node_size=10, node_zorder=3, edge_color=ec,
    #                   edge_linewidth=1, show=False, save=True,
    #                   filepath=f'{output_folder}/{i}.png')

    # nc = ['b' if node_id in id_path else 'w' for node_id in osmnx_graph.nodes()]
    ec = ['r' if (u, v) in pair_id_path else 'w' for u, v, k in osmnx_graph.edges(keys=True)]
    print(ec)
    # fig, ax = ox.plot_graph(osmnx_graph, node_color='w', node_edgecolor='k', node_size=10, node_zorder=3,
    # edge_color=ec, edge_linewidth=1, save=True, filepath=f'{output_dir}/output.png')
    fig, ax = ox.plot_graph_route(osmnx_graph, route=id_path, route_color='r', route_linewidth=3, orig_dest_size=30,
                                  node_size=2, save=True, filepath=f'{output_dir}/output.png')


if __name__ == '__main__':
    main()
