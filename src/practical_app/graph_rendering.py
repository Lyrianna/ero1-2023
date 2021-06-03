import os
import time
import imageio

import osmnx as ox


class EdgeInfo:

    def __init__(self, index, edge):
        self.index = index  # index in graph edge list
        self.edge = edge
        self.visited_times = 0
        self.color = 'w'

    def update_color(self):
        if self.visited_times <= 1:
            self.color = 'red'
        else:
            self.color = 'blue'

    def visit(self):
        self.visited_times += 1
        self.update_color()


def render_osmnx_path(graph, edge_path, duration_between_steps=0.5, step_size=1, edge_width=1.0):

    visit_times = {}
    for edge in edge_path:
        visit_times[edge] = 0

    edge_info_dict = {}
    for index, edge in enumerate(graph.edges):
        u, v, _ = edge
        edge = (u, v)
        if edge not in edge_info_dict:
            edge_info_dict[edge] = []
        edge_info_dict[edge].append(EdgeInfo(index, (u, v)))

    path_info = []
    for edge in edge_path:
        path_info.append(edge_info_dict[edge])

    edge_colors = ['w'] * len(graph.edges)  # List with the ith value representing the ith edge's color in graph.edges

    def update_edge_color(edge_info):
        edge_info.visit()
        edge_colors[edge_info.index] = edge_info.color

    def update_edge_colors(edges_to_visit):
        for edge in edges_to_visit:
            for ei in edge_info_dict[edge]:
                update_edge_color(ei)

    time_stamp = int(time.time())
    output_dir = f'render_files_{time_stamp}'
    os.makedirs(output_dir)

    files = []

    def render_path(filename):
        ox.plot_graph(graph, node_edgecolor='k', node_size=0, node_zorder=3,
                      edge_color=edge_colors, edge_linewidth=edge_width, edge_alpha=0.5,
                      show=False, close=True, save=True, filepath=filename)
        files.append(filename)

    # Render by big steps
    for i in range(len(edge_path) // step_size + 1):

        start_i, end_i = step_size * i, step_size * (i + 1)
        edges_to_visit = edge_path[start_i:end_i]

        update_edge_colors(edges_to_visit)

        render_path(f'{output_dir}/step_{i:05}.png')

    # Render final step
    render_path(f'{output_dir}/step_{len(edge_path)+1:05}.png')

    print(files)

    # Render final gif
    with imageio.get_writer(f'osmnx_render_{time_stamp}.gif', mode='I', duration=duration_between_steps) as writer:
        for file in files:
            image = imageio.imread(file)
            writer.append_data(image)

    print(output_dir)
