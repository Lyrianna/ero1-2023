import os
from collections import deque
import sys
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


def render_path_or_paths(graph, path=None, paths=None, duration_between_steps=0.5, step_size=1, edge_width=1.0):

    edge_info_dict = {}
    for index, edge in enumerate(graph.edges):
        u, v, _ = edge
        edge = (u, v)
        if edge not in edge_info_dict:
            edge_info_dict[edge] = deque()
        edge_info_dict[edge].append(EdgeInfo(index, (u, v)))

    path_info = []

    def init_path_info(path):
        for edge in path:
            path_info.append(edge_info_dict[edge])

    if path is not None:
        init_path_info(path)
    elif paths is not None:
        for p in paths:
            init_path_info(p)

    edge_colors = ['w'] * len(graph.edges)  # List with the ith value representing the ith edge's color in graph.edges

    def update_edge_color(edge_info):
        edge_info.visit()
        edge_colors[edge_info.index] = edge_info.color

    def update_edge_colors(edges_to_visit):
        for edge in edges_to_visit:
            ei_queue = edge_info_dict[edge]
            ei = ei_queue.pop()
            update_edge_color(ei)
            ei_queue.appendleft(ei)

    time_stamp = int(time.time())
    output_dir = f'render_files_{time_stamp}'
    os.makedirs(output_dir)

    files = []

    def render_path(filename):
        ox.plot_graph(graph, node_edgecolor='k', node_size=0, node_zorder=3,
                      edge_color=edge_colors, edge_linewidth=edge_width, edge_alpha=0.5,
                      show=False, close=True, save=True, filepath=filename)
        files.append(filename)

    def render_path_step(path, step_index):
        start_i, end_i = step_size * step_index, step_size * (step_index + 1)
        edges_to_visit = path[start_i:end_i]
        update_edge_colors(edges_to_visit)

    # Render empty step
    render_path(f'{output_dir}/_.png')

    # Render by big steps
    if path is not None:
        nb_steps = len(path) // step_size + 1
        for i in range(nb_steps):
            print(f'Rendering step {i}/{nb_steps}')
            render_path_step(path, i)
            render_path(f'{output_dir}/step_{i:05}.png')
    elif paths is not None:
        max_len = len(max(paths, key=len))
        nb_steps = max_len // step_size + 1
        for i in range(nb_steps):
            print(f'Rendering step {i}/{nb_steps}')
            for path in paths:
                render_path_step(path, i)
            render_path(f'{output_dir}/step_{i:05}.png')

    # Render final step
    render_path(f'{output_dir}/step_{9999}.png')

    print(files)
    render_filename = f'osmnx_render_{time_stamp}.gif'

    # Render final gif
    with imageio.get_writer(render_filename, mode='I', duration=duration_between_steps) as writer:
        for file in files:
            image = imageio.imread(file)
            writer.append_data(image)

    print(f'Path rendering available at src/{render_filename}')


def render_sub_graphs(og_graph, sub_graphs):

    node_colors_dict = dict.fromkeys(og_graph.nodes)
    edge_colors_dict = dict.fromkeys(og_graph.edges)

    colors = ['darkviolet', 'blue', 'deeppink', 'lime', 'indigo', 'deepskyblue', 'green',
              'maroon', 'teal', 'yellow', 'fuchsia', 'gold', 'orange', 'aqua', 'red', 'mint']

    for i, g in enumerate(sub_graphs):
        color = colors[i % len(colors)]
        for node in g.nodes:
            node_colors_dict[node] = color
        for edge in g.edges:
            edge_colors_dict[edge] = color

    node_colors = [node_colors_dict.get(node, 0) for node in og_graph.nodes]
    edge_colors = [edge_colors_dict.get(edge, 0) for edge in og_graph.edges]

    edge_colors = [c if c is not None else 'white' for c in edge_colors]

    ox.plot_graph(og_graph,
                  node_size=0, node_zorder=2, node_color=node_colors,
                  edge_linewidth=0.1, edge_color=edge_colors,
                  show=False, close=True, save=True, filepath='zones.png')

    print('Zone rendering available at "src/zones.png"')
